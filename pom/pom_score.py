"""
Score Pom episodes from raw platform metrics (see ALGORITHM.md §5).

    python3 pom_score.py performance.json            # prints a ranked table (markdown)
    python3 pom_score.py performance.json --tags     # also averages score by meta tag

performance.json = list of episodes:
[{"id": "ep002_60_days_left", "published": "2026-11-02T19:00", "duration": 20.7,
  "meta": {"topic": "habits", "format": "split", ...},
  "instagram": {"reach": .., "views": .., "likes": .., "comments": .., "shares": .., "saved": ..,
                "retention": .., "reelsViewRate": ..},
  "tiktok":    {"views": .., "likes": .., "comments": .., "shares": .., "fullVideoWatchedRate": ..,
                "avgTimeWatched": ..},
  "youtube":   {"views": .., "likes": .., "comments": .., "shares": .., "averageViewDuration": ..}}]
Missing platforms / metrics are skipped. Percentages may be 0-1 or 0-100 (normalised automatically).
"""
import json, sys, statistics
from collections import defaultdict

CAP = 3.0

def pct(v):
    if v is None: return None
    v = float(v)
    return v / 100 if v > 1.0 else v

def ratio(a, b):
    try:
        a, b = float(a), float(b)
        return a / b if b > 0 else None
    except (TypeError, ValueError):
        return None

def features(ep):
    d = ep.get('duration') or 20
    out = {}
    ig = ep.get('instagram') or {}
    if ig:
        reach = ig.get('reach') or ig.get('views')
        out['instagram'] = {
            'retention': (pct(ig.get('retention')), 0.30),
            'shares_reach': (ratio(ig.get('shares'), reach), 0.25),
            'saves_reach': (ratio(ig.get('saved'), reach), 0.10),
            'likes_reach': (ratio(ig.get('likes'), reach), 0.15),
            'comments_reach': (ratio(ig.get('comments'), reach), 0.10),
            'view_rate': (pct(ig.get('reelsViewRate')), 0.10),
        }
    tk = ep.get('tiktok') or {}
    if tk:
        v = tk.get('views')
        out['tiktok'] = {
            'full_watch': (pct(tk.get('fullVideoWatchedRate')), 0.30),
            'avg_watch_ratio': (ratio(tk.get('avgTimeWatched'), d), 0.20),
            'shares_views': (ratio(tk.get('shares'), v), 0.20),
            'comments_views': (ratio(tk.get('comments'), v), 0.15),
            'likes_views': (ratio(tk.get('likes'), v), 0.15),
        }
    yt = ep.get('youtube') or {}
    if yt:
        v = yt.get('views')
        out['youtube'] = {
            'avd_ratio': (ratio(yt.get('averageViewDuration'), d), 0.40),
            'likes_views': (ratio(yt.get('likes'), v), 0.20),
            'comments_views': (ratio(yt.get('comments'), v), 0.15),
            'shares_views': (ratio(yt.get('shares'), v), 0.15),
            'views': (float(v) if v not in (None, '') else None, 0.10),
        }
    return out

def score(episodes):
    feats = {e['id']: features(e) for e in episodes}
    med = defaultdict(list)
    for f in feats.values():
        for plat, ms in f.items():
            for k, (val, _) in ms.items():
                if val is not None: med[(plat, k)].append(val)
    med = {k: statistics.median(v) for k, v in med.items() if v}
    rows = []
    for e in episodes:
        plat_scores = {}
        for plat, ms in feats[e['id']].items():
            num = den = 0.0
            for k, (val, w) in ms.items():
                m = med.get((plat, k))
                if val is None or not m: continue
                num += w * min(CAP, val / m); den += w
            if den > 0: plat_scores[plat] = num / den
        total = sum(plat_scores.values()) / len(plat_scores) if plat_scores else None
        rows.append({'id': e['id'], 'score': total, **{p: plat_scores.get(p) for p in ('instagram', 'tiktok', 'youtube')},
                     'meta': e.get('meta', {})})
    rows.sort(key=lambda r: (r['score'] is None, -(r['score'] or 0)))
    return rows

def fmt(x): return '–' if x is None else f'{x:.2f}'

def main():
    eps = [e for e in json.load(open(sys.argv[1])) if not e.get('removed')]   # deleted posts don't count
    rows = score(eps)
    print('| Episode | Score | Instagram | TikTok | YouTube |\n|---|---|---|---|---|')
    for r in rows:
        print(f"| {r['id']} | {fmt(r['score'])} | {fmt(r['instagram'])} | {fmt(r['tiktok'])} | {fmt(r['youtube'])} |")
    if '--tags' in sys.argv:
        agg = defaultdict(list)
        for r in rows:
            if r['score'] is None: continue
            for k, v in (r['meta'] or {}).items():
                agg[(k, v)].append(r['score'])
        print('\n| Tag | Value | Episodes | Avg score |\n|---|---|---|---|')
        for (k, v), s in sorted(agg.items(), key=lambda kv: -statistics.mean(kv[1])):
            print(f'| {k} | {v} | {len(s)} | {statistics.mean(s):.2f} |')

if __name__ == '__main__':
    main()
