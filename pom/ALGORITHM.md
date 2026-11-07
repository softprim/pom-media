# Pom — growth playbook (content + publishing algorithm)

Read this before writing any episode. The weekly analytics review updates the **"What works for Pom"** and **"Experiments"** sections; the rest changes only when platforms change.
_Last updated: 2026-11-07 (first weekly review: 5 posts with data, 2 scoreable ≥ 72 h; E1 concluded; slots unchanged; TikTok shows 0 views)_

## 1. What the platforms reward (sources at the bottom)
| | Strongest signals | What it means for Pom |
|---|---|---|
| **YouTube Shorts** | Whether viewers *choose to view* vs swipe away, average view duration and **average % viewed**, likes, satisfaction. Only "engaged views" (watched past the first seconds) count for monetization. | First 1–2 s decide everything. Short and complete > long. End on the payoff. |
| **Instagram Reels** | **Watch time**, **likes per reach**, **sends per reach** (DM shares). Sends weigh most for reaching non-followers; likes weigh more for followers. Original content only (reposts get no recommendations). | Make it *sendable*: relatable situation + "send this to…" CTA. Trial Reels show a reel to non-followers first — use them for A/B tests. |
| **TikTok** | Predicted likes, shares, comments, follows, profile visits, **finishing vs skipping**, watch time, sound taps, "not interested". Also post time, region, language, sound, length, hashtags. | Completion + comments. Ask a question people want to answer. English captions, US-friendly posting time. |
| **All (recommender design)** | Systems like ByteDance's Monolith (open-sourced on GitHub) train **online/in real time** from fresh interactions. | The first hours after posting shape distribution → post when the audience is awake; reply to early comments. |

## 2. Episode recipe (default rules)
1. **Hook in frame 1** (no fade-in, no logo). Text readable in < 1.5 s: a number, a date, a "POV", or a relatable pain. Pom must be visible in the first frame. **Pom data (§6): the opener must describe the viewer's own moment right now ("It's dark at 5 PM", "Same day. Different date") — not an offer/deal or an off-niche fact. Don't add a second instruction line ("Pick A or B") in the first 2 s.**
2. **One idea, one turn.** Structure: hook → problem / A vs B → consequence / time skip → *the line that lands* (stop) → answer + CTA.
3. **Length 15–25 s.** Under 20 s when the idea is simple. Every scene must earn its seconds; cut anything that repeats.
4. **Loop the ending.** Last frame should connect to the first (same pose / same question) so replays feel natural. No lingering after the payoff; CTA ≤ 2 s on screen.
5. **Make it sendable.** The situation must be about *someone you know* ("the friend who always says from Monday"). Instagram caption ends with "📩 Send this to…".
6. **Comment bait that's easy to answer:** one word or A/B ("Comment DAY 1", "A or B?"). Put it at the END only (on-screen + caption). So far every post has 0 Instagram comments → Paul replying/pinning a first comment matters more than the wording.
7. **On-screen text ≤ ~30 chars per line, max 2 lines at once**, key line in orange.
8. **Consistent character = brand.** Always Pom (orange beanie + scarf). Grey = problem, warm = change.
9. **Captions per platform** (see README): YouTube searchable title (keyword first, ≤ 70 chars ideally), TikTok short question + 3–5 hashtags, Instagram longer + send/save CTA.
10. **Audio quality gate:** every render must be click-free (the 2026-11-03 fix in `pom_audio.py` fades every note's tail; never remove it). A bad-sounding video is worse than no video.

## 3. Publishing algorithm
- **Cadence:** one main video per day (episodes Sun/Mon/Wed/Fri, stories Tue/Thu/Sat), max 1 main video/day, same slots every time — consistency beats perfect timing. Plus TikTok-only "Pom quick" (see README budget).
- **Slots (Europe/Bucharest) — from Metricool `getBestTimeToPostByNetwork`, re-checked 2026-11-07 for Nov 8–14 (same peaks, no change):** the same video goes out per network at
  - **YouTube: 16:00** (peak every day of the week, 15–17 strong)
  - **TikTok: 18:00** (evening peak every day; 10:00 is the other peak)
  - **Instagram: 18:00** (second peak after 10:00; 18:00 also reaches the UK evening / US midday for an English audience)
  - **TikTok-only "Pom quick": 10:00** the day after a main episode (TikTok's morning peak).
  A day is "taken" when it already has a main post (YouTube 16:00 / TikTok 18:00 / Instagram 18:00). Re-check best times monthly; once Pom has ≥ 2 weeks of its own data (earliest review: 2026-11-16), the weekly review may move a slot (within ±2 h, between 17:00 and 23:00 for IG/TikTok) and records it in "Experiments".
- **Order of priority when choosing a topic** (the episode task follows this):
  1. Dated/seasonal idea whose date is within 10 days.
  2. A topic/format from "What works for Pom" with the highest score.
  3. A competitor topic that over-performed in the last 30 days (Metricool competitors), done Pom's way.
  4. Fresh idea from this week's trends.
  Keep a 70/20/10 mix: 70% proven formats, 20% variations, 10% wild experiments.
- **Never repeat** a topic already in `episodes/`. A *format* can repeat; a topic cannot (sequels are fine if labelled "Part 2" and the first part scored top-25%).
- **First hour:** the delivery message reminds Paul to reply to the first comments (Metricool Inbox shows comments from all three networks in one place).

## 4. Episode tags (put in every spec as `"meta"`)
```json
"meta": {"topic": "money|habits|time|career|relationships|mindset|business",
         "format": "split|montage|counter|story|list|quick",
         "hook": "number|date|pov|question|pain|contrarian",
         "cta": "comment_word|ab_choice|send_to|save",
         "season": "none|<event name>",
         "experiment": "<id from Experiments, or none>"}
```
The weekly review scores episodes and compares tags to learn what works.

## 5. Scoring (per episode, computed by `pom_score.py`)
Each metric is divided by Pom's **median** for that metric (so 1.0 = typical, 2.0 = twice as good), capped at 3, then weighted:
- **Instagram:** retention (avg % viewed) 0.30 · shares/reach 0.25 · saves/reach 0.10 · likes/reach 0.15 · comments/reach 0.10 · reel view rate (3 s) 0.10
- **TikTok:** full-video-watched rate 0.30 · avg watch time / duration 0.20 · shares/views 0.20 · comments/views 0.15 · likes/views 0.15
- **YouTube:** avg view duration / duration 0.40 · likes/views 0.20 · comments/views 0.15 · shares/views 0.15 · views 0.10
**Episode score** = average of the platform scores available. Only score episodes ≥ 72 h old. With < 5 scored episodes, treat results as hints, not rules. Entries with `"removed"` are skipped.
Note (2026-11-07): Metricool returns `null` for Instagram retention (IGRE27), so `performance.json` stores `retention` = avg watch time (IGRE24) / duration, marked `retention_source`. TikTok watch metrics are empty while views are 0.

## 6. What works for Pom (updated by the weekly review)
_Review 2026-11-07. Only **2 episodes ≥ 72 h** (ep001, ep003) → scores are hints, not rules. Early (< 72 h) Instagram numbers for ep004, story001, ep005 are used as directional evidence._

| Episode | IG views | IG 3-s hold | IG % watched | IG likes/reach | YT views · AVD | Score (≥72 h / early) |
|---|---|---|---|---|---|---|
| ep001 the loop (habits, montage, pain) | 2,064 | 61% | 57% | 4.5% | 1,169 · 8 s | 0.99 / 1.20 |
| ep003 dark at 5 PM (habits, split, pain, winter) | 892 | 58% | 38% | 4.1% | 1,149 · 8 s | 1.02 / 1.30 |
| ep005 winter arc Monday (habits, split, E1) | 1,187 (< 1 day) | 50% | 32% | 0.7% | not synced yet | – / 0.96 |
| story001 Voyager (science story, 52 s) | 129 | 32% | 13% | 0.9% | not synced yet | – / 0.71 |
| ep004 Black Friday (money, split, E1) | 139 | 31% | 29% | 0.8% | not synced yet | – / 0.52 |

1. **The first 3 seconds decide Instagram distribution.** The 3-s hold rate splits the posts cleanly: 50–61% → 892–2,064 views; 31–32% → 129–139 views (10× less). Same account, same slot, same week — so it's the opener, not the time.
2. **Relatable "your moment right now" habit hooks win** (ep001 "Same day. Different date", ep003 "It's dark at 5 PM", ep005 "Starting Monday") — avg early score 1.15 vs 0.52 for money (ep004) and 0.71 for the science story. Winter / winter-arc framing works (#winterarc posts: 892 and 1,187 views).
3. **"Everything 50% off" reads like an ad** → 31% hold. Money topics are not dead yet (n = 1, E3 still running with ep007), but money hooks must open on the viewer's pain, not on a deal.
4. **Long true stories on Pom underperform** (story001: 13% watched of 52 s, 129 views). One data point; story002 (Roanoke, 59 s) goes out tonight — if it also scores < 0.7, move true/unsolved stories off Pom (they fit the "Mystery Frames" channel).
5. **Shortest = best watched:** ep001 (17 s) 57% watched vs 29–38% for 18.8–21.9 s episodes. Supports E2 (< 20 s), not yet tested cleanly.
6. **Engagement is the weak spot everywhere:** 0 Instagram comments on all 5 posts; ≤ 2 shares per post. YouTube views are steady (~1,150 per Short, AVD 8 s ≈ 37–47%) regardless of time posted (ep001 03:00, ep003 16:00).
7. **TikTok: 0 views on every post** (Metricool, Nov 2–6; ep001 has 1). That is not a content signal — it looks like a visibility/account problem (private, under review, or not synced). TikTok data can't be used until fixed.
- ep002 "60 days left" was deleted by Paul (audio bug + weak video) — not data.

## 7. Experiments (one variable at a time)
| id | Hypothesis | How | Status |
|---|---|---|---|
| E1 | Explicit "Pick A or B" in the first 2 s raises comments & completion | ep004 + ep005 opened with "Pick A or B." | **concluded 2026-11-07 — not supported.** 0 IG comments on both (same as non-E1 posts); IG 3-s hold 31% / 50% vs 61% / 58% for ep001/ep003 without it. Drop the extra opener line; keep "A or B?" only at the end. (Weak evidence, n = 2, topic confounded.) |
| E2 | Under-20 s episodes get higher % viewed than 20–25 s | Alternate lengths for 4 episodes, same format | planned — hint in favour: ep001 17 s → 57% watched |
| E3 | Money topics outperform habit topics | Alternate topic for 4 episodes | **running** — so far money 0.52 (ep004) vs habits 1.15 avg (early). Remaining: ep007 money (Nov 8), ep008 habits (Nov 9). Conclude at the 2026-11-14 review. |
| E4 | Instagram Trial Reel with an alternative hook finds a better opener | Post the same episode with a different first scene as `TRIAL_REEL` 1 day later | **next** — start with the first episode after ep008. Metric: IG 3-s hold rate (the variable that decided reach this week). Variant hook = "you/your moment right now" line, Pom in action, no second line. |
| E_quick | 8–14 s TikTok-only "Pom quick" clips add views/follows without hurting main episodes | 2/week at 10:00, compare TikTok views & follows per post vs main episodes | running from 2026-11-04 — **blocked**: TikTok shows 0 views for all posts, can't evaluate until fixed |
| E_slots | Per-network slots (YT 16:00, TT/IG 18:00) beat a single 19:00 slot | From 2026-11-03; compare first-24 h views once ≥ 2 weeks of data | running — best-time data (2026-11-07) unchanged; review 2026-11-16 |

## 8. When content should change (decision rules for the review)
- A format scores < 0.7 three times in a row → pause it.
- A topic/format scores > 1.5 twice → make it a series ("Pom vs Money, ep. N").
- Retention low but shares high → the idea is good, the pacing is slow → cut the middle.
- Retention high but shares/comments low → stronger CTA / more relatable framing.
- YouTube views low but IG/TikTok fine → the first frame/title is the problem (YouTube is the most search/title sensitive).
- **IG 3-s hold < 40% → the opener failed** (2026-11-07: it cut views ~10×). Rewrite the first scene for that topic before reusing it; test alternatives with E4 Trial Reels.

## Sources
- TikTok official: [Introduction to the TikTok recommendation system](https://www.tiktok.com/transparency/en/recommendation-system)
- Instagram (Mosseri's guidance, summarized): [Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance), [Buffer](https://buffer.com/resources/instagram-algorithms/)
- YouTube Shorts metrics (citing YouTube Help): [Shortimize – Shorts retention](https://www.shortimize.com/blog/youtube-shorts-retention-rate)
- Recommender design (Monolith, ByteDance, open-source): [MLOps newsletter](https://mlops.substack.com/p/tiktoks-recommendation-engine-explained)
- Hook types by content type: [Bytecap research](https://www.bytecap.io/research/best-hooks-for-youtube-shorts)
- Posting frequency: [Buffer – how often to post](https://buffer.com/library/how-often-post-social-media)
- Best times: Metricool `getBestTimeToPostByNetwork` (brand pomschoices, weeks of 2026-11-03 and 2026-11-08)
- Pom performance: Metricool analytics (brand pomschoices), pulled 2026-11-07 → `analytics/performance.json`
