"""
Illustrated story film: full-screen hand-drawn frames (generated in Figma) + narration + captions + music.
Each segment shows one illustrated frame with a slow camera move; frames cross-fade like cuts in an animated film.

    python3 pom_film.py films/<id>.json out/                 # full render
    python3 pom_film.py films/<id>.json out/ still 3 12 25   # stills

Reuses the voice / music / caption helpers of pom_story.py (TTS_DIR must point to the Kokoro model).
"""
import cairo, math, os, sys, json, subprocess, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pom_story as ps
from pom_story import W, H, FPS, clamp, ease, eout, eob, text, font, rrect, stamp, GOLD, CYAN, WHITE, DIM, RED, hexc

XFADE = 0.45           # cross-fade between frames (s)
OVERSCAN = 1.16        # image is drawn bigger than the screen so the camera can move

_img = {}
def frame_surface(path):
    if path not in _img:
        from PIL import Image, ImageFilter
        im = Image.open(path).convert('RGB')
        tw, th = int(W * OVERSCAN), int(H * OVERSCAN)
        sc = max(tw / im.size[0], th / im.size[1])
        im = im.resize((int(im.size[0] * sc + .5), int(im.size[1] * sc + .5)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
        arr = np.array(im); h, w, _ = arr.shape
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
        buf = np.zeros((h, stride // 4, 4), np.uint8)
        buf[:, :w, 0] = arr[..., 2]; buf[:, :w, 1] = arr[..., 1]; buf[:, :w, 2] = arr[..., 0]; buf[:, :w, 3] = 255
        _img[path] = (cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, stride), w, h, buf)
    return _img[path]

_clips = {}
def clip_frames(path):
    """decodes an animated clip (e.g. a Higgsfield image-to-video of the frame) into cairo surfaces; keeps the 2 most recent clips in memory"""
    if path not in _clips:
        while len(_clips) >= 2: _clips.pop(next(iter(_clips)))
        pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                             '-of', 'csv=p=0', path], capture_output=True, text=True, check=True).stdout.strip().split(',')
        w, h = int(pr[0]), int(pr[1]); a, b = pr[2].split('/'); fps = float(a) / float(b)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'bgra', '-'], capture_output=True, check=True).stdout
        n = len(raw) // (w * h * 4); stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
        arr = np.frombuffer(raw, np.uint8)[:n * w * h * 4].reshape(n, h, w, 4)
        frames = []
        for i in range(n):
            buf = np.zeros((h, stride // 4, 4), np.uint8); buf[:, :w] = arr[i]
            frames.append((cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, stride), buf))
        _clips[path] = (frames, w, h, n / fps)
    return _clips[path]

MAX_SLOW = 2.0         # a clip is slowed down at most this much to fill its segment; after that the last frame is held (the camera keeps moving)

def cam(move, k):
    """camera for progress k (0..1): returns (zoom, dx, dy) where dx,dy are fractions of the free margin (-1..1)"""
    k = ease(k)
    return {
        'zoom_in':   (1.0 + .12 * k, 0, 0),
        'zoom_out':  (1.12 - .12 * k, 0, 0),
        'pan_left':  (1.04, .8 - 1.6 * k, 0),
        'pan_right': (1.04, -.8 + 1.6 * k, 0),
        'pan_up':    (1.04, 0, .8 - 1.6 * k),
        'pan_down':  (1.04, 0, -.8 + 1.6 * k),
        'push_face': (1.0 + .2 * k, 0, -.3 * k),
        'still':     (1.0 + .03 * k, 0, 0),
    }.get(move, (1.0 + .08 * k, 0, 0))

def draw_frame(ctx, seg, k, alpha=1.0, focus=None):
    """draws the segment's illustration; returns the transform (to place overlays in image coords)"""
    surf2 = None
    if seg.get('_clip'):
        frames, iw, ih, cd = clip_frames(seg['_clip'])
        el = k * seg.get('_span', cd)                                   # seconds since this frame came on screen
        pos = min(len(frames) - 1, el / max(cd, min(seg.get('_span', cd), cd * MAX_SLOW)) * (len(frames) - 1))
        i0 = int(pos); surf = frames[i0][0]
        if pos - i0 > 0.02 and i0 + 1 < len(frames): surf2 = (frames[i0 + 1][0], pos - i0)   # blend neighbours: smooth slow motion
    else:
        surf, iw, ih, _ = frame_surface(seg['_path'])
    z, dx, dy = cam(seg.get('move', 'zoom_in'), k)
    if focus: dx, dy = focus
    s = max(W / iw, H / ih) * z
    mx, my = (iw * s - W) / 2, (ih * s - H) / 2
    ox, oy = -mx + dx * mx, -my + dy * my
    ctx.save(); ctx.translate(ox, oy); ctx.scale(s, s); ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(alpha)
    if surf2:
        ctx.set_source_surface(surf2[0], 0, 0); ctx.get_source().set_filter(cairo.FILTER_GOOD); ctx.paint_with_alpha(alpha * surf2[1])
    ctx.restore()
    return ox, oy, s, iw, ih

_amb = {}
def ambient(ctx, kind, T):
    """free 'living picture' layer over a frame: fog | rain | snow | dust | embers | flicker (list or one name).
    Use it on every still frame that has no animated clip, so no shot is ever a frozen picture."""
    for kd in ([kind] if isinstance(kind, str) else (kind or [])):
        if kd not in _amb:
            r = random.Random(hash(kd) % 1000)
            _amb[kd] = [(r.random(), r.random(), r.random(), r.random()) for _ in range(140)]
        P = _amb[kd]
        if kd == 'fog':
            for i, (a, b, c, d) in enumerate(P[:9]):
                x = ((a + T * (.012 + .02 * c) * (1 if i % 2 else -1)) % 1.4 - .2) * W; y = (.35 + .6 * b) * H
                rx, ry = 520 + 380 * c, 120 + 110 * d
                ctx.save(); ctx.translate(x, y); ctx.scale(rx, ry)
                g = cairo.RadialGradient(0, 0, 0, 0, 0, 1); g.add_color_stop_rgba(0, .85, .9, .95, .13 + .05 * math.sin(T * .5 + i)); g.add_color_stop_rgba(1, .85, .9, .95, 0)
                ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.set_source(g); ctx.fill(); ctx.restore()
        elif kd == 'rain':
            ctx.set_line_width(2.5); ctx.set_line_cap(1)
            for a, b, c, d in P:
                sp = 1.6 + 1.2 * c; y = ((b + T * sp) % 1.1 - .05) * H; x = (a * 1.2 - .1) * W - (y / H) * 120
                ctx.move_to(x, y); ctx.line_to(x - 9, y + 42 + 30 * c); ctx.set_source_rgba(.8, .88, 1, .16 + .2 * d); ctx.stroke()
        elif kd in ('snow', 'dust'):
            for a, b, c, d in P[:110 if kd == 'snow' else 60]:
                sp = (.05 + .07 * c) if kd == 'snow' else (.008 + .01 * c)
                y = ((b + T * sp) % 1.05) * H; x = (a + .03 * math.sin(T * (.6 + c) + d * 6)) * W
                ctx.arc(x, y, (2.5 + 4 * d) if kd == 'snow' else (1.5 + 2.5 * d), 0, 2 * math.pi)
                ctx.set_source_rgba(1, 1, 1 if kd == 'snow' else .85, (.55 if kd == 'snow' else .22) * (.5 + .5 * math.sin(T * 2 + d * 9) ** 2)); ctx.fill()
        elif kd == 'embers':
            for a, b, c, d in P[:45]:
                k = (b + T * (.05 + .08 * c)) % 1; y = (1 - k) * H; x = (a + .05 * math.sin(T * (1 + c) + d * 6)) * W
                ctx.arc(x, y, 2 + 3.5 * d, 0, 2 * math.pi); ctx.set_source_rgba(1, .55 + .3 * d, .15, .75 * math.sin(k * math.pi)); ctx.fill()
        elif kd == 'flicker':
            a = .05 + .04 * math.sin(T * 9.1) * math.sin(T * 3.7) + .02 * math.sin(T * 23)
            ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(1, .7, .3, max(0, a)); ctx.fill()

def vignette(ctx):
    g = cairo.RadialGradient(W / 2, H / 2, H * .25, W / 2, H / 2, H * .75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .55)
    ctx.rectangle(0, 0, W, H); ctx.set_source(g); ctx.fill()
    g = cairo.LinearGradient(0, H * .62, 0, H)                    # darker bottom for captions
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .6)
    ctx.rectangle(0, H * .62, W, H * .38); ctx.set_source(g); ctx.fill()

_grain = []
def grain(ctx, T):
    if not _grain:
        rng = np.random.default_rng(3)
        for _ in range(4):
            n = (rng.random((H // 3, W // 3)) * 255).astype(np.uint8)
            stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_A8, W // 3)
            buf = np.zeros((H // 3, stride), np.uint8); buf[:, :W // 3] = n
            _grain.append((cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_A8, W // 3, H // 3, stride), buf))
    s, _ = _grain[int(T * 12) % 4]
    ctx.save(); ctx.scale(3, 3); ctx.set_source_rgba(1, 1, 1, .035); ctx.mask_surface(s, 0, 0); ctx.restore()

SAFE_TOP, SAFE_BOTTOM, SAFE_W = 290, 1420, 760   # platform UI safe zone (status bar / Dynamic Island, right-side buttons, bottom caption bar)

def captions(ctx, words, T, y=1330):
    cur = [w for w in words if w['s'] <= T + 0.05]
    if not cur: return
    last = cur[-1]
    if T > last['e'] + 0.6: return
    seg = [w for w in words if w['seg'] == last['seg']]
    chunks, c = [], []
    for w in seg:
        c.append(w)
        if len(c) >= 4 or w['txt'].endswith((',', '.', '?', '...', '!')): chunks.append(c); c = []
    if c: chunks.append(c)
    chunk = next((c for c in chunks if c[0]['s'] <= T + .05 and T <= c[-1]['e'] + .25), None) or chunks[-1]
    size = 70; font(ctx, size)
    sp = ctx.text_extents('a a').x_advance - ctx.text_extents('aa').x_advance
    widths = [ctx.text_extents(w['txt']).x_advance for w in chunk]; total = sum(widths) + sp * (len(chunk) - 1)
    if total > SAFE_W:
        size = int(size * SAFE_W / total); font(ctx, size); sp = ctx.text_extents('a a').x_advance - ctx.text_extents('aa').x_advance
        widths = [ctx.text_extents(w['txt']).x_advance for w in chunk]; total = sum(widths) + sp * (len(chunk) - 1)
    x = W / 2 - total / 2
    for w, wd in zip(chunk, widths):
        active = w['s'] <= T <= w['e'] + .05
        font(ctx, size)
        ctx.move_to(x, y); ctx.text_path(w['txt']); ctx.set_source_rgba(0, 0, 0, .85); ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
        ctx.move_to(x, y); ctx.set_source_rgba(*(GOLD if active else WHITE), 1); ctx.show_text(w['txt'])
        x += wd + sp

# ---------------------------------------------------------------- overlays
def ov_hook(ctx, hook, T):
    """Hook title shown from the very first frame (0 s) for `hook.until` seconds: 1–2 short lines, huge, inside the safe zone.
    This is what decides 'viewed vs swiped away' on Shorts, so it must be readable in < 1 s."""
    if not hook: return
    until = hook.get('until', 2.6)
    if T > until + .3: return
    a = 1.0 if T < until else 1 - (T - until) / .3
    lines = hook['lines'][:2]
    y = hook.get('y', 520)
    band_h = 150 * len(lines) + 60
    ctx.rectangle(0, y - 120, W, band_h); ctx.set_source_rgba(0, 0, 0, .55 * a); ctx.fill()
    for i, ln in enumerate(lines):
        size = 110 if i == 0 else 92
        font(ctx, size); e = ctx.text_extents(ln)
        if e.x_advance > SAFE_W: size *= SAFE_W / e.x_advance; font(ctx, size); e = ctx.text_extents(ln)
        yy = y + i * 150
        ctx.move_to(W / 2 - e.x_advance / 2, yy); ctx.text_path(ln); ctx.set_source_rgba(0, 0, 0, a); ctx.set_line_width(12); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
        ctx.move_to(W / 2 - e.x_advance / 2, yy); ctx.set_source_rgba(*(GOLD if i == len(lines) - 1 else WHITE), a); ctx.show_text(ln)

def ov_stamp(ctx, seg, t):
    if seg.get('stamp'): stamp(ctx, seg['stamp'], W / 2, min(seg.get('stamp_y', 1190), 1200), eob(clamp((t - .25) / .35)), size=46)

def ov_stat(ctx, seg, t, d):
    st = seg.get('stat')
    if not st: return
    a = eout(clamp((t - .2) / .4))
    k = eout(clamp((t - .4) / max(.6, d * .5)))
    v = st.get('from', 0) + (st['to'] - st.get('from', 0)) * k
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, .35 * a); ctx.fill()
    big = f"{v:,.0f}{st.get('suffix', '')}"
    fin = f"{st['to']:,.0f}{st.get('suffix', '')}"; sz = 230; font(ctx, sz); ew = ctx.text_extents(fin).x_advance
    if ew > SAFE_W: sz = 230 * SAFE_W / ew                              # long numbers: shrink outline and fill together (stay inside the safe zone)
    font(ctx, sz); e = ctx.text_extents(big)
    ctx.move_to(W / 2 - e.x_advance / 2, 900); ctx.text_path(big); ctx.set_source_rgba(0, 0, 0, .8 * a); ctx.set_line_width(16); ctx.stroke()
    text(ctx, big, W / 2, 900, sz, GOLD, a)
    if st.get('label'): text(ctx, st['label'], W / 2, 1010, 60, WHITE, a * clamp((t - .9) / .4))

def ov_carve(ctx, seg, t, d, tr):
    cv = seg.get('carve')
    if not cv: return
    ox, oy, s, iw, ih = tr
    (x0, y0, x1, y1) = cv['box']                               # box on the illustration, 0..1
    cx, cy = ox + (x0 + x1) / 2 * iw * s, oy + (y0 + y1) / 2 * ih * s
    bw, bh = (x1 - x0) * iw * s, (y1 - y0) * ih * s
    word = cv['word']; vertical = bh > bw
    k = clamp((t - cv.get('at', .4)) / max(.9, d * .5)); n = int(len(word) * k + .999) if k > 0 else 0
    ctx.save(); ctx.translate(cx, cy)
    if vertical: ctx.rotate(-math.pi / 2); bw, bh = bh, bw
    def cf(sz): ctx.select_font_face('FreeSerif', 0, 1); ctx.set_font_size(sz)
    size = 200; cf(size); e = ctx.text_extents(word)
    size *= min(bw * .86 / e.x_advance, bh * .62 / (e.height or 1)); cf(size); e = ctx.text_extents(word)
    x = -e.x_advance / 2; y = e.height / 2 - 4; rnd = random.Random(5)
    for ch in word[:n]:
        adv = ctx.text_extents(ch).x_advance; r = rnd.uniform(-.07, .07); yy = y + rnd.uniform(-.04, .04) * size
        ctx.save(); ctx.translate(x + adv / 2, yy); ctx.rotate(r)
        ctx.move_to(-adv / 2 + size * .02, size * .025); ctx.set_source_rgba(1, .93, .8, .28); ctx.show_text(ch)   # lit lower edge
        ctx.move_to(-adv / 2, 0); ctx.text_path(ch); ctx.set_source_rgba(*hexc('#3b2410'), .78); ctx.fill_preserve()   # groove
        ctx.set_source_rgba(*hexc('#1a0e05'), .5); ctx.set_line_width(size * .02); ctx.stroke()
        ctx.restore(); x += adv * 1.04
    ctx.restore()

def ov_question(ctx, seg, t, d):
    q = seg.get('question')
    if not q: return
    a = eout(clamp((t - .3) / .5))
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, .3 * a); ctx.fill()
    pulse = 1 + .04 * math.sin(t * 3)
    ctx.save(); ctx.translate(W / 2, 560); ctx.scale(pulse * eob(clamp(t / .5)), pulse * eob(clamp(t / .5)))
    text(ctx, '?', 0, 120, 340, GOLD, a); ctx.restore()
    for i, ln in enumerate(q.get('lines', [])):
        text(ctx, ln, W / 2, 860 + i * 84, 66 if i == 0 else 50, WHITE if i == 0 else DIM, a * clamp((t - .6 - i * .5) / .4), bold=(i == 0))
    ops = q.get('options', [])[:3]
    if ops:
        csz = 36; font(ctx, csz); ws = [ctx.text_extents(op).x_advance + 56 for op in ops]; gap = 22
        tot = sum(ws) + gap * (len(ws) - 1)
        if tot > SAFE_W:                                                 # keep the answer chips clear of the side buttons
            csz = 36 * SAFE_W / tot; font(ctx, csz); ws = [ctx.text_extents(op).x_advance + 56 * SAFE_W / tot for op in ops]; gap = 22 * SAFE_W / tot
        cx0 = W / 2 - (sum(ws) + gap * (len(ws) - 1)) / 2
        for i, op in enumerate(ops):
            stamp(ctx, op, cx0 + ws[i] / 2, 1090, eob(clamp((t - 1.3 - i * .35) / .35)), bg=(GOLD, CYAN, RED)[i], size=csz, rot=0)
            cx0 += ws[i] + gap


def ov_hud(ctx, seg, t):
    """series tracker pills under the signature (e.g. DAYS LEFT 29 · SAVINGS $452); savings counts up from `savings_from`"""
    h = seg.get('hud')
    if not h: return
    items = []
    if 'days' in h: items.append((f"DAYS LEFT: {h['days']}", RED))
    if 'savings' in h:
        k = eout(clamp((t - .3) / 1.4)); v = h.get('savings_from', h['savings']) + (h['savings'] - h.get('savings_from', h['savings'])) * k
        items.append((f"SAVINGS: ${v:,.0f}", hexc('#3ddc84')))
    sz = 40; font(ctx, sz); ws = [ctx.text_extents(s).x_advance + 50 for s, _ in items]; gap = 24
    x = W / 2 - (sum(ws) + gap * (len(ws) - 1)) / 2; y = SAFE_TOP + 90
    for (s, col), w in zip(items, ws):
        rrect(ctx, x, y, w, 64, 32); ctx.set_source_rgba(0, 0, 0, .6); ctx.fill()
        rrect(ctx, x, y, w, 64, 32); ctx.set_source_rgba(*col, 1); ctx.set_line_width(4); ctx.stroke()
        text(ctx, s, x + w / 2, y + 46, sz, col, 1); x += w + gap

def polish_voice(voice, sr, fx='cinema'):
    """narrator 'radio/cinema' chain: warmth, presence, gentle compression, a short room — keeps length identical"""
    if fx in (None, 'none'): return voice
    import soundfile as sf, tempfile
    d = tempfile.mkdtemp(); a, b = os.path.join(d, 'a.wav'), os.path.join(d, 'b.wav')
    sf.write(a, voice, sr)
    chain = ('adeclick=t=1.5,highpass=f=70,equalizer=f=120:t=q:w=1:g=3,equalizer=f=3200:t=q:w=1.5:g=2.5,'
             'acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,aecho=0.85:0.5:35|70:0.10|0.05')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a, '-af', chain, '-ar', str(sr), '-ac', '1', b], check=True)
    out, _ = sf.read(b, dtype='float32')
    out = out[:len(voice)] if len(out) >= len(voice) else np.pad(out, (0, len(voice) - len(out)))
    return out / (np.max(np.abs(out)) + 1e-9) * np.max(np.abs(voice))

def suspense_bed(n, sr, timeline, segments, seed=7):
    """Suspense score: enters already tense (drone + heartbeat), rises through the story, hits on 'rewind'/'hit' cuts,
    and leaves unresolved (dissonant cluster + riser cut off by a final boom). Returns (music, sfx), each peak-normalised."""
    rng = np.random.default_rng(seed)
    tt = np.arange(n) / sr; total = n / sr
    mus = np.zeros(n); sfx = np.zeros(n)
    def add(buf, sig, at):
        i = int(at * sr)
        if i >= n or i + len(sig) <= 0: return
        if i < 0: sig = sig[-i:]; i = 0
        sig = np.array(sig, float); k = min(len(sig), int(.008 * sr))
        if k: sig[-k:] *= np.linspace(1, 0, k) ** 2                 # every sound ends at zero (no clicks)
        j = min(n, i + len(sig)); buf[i:j] += sig[:j - i]
    def T(d): return np.arange(int(d * sr)) / sr
    def lp(x, w): return np.convolve(x, np.ones(w) / w, 'same')
    starts = [st for _, st, _ in timeline]
    fxs = [(segments[si].get('fx'), st) for si, st, _ in timeline]
    last_st = timeline[-1][1]
    # intensity: tense from the first frame, dips after the rewind, climbs to the end
    rew = next((st for f, st in fxs if f == 'rewind'), None)
    inten = np.clip(.55 + .45 * tt / total, 0, 1)
    if rew is not None:
        inten = np.where(tt < rew, .75, .35 + .65 * np.clip((tt - rew) / max(1, total - rew), 0, 1))
    fade_in = np.clip(tt / .25, 0, 1); fade_out = np.clip((total - .35 - tt) / .05, 0, 1)   # hard stop at the end
    # 1. low drone (A1 + E2, slow beating) + rumble
    lfo = .75 + .25 * np.sin(2 * np.pi * .12 * tt)
    drone = (np.sin(2 * np.pi * 55 * tt) + .6 * np.sin(2 * np.pi * 55.4 * tt) + .35 * np.sin(2 * np.pi * 82.4 * tt) + .2 * np.sin(2 * np.pi * 110.3 * tt))
    rumble = lp(rng.standard_normal(n), 120) * 6
    mus += (.18 * drone + .12 * rumble) * lfo * (.6 + .4 * inten)
    # 2. high dissonant tremolo (A4 + Bb4), grows with intensity
    trem = .5 + .5 * np.sin(2 * np.pi * 7.5 * tt)
    hi = (np.sin(2 * np.pi * 440 * tt) + np.sin(2 * np.pi * 466.2 * tt) + .5 * np.sin(2 * np.pi * 880.5 * tt)) * trem
    mus += .05 * hi * np.clip((inten - .3) / .7, 0, 1) ** 1.5
    # 2b. MELODY (audible on phone speakers): string pad chords + a music-box/piano ostinato in A minor
    prog = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (146.8, 174.6, 220.0), (164.8, 207.7, 246.9)]  # Am F Dm E
    bar = 2.4
    t0 = 0.0; bi = 0
    while t0 < total:
        ch = prog[bi % 4]; d = min(bar + .6, total - t0)
        x = T(d); env = np.minimum(1, x / .6) * np.minimum(1, (d - x) / .6)
        pad = sum(sum(np.sin(2 * np.pi * f * (1 + dt) * x) for dt in (-.003, 0, .003)) for f in ch)
        pad += .5 * sum(np.sin(2 * np.pi * 2 * f * x) for f in ch)
        add(mus, .10 * pad * env * (.7 + .3 * float(inten[min(n - 1, int(t0 * sr))])), t0)
        t0 += bar; bi += 1
    motif = [440.0, 523.3, 659.3, 523.3, 493.9, 523.3, 659.3, 587.3,   # A C E C B C E D
             440.0, 523.3, 698.5, 659.3, 587.3, 523.3, 493.9, 415.3]   # A C F E D C B G#
    def piano(f, v, d=1.1):
        x = T(d); e = np.exp(-x / .35) * np.minimum(1, x / .004)
        return v * e * (np.sin(2 * np.pi * f * x) + .45 * np.sin(4 * np.pi * f * x) * np.exp(-x / .2) + .2 * np.sin(6 * np.pi * f * x) * np.exp(-x / .1))
    t = .05; i = 0
    while t < total - 1.2:
        k = float(inten[min(n - 1, int(t * sr))])
        step = .30 - .06 * k                                             # the ostinato speeds up with the tension
        add(mus, piano(motif[i % len(motif)], .16 + .12 * k), t)
        if i % 4 == 0: add(mus, piano(motif[i % len(motif)] / 4, .12 + .08 * k, 1.6), t)   # low octave on the downbeat
        t += step; i += 1
    # 3. heartbeat pulse that speeds up (period 1.05 s → 0.62 s)
    def thump(v):
        x = T(.32); f = 48 + 60 * np.exp(-x / .025); ph = 2 * np.pi * np.cumsum(f) / sr
        return v * np.sin(ph) * np.exp(-x / .09)
    t = .15
    while t < total - .6:
        k = float(inten[min(n - 1, int(t * sr))])
        add(mus, thump(.9 * k), t); add(mus, thump(.6 * k), t + .24)
        t += 1.05 - .43 * k
    # 4. clock ticks under the story (after the rewind)
    if rew is not None:
        t = rew + .5
        while t < last_st:
            x = T(.03); add(sfx, .08 * np.sin(2 * np.pi * 2400 * x) * np.exp(-x / .005), t); t += .5
    # 5. risers into every rewind/hit and a boom on the cut
    def riser(d, v):
        x = T(d); k = x / d; f = 200 * (8 ** k); ph = 2 * np.pi * np.cumsum(f) / sr
        nz = np.diff(rng.standard_normal(len(x) + 1))
        return v * k ** 2.4 * (.35 * np.sin(ph) + .4 * nz)
    def boom(v):
        x = T(2.4); f = 30 + 55 * np.exp(-x / .12); ph = 2 * np.pi * np.cumsum(f) / sr
        return v * (np.sin(ph) * np.exp(-x / .8) + .4 * lp(rng.standard_normal(len(x)), 6) * np.exp(-x / .07))
    for f, st in fxs:
        if f in ('rewind', 'hit'):
            add(sfx, riser(1.4, .5), st - 1.4); add(sfx, boom(1.0), st)
            gi, gj = int((st - .12) * sr), int(st * sr)               # tiny silence right before the hit
            if gi > 0: mus[gi:gj] *= np.linspace(1, 0, max(1, gj - gi)) ** 2
    # 6. unresolved ending: cluster swell + riser, cut by a final boom
    end_d = min(4.0, total - last_st)
    x = T(end_d); k = x / end_d
    cl = sum(np.sin(2 * np.pi * f0 * x) for f0 in (220, 233.1, 246.9, 261.6)) * k ** 1.8
    add(mus, .12 * cl, total - .35 - end_d); add(sfx, riser(end_d, .55), total - .35 - end_d)
    add(sfx, boom(1.0), total - .35)
    mus *= fade_in * fade_out
    mus /= np.max(np.abs(mus)) + 1e-9; sfx /= np.max(np.abs(sfx)) + 1e-9
    return mus, sfx

def flash(ctx, t, kind):
    """transition accents: 'rewind' = white flash + scanlines (cold open → story start), 'hit' = white flash"""
    if kind not in ('rewind', 'hit') or t > .45: return
    a = (1 - t / .45) ** 2
    ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(1, 1, 1, .85 * a); ctx.fill()
    if kind == 'rewind':
        for y in range(0, H, 14):
            ctx.rectangle(0, y, W, 3); ctx.set_source_rgba(0, 0, 0, .25 * a); ctx.fill()

# ---------------------------------------------------------------- build
def build(spec_path, outdir, stills=None):
    import soundfile as sf
    spec = json.load(open(spec_path)); sid = spec['id']; os.makedirs(outdir, exist_ok=True)
    base = os.path.dirname(os.path.abspath(spec_path))
    spec['_base'] = base
    def res(p): return p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))
    for seg in spec['segments']:
        seg['_path'] = res(seg['frame'])
        if seg.get('clip'): seg['_clip'] = res(seg['clip'])             # animated version of the frame (played instead of the still)
    voice, sr, timeline, words, total = ps.build_voice(spec)
    voice = polish_voice(voice, sr, spec.get('voice_fx', 'cinema'))
    if spec.get('music', 'suspense') == 'suspense':
        bed, sfx = suspense_bed(len(voice), sr, timeline, spec['segments'])
    else:
        bed, sfx = ps.music_bed(len(voice), sr, timeline, spec.get('music', 'mystery'))
    env = np.convolve(np.abs(voice), np.ones(int(sr * .2)) / int(sr * .2), 'same')
    duck = 1 - .6 * np.clip(env / (env.max() * .2), 0, 1)
    if spec.get('music_file'):                                           # a real music track (e.g. ElevenLabs Music) replaces the synthesized bed; risers/booms stay
        n = len(voice); m = ps.loop_to(ps.load_audio(res(spec['music_file']), sr), n, sr)
        tt = np.arange(n) / sr; tot = n / sr
        m *= np.clip(tt / .05, 0, 1) * np.clip((tot - .3 - tt) / 1.0, 0, 1)
        vact = voice[np.abs(voice) > 0.02]; vr = np.sqrt(np.mean(vact ** 2)) if len(vact) else .1
        m *= vr / (np.sqrt(np.mean(m ** 2)) + 1e-9)                      # music as loud as the voice, then set under it
        if spec.get('music', 'suspense') != 'suspense': sfx = sfx * .3
        duck = 1 - .5 * np.clip(env / (env.max() * .2), 0, 1)
        bedmix = m * spec.get('music_gain', .5) * duck + sfx / (np.max(np.abs(sfx)) + 1e-9) * vr * 1.8 * spec.get('sfx_gain', 1.0)
        mix = voice + bedmix
    elif spec.get('music', 'suspense') == 'suspense':
        duck = 1 - .45 * np.clip(env / (env.max() * .2), 0, 1)
        mix = voice + bed * .30 * duck + sfx * .22
    else:
        mix = voice + bed * .12 * duck + sfx * .06
    if spec.get('music_file') or any(seg.get('voice_file') for seg in spec['segments']):
        # click gate on music+effects only (recorded speech consonants look like clicks; the voice lines are faded at both ends)
        b = (bedmix if spec.get('music_file') else mix - voice) / np.max(np.abs(mix)) * .9 * 1.414
        xb = b if sr == 48000 else ps.load_audio_array(b, sr, 48000)
        d2 = np.abs(np.diff(xb, 2)); loc = np.convolve(d2, np.ones(480) / 480, 'same') + 1e-4
        idx = np.where((d2 > 8 * loc) & (d2 > 0.05))[0]; dur = len(xb) / 48000
        worst = int(np.bincount(idx // 48000).max()) if len(idx) else 0
        okc = len(idx) / dur <= 5 and worst <= 20
        print(f"sound check [music+effects under the voice]: {len(idx) / dur:.2f} spikes/s, worst second {worst} -> {'OK' if okc else 'FAIL - do not publish this render'}")
    mix /= np.max(np.abs(mix)); mix *= .9
    wav = os.path.join(outdir, f'_{sid}.wav'); sf.write(wav, np.stack([mix, mix], 1), sr)
    # a frame shown in consecutive segments keeps one continuous camera move
    spans = []
    for i, (si, st, d) in enumerate(timeline):
        seg = spec['segments'][si]
        if spans and spec['segments'][spans[-1][0]]['frame'] == seg['frame'] and not seg.get('cut'):
            spans[-1][2] = st + d
        else:
            spans.append([si, st, st + d])
    for si, s0, s1 in spans: spec['segments'][si]['_span'] = s1 - s0 + XFADE
    series = spec.get('series_title', 'A TRUE STORY')

    def seg_at(T):
        cur = timeline[0]
        for c in timeline:
            if T >= c[1]: cur = c
        return cur
    def span_at(T):
        cur = spans[0]
        for sp in spans:
            if T >= sp[1]: cur = sp
        return cur

    def frame(T):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        ctx.rectangle(0, 0, W, H); ctx.set_source_rgb(0, 0, 0); ctx.fill()
        sp = span_at(T); idx = spans.index(sp)
        si0, s0, s1 = sp; seg0 = spec['segments'][si0]
        k = clamp((T - s0) / max(.1, s1 - s0 + XFADE))
        tr = None
        if idx > 0 and T - s0 < XFADE:                                   # cross-fade from the previous frame
            p = spans[idx - 1]; pk = clamp((T - p[1]) / max(.1, p[2] - p[1] + XFADE))
            draw_frame(ctx, spec['segments'][p[0]], pk)
            tr = draw_frame(ctx, seg0, k, alpha=ease((T - s0) / XFADE))
        else:
            tr = draw_frame(ctx, seg0, k)
        ambient(ctx, seg0.get('ambient', spec.get('ambient')), T)
        vignette(ctx); grain(ctx, T)
        si, st, d = seg_at(T); seg = spec['segments'][si]; t = T - st
        ov_carve(ctx, seg, t, d, tr); ov_stat(ctx, seg, t, d); ov_question(ctx, seg, t, d); ov_stamp(ctx, seg, t); ov_hud(ctx, seg, t)
        flash(ctx, t, seg.get('fx'))
        sig = spec.get('signature')
        if sig:                                                          # channel signature (YouTube handle) at the top
            font(ctx, 40); e = ctx.text_extents(sig)
            rrect(ctx, W / 2 - e.x_advance / 2 - 28, SAFE_TOP - 6, e.x_advance + 56, 66, 33); ctx.set_source_rgba(0, 0, 0, .45); ctx.fill()
            text(ctx, sig, W / 2, SAFE_TOP + 40, 40, GOLD, .95)
        else:
            text(ctx, series, W / 2, SAFE_TOP + 40, 38, WHITE, .75)
        captions(ctx, words, T)
        ov_hook(ctx, spec.get('hook'), T)                                # big hook text on frame 1 (no fade-in: the first frame must grab)
        if T > total - .6:
            ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, clamp((T - (total - .6)) / .6)); ctx.fill()
        return surf

    if stills:
        for s in stills: frame(float(s)).write_to_png(os.path.join(outdir, f'{sid}_still_{s}.png'))
        print(json.dumps([(spec['segments'][si]['say'][:40], round(st, 2), round(d, 2)) for si, st, d in timeline], indent=0)); return
    out = os.path.join(outdir, f'{sid}.mp4'); tmp = out.replace('.mp4', '.part.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-tune', 'film', '-b:v', '8M', '-minrate', '6M', '-maxrate', '10M', '-bufsize', '16M',
                          '-profile:v', 'high', '-g', '60', '-pix_fmt', 'yuv420p',
                          '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', tmp],
                         stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        p.stdin.write(bytes(frame(f / FPS).get_data()))
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError('ffmpeg failed')
    os.replace(tmp, out); os.remove(wav)
    frame(spec.get('cover_time', 2.0)).write_to_png(os.path.join(outdir, f'{sid}_cover.png'))
    print(f'done: {sid} {total:.1f}s -> {out}')

if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == 'still': build(sys.argv[1], sys.argv[2], stills=sys.argv[4:])
    else: build(sys.argv[1], sys.argv[2])
