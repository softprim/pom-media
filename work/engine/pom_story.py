"""
"Pom tells a true story" — vertical Short: Pom narrates (synthetic voice) over real public-domain photos.

    python3 pom_story.py stories/<id>.json out/                 # full render
    python3 pom_story.py stories/<id>.json out/ still 2 9 15     # stills at seconds (voice is generated first)

Needs: pom/stickman.py next to this file, `pip install kokoro-onnx soundfile pycairo --break-system-packages`,
and the voice model in TTS_DIR (default ~/tts): run `python3 pom_story.py --setup` once per machine.
Outputs: <id>.mp4, <id>_cover.png, <id>_captions.md (incl. image credits + sources).
Spec format: see STORY_README.md.
"""
import cairo, math, os, sys, subprocess, random, json, urllib.request, urllib.parse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stickman import stickman, shoulder_of, head_of, hexc, INK, R_HEAD

W, H, FPS = 1080, 1920, 30
PI = math.pi
TTS_DIR = os.path.expanduser(os.environ.get('TTS_DIR', '~/tts'))
HF = 'https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/'
VOICES = ['am_michael', 'am_adam', 'am_fenrir', 'am_puck', 'am_onyx', 'af_heart', 'af_bella', 'bm_george', 'bm_lewis', 'bm_fable', 'bf_emma']
UA = 'PomStories/1.0 (softprim)'

# ---------------------------------------------------------------- setup / assets
def setup():
    os.makedirs(TTS_DIR, exist_ok=True)
    mp = os.path.join(TTS_DIR, 'model.onnx')
    if not os.path.exists(mp):
        urllib.request.urlretrieve(HF + 'onnx/model.onnx', mp)     # full-precision model: clearer, more natural voice than the quantized one
    vo = {}
    for v in VOICES:
        p = os.path.join(TTS_DIR, v + '.bin')
        if not os.path.exists(p): urllib.request.urlretrieve(HF + f'voices/{v}.bin', p)
        vo[v] = np.fromfile(p, dtype=np.float32).reshape(-1, 1, 256)
    np.savez(os.path.join(TTS_DIR, 'voices.npz'), **vo)
    os.replace(os.path.join(TTS_DIR, 'voices.npz'), os.path.join(TTS_DIR, 'voices.bin'))
    print('TTS ready in', TTS_DIR)

def fetch(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, 'wb') as f: f.write(r.read())

def get_image(ref, cache):
    """ref: 'nasa:PIA00452' (NASA Image Library) or 'loc:<direct image url>' (Library of Congress) or 'file:<path>'."""
    os.makedirs(cache, exist_ok=True)
    kind, val = ref.split(':', 1)
    if kind == 'file': return val
    name = os.path.join(cache, (val if kind == 'nasa' else urllib.parse.quote(val, safe='')[-80:]) + '.jpg')
    if os.path.exists(name): return name
    if kind == 'nasa':
        for sz in ('large', 'medium', 'orig'):
            try:
                fetch(f'https://images-assets.nasa.gov/image/{val}/{val}~{sz}.jpg', name)
                from PIL import Image; Image.open(name).verify(); return name
            except Exception: pass
        raise RuntimeError('NASA image not found: ' + val)
    if kind == 'loc':
        fetch(val.split('#')[0], name); return name
    raise ValueError(ref)

# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
PALETTES = {
    'space':   (hexc('#0b1026'), hexc('#1b2452')),
    'mystery': (hexc('#120d1a'), hexc('#2b1d3a')),
    'history': (hexc('#1d160f'), hexc('#3a2a1b')),
    'nature':  (hexc('#0d1a14'), hexc('#1d3a2b')),
}
GOLD, CYAN, WHITE, DIM, RED = hexc('#ffcf5c'), hexc('#61d6ff'), (1, 1, 1), hexc('#a7a3c0'), hexc('#ff5d5d')

def font(ctx, size, bold=True):
    ctx.select_font_face('Poppins', 0, 1 if bold else 0); ctx.set_font_size(size)

def text(ctx, s, x, y, size, col=WHITE, a=1.0, bold=True, maxw=760):   # 760 = inside the platform UI safe zone
    if a <= 0: return
    font(ctx, size, bold); e = ctx.text_extents(s)
    if e.x_advance > maxw:
        size *= maxw / e.x_advance; font(ctx, size, bold); e = ctx.text_extents(s)
    ctx.move_to(x - e.x_advance / 2, y); ctx.set_source_rgba(*col, a); ctx.show_text(s)

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -PI / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI); ctx.arc(x + r, y + r, r, PI, 3 * PI / 2); ctx.close_path()

STARS = [(random.Random(i).uniform(0, W), random.Random(i * 7).uniform(0, H), random.Random(i * 13).uniform(0.6, 2.6)) for i in range(220)]
def backdrop(ctx, T, pal):
    b1, b2 = PALETTES.get(pal, PALETTES['space'])
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *b1); g.add_color_stop_rgb(1, *b2)
    ctx.rectangle(0, 0, W, H); ctx.set_source(g); ctx.fill()
    for i, (x, y, r) in enumerate(STARS):
        tw = .5 + .5 * math.sin(T * 1.4 + i)
        ctx.arc((x - T * 6 * r) % W, y, r, 0, 2 * PI); ctx.set_source_rgba(1, 1, 1, (.25 + .5 * tw * r / 2.6) * (1 if pal == 'space' else .35)); ctx.fill()

_cache = {}
def photo_surface(path):
    if path not in _cache:
        from PIL import Image
        im = Image.open(path).convert('RGB')
        sc = 1500 / max(im.size); im = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.LANCZOS)
        arr = np.array(im); h, w, _ = arr.shape
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
        buf = np.zeros((h, stride // 4, 4), np.uint8)
        buf[:, :w, 0] = arr[..., 2]; buf[:, :w, 1] = arr[..., 1]; buf[:, :w, 2] = arr[..., 0]; buf[:, :w, 3] = 255
        _cache[path] = (cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, stride), w, h, buf)
    return _cache[path]

CARD = (70, 200, 940, 960)

def stamp(ctx, s, x, y, k, bg=GOLD, fg=INK, size=46, rot=-0.06):
    if k <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(k, k)
    font(ctx, size); e = ctx.text_extents(s)
    rrect(ctx, -e.x_advance / 2 - 26, -size - 2, e.x_advance + 52, size * 1.6, 14); ctx.set_source_rgba(*bg, 1); ctx.fill()
    text(ctx, s, 0, 2, size, fg); ctx.restore()

def card_photo(ctx, seg, k_in, t, d, T, ext):
    x, y, w, h = CARD
    surf, iw, ih, _ = photo_surface(seg['_img'])
    prog = (ext + t) / max(seg.get('_span', d), 1)
    zoom = seg.get('zoom', 'in')
    z = 1.04 + (0.10 * prog if zoom == 'in' else 0.10 * (1 - prog))
    sc = max(w / iw, h / ih) * z
    off = prog * 30 * (1 if seg.get('pan', 'left') == 'left' else -1)
    a = eout(k_in)
    ctx.save(); ctx.translate(0, (1 - a) * 60)
    rrect(ctx, x - 10, y - 10, w + 20, h + 20, 34); ctx.set_source_rgba(1, 1, 1, .95 * a); ctx.fill()
    rrect(ctx, x, y, w, h, 26); ctx.clip()
    ctx.translate(x + w / 2 - off, y + h / 2); ctx.scale(sc, sc); ctx.translate(-iw / 2, -ih / 2)
    ctx.set_source_surface(surf, 0, 0); ctx.paint_with_alpha(a)
    ctx.restore()
    if seg.get('credit'): text(ctx, seg['credit'], x + w - 140, y + h - 22, 24, WHITE, .6 * a, bold=False, maxw=260)
    if seg.get('stamp'): stamp(ctx, seg['stamp'], x + 210, y + 90, eob(clamp((t - .3) / .4)))
    if seg.get('label'):
        k = eob(clamp((t - .4) / .4))
        if k > 0:
            ctx.save(); ctx.translate(x + w / 2, y + h - 90); ctx.scale(k, k)
            font(ctx, 54); e = ctx.text_extents(seg['label'])
            rrect(ctx, -e.x_advance / 2 - 30, -52, e.x_advance + 60, 80, 40); ctx.set_source_rgba(*INK, .85); ctx.fill()
            text(ctx, seg['label'], 0, 6, 54, GOLD); ctx.restore()
    if seg.get('circle'):
        cx, cy = seg['circle']
        px = x + w / 2 - off + (cx * iw - iw / 2) * sc; py = y + h / 2 + (cy * ih - ih / 2) * sc
        k = clamp((t - .6) / .8)
        if k > 0:
            ctx.new_path(); ctx.set_line_width(7); ctx.arc(px, py, seg.get('circle_r', 46), -PI / 2, -PI / 2 + 2 * PI * eout(k))
            ctx.set_source_rgba(*GOLD, 1); ctx.stroke()
        if seg.get('arrow_label'):
            k2 = eout(clamp((t - .2) / .5))
            ax, ay = px - 230, py + 200
            ctx.new_path(); ctx.set_line_width(9); ctx.set_line_cap(1)
            ctx.move_to(ax, ay); ctx.line_to(ax + (px - 60 - ax) * k2, ay + (py + 50 - ay) * k2); ctx.set_source_rgba(*GOLD, 1); ctx.stroke()
            if k2 >= 1: text(ctx, seg['arrow_label'], ax - 10, ay + 60, 52, GOLD)

def card_travel(ctx, seg, k_in, t, d, T, ext):
    """something travels from A to B while a clock/counter runs (e.g. a signal taking a day)"""
    x, y, w, h = CARD; a = eout(k_in)
    rrect(ctx, x, y, w, h, 26); ctx.set_source_rgba(1, 1, 1, .06 * a); ctx.fill()
    ax, ay = x + 140, y + h - 180; bx, by = x + w - 150, y + 200
    ctx.arc(ax, ay, 60, 0, 2 * PI); ctx.set_source_rgba(*CYAN, a); ctx.fill()
    text(ctx, seg.get('from', 'A'), ax, ay + 110, 36, DIM, a)
    ctx.arc(bx, by, 16, 0, 2 * PI); ctx.set_source_rgba(*GOLD, a); ctx.fill()
    text(ctx, seg.get('to', 'B'), bx - 40, by - 40, 36, GOLD, a)
    ctx.set_dash([12, 14]); ctx.set_line_width(4); ctx.move_to(ax, ay); ctx.line_to(bx, by); ctx.set_source_rgba(1, 1, 1, .3 * a); ctx.stroke(); ctx.set_dash([])
    k = clamp((t - .8) / max(.5, d - 1.6))
    sx, sy, ex_, ey_ = (bx, by, ax, ay) if seg.get('direction', 'to_a') == 'to_a' else (ax, ay, bx, by)
    px, py = sx + (ex_ - sx) * ease(k), sy + (ey_ - sy) * ease(k)
    ctx.arc(px, py, 13, 0, 2 * PI); ctx.set_source_rgba(*CYAN, 1); ctx.fill()
    v = seg.get('from_value', 0) + (seg.get('to_value', 24) - seg.get('from_value', 0)) * ease(k)
    if seg.get('format') == 'clock':
        hh = int(v); mm = int((v - hh) * 60); ss = int(((v - hh) * 60 - mm) * 60); s = f'{hh:02d}:{mm:02d}:{ss:02d}'
    else:
        s = f"{seg.get('prefix', '')}{v:,.{seg.get('decimals', 0)}f}{seg.get('suffix', '')}"
    text(ctx, s, x + w / 2, y + 520, 120, CYAN, a)
    text(ctx, seg.get('caption', ''), x + w / 2, y + 590, 40, DIM, a, bold=False)
    if k >= 1 and seg.get('big'):
        kk = eob(clamp((t - (d - .8)) / .4))
        ctx.save(); ctx.translate(x + w / 2, y + 720); ctx.scale(kk, kk); text(ctx, seg['big'], 0, 0, 84, GOLD); ctx.restore()

def card_stat(ctx, seg, k_in, t, d, T, ext):
    """big number counting up with a label"""
    x, y, w, h = CARD; a = eout(k_in)
    rrect(ctx, x, y, w, h, 26); ctx.set_source_rgba(1, 1, 1, .06 * a); ctx.fill()
    k = eout(clamp((t - .3) / max(.6, d * .6)))
    v = seg.get('from_value', 0) + (seg['to_value'] - seg.get('from_value', 0)) * k
    s = f"{seg.get('prefix', '')}{v:,.{seg.get('decimals', 0)}f}{seg.get('suffix', '')}"
    text(ctx, seg.get('title', ''), x + w / 2, y + 300, 54, DIM, a)
    text(ctx, s, x + w / 2, y + 500, 150, GOLD, a)
    text(ctx, seg.get('caption', ''), x + w / 2, y + 600, 48, WHITE, a * clamp((t - .8) / .4), bold=False)

def card_question(ctx, seg, k_in, t, d, T, ext):
    """mystery ending: big '?' and the open question; nobody knows the answer"""
    x, y, w, h = CARD; a = eout(k_in)
    rrect(ctx, x, y, w, h, 26); ctx.set_source_rgba(1, 1, 1, .05 * a); ctx.fill()
    pulse = 1 + .05 * math.sin(T * 3)
    ctx.save(); ctx.translate(x + w / 2, y + 430); ctx.scale(pulse * eob(clamp(t / .5)), pulse * eob(clamp(t / .5)))
    text(ctx, '?', 0, 120, 380, GOLD, a); ctx.restore()
    for i, ln in enumerate(seg.get('lines', [])):
        text(ctx, ln, x + w / 2, y + 700 + i * 80, 60 if i == 0 else 48, WHITE if i == 0 else DIM, a * clamp((t - .6 - i * .5) / .4), bold=(i == 0))
    if seg.get('options'):
        ops = seg['options'][:3]; font(ctx, 34)
        ws = [ctx.text_extents(op).x_advance + 52 for op in ops]; gap = 24
        cx0 = x + w / 2 - (sum(ws) + gap * (len(ws) - 1)) / 2
        for i, op in enumerate(ops):
            k = eob(clamp((t - 1.2 - i * .35) / .35))
            stamp(ctx, op, cx0 + ws[i] / 2, y + 900, k, bg=(GOLD if i == 0 else (CYAN if i == 1 else RED)), size=34, rot=0)
            cx0 += ws[i] + gap

def card_end(ctx, seg, k_in, t, d, T, ext):
    x, y, w, h = CARD; a = eout(k_in)
    cx, cy = x + w / 2, y + 420
    for r, al in ((160, .08), (100, .14), (55, .3)):
        ctx.arc(cx, cy, r * (1 + .05 * math.sin(T * 3)), 0, 2 * PI); ctx.set_source_rgba(*GOLD, al * a); ctx.fill()
    ctx.arc(cx, cy, 22, 0, 2 * PI); ctx.set_source_rgba(*GOLD, a); ctx.fill()
    for i in range(3):
        k = ((T * .7) + i / 3) % 1
        ctx.set_line_width(4); ctx.arc(cx, cy, 40 + 220 * k, -PI * .35, PI * .35); ctx.set_source_rgba(*CYAN, (1 - k) * .7 * a); ctx.stroke()
    lines = seg.get('lines', [])
    for i, ln in enumerate(lines):
        text(ctx, ln, x + w / 2, y + 760 + i * 100, 96 if i == 0 else 64, WHITE if i == 0 else GOLD, a * clamp((t - i * 1.0) / .4))

def card_word(ctx, seg, k_in, t, d, T, ext):
    """a single word carved/written on a surface (e.g. CROATOAN on a wooden post)"""
    x, y, w, h = CARD; a = eout(k_in)
    rrect(ctx, x, y, w, h, 26); ctx.set_source_rgba(*hexc('#2a1d12'), a); ctx.fill()
    px, pw = x + 250, 440
    g = cairo.LinearGradient(px, 0, px + pw, 0)
    for stop, c in ((0, '#6b4a2b'), (.5, '#8a6238'), (1, '#5a3c22')): g.add_color_stop_rgb(stop, *hexc(c))
    ctx.rectangle(px, y + 40, pw, h - 80); ctx.set_source(g); ctx.fill()
    rnd = random.Random(7); ctx.set_line_width(2)
    for i in range(40):
        xx = px + rnd.uniform(10, pw - 10); ctx.move_to(xx, y + 40); ctx.curve_to(xx + rnd.uniform(-20, 20), y + 300, xx + rnd.uniform(-20, 20), y + 600, xx + rnd.uniform(-15, 15), y + h - 40)
        ctx.set_source_rgba(0, 0, 0, .12); ctx.stroke()
    word = seg.get('word', '')
    k = clamp((t - .3) / max(.8, d * .5)); n = int(len(word) * k + .999) if k > 0 else 0
    ctx.save(); ctx.translate(px + pw / 2, y + h / 2); ctx.rotate(-PI / 2)
    font(ctx, 120); e = ctx.text_extents(word); x0 = -e.x_advance / 2
    for i, ch in enumerate(word[:n]):
        ctx.move_to(x0 + 1, 44); ctx.set_source_rgba(1, 1, 1, .15); ctx.show_text(ch)
        ctx.move_to(x0, 40); ctx.set_source_rgba(*hexc('#2a170a'), .95); ctx.show_text(ch)
        x0 += ctx.text_extents(ch).x_advance
    ctx.restore()
    if seg.get('note'): text(ctx, seg['note'], x + w / 2, y + h - 10 + 0, 1, WHITE, 0)

CARDS = {'word': card_word, 'photo': card_photo, 'travel': card_travel, 'stat': card_stat, 'question': card_question, 'end': card_end}

# ---------------------------------------------------------------- Pom narrator
POM_HIP = (540, 1745)
def pom(ctx, T, amp, seg, t):
    s = 1.15
    hip = (POM_HIP[0], POM_HIP[1] - 6 * math.sin(T * 2))
    sh = shoulder_of(hip, s, 180)
    bob = 18 * amp
    pose = seg.get('pose', 'talk')
    hl = (sh[0] - 90, sh[1] + 120 - bob)
    if pose == 'point':
        k = ease(clamp(t / .4)); hr = (sh[0] + 60 + 90 * k, sh[1] + 140 - 280 * k)
    elif pose == 'shrug':
        k = ease(clamp(t / .4)); hl = (sh[0] - 90 - 60 * k, sh[1] + 120 - 120 * k); hr = (sh[0] + 90 + 60 * k, sh[1] + 120 - 120 * k)
    elif pose == 'think':
        hc = head_of(hip, s, 180); hr = (hc[0] + 30, hc[1] + 92)
    else:
        hr = (sh[0] + 95, sh[1] + 110 - bob * 1.4)
    mood = seg.get('mood', 0.2)
    stickman(ctx, hip, s, 180, head_tilt=4 * math.sin(T * 1.7), hands=(hl, hr), look=seg.get('look', 0.0), mood=mood,
             eyes=0.05 if (T % 3.3) > 3.18 else 1, scarf_ang=14 + 6 * math.sin(T * 2))
    if pose == 'think':
        hc = head_of(hip, s, 180); text(ctx, '?', hc[0] + 120, hc[1] - 90 + 8 * math.sin(T * 4), 90, GOLD, .9)
    if amp > 0.08:
        hc = head_of(hip, s, 180, 4 * math.sin(T * 1.7))
        ctx.save(); ctx.translate(hc[0], hc[1] + R_HEAD * 0.48 * s); ctx.scale(1, 0.4 + 0.9 * amp)
        ctx.arc(0, 0, R_HEAD * 0.17 * s, 0, 2 * PI); ctx.restore(); ctx.set_source_rgba(*INK, 1); ctx.fill()

# ---------------------------------------------------------------- captions
def captions(ctx, words, T):
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
    size = 64; font(ctx, size)
    sp = ctx.text_extents('a a').x_advance - ctx.text_extents('aa').x_advance
    widths = [ctx.text_extents(w['txt']).x_advance for w in chunk]
    total = sum(widths) + sp * (len(chunk) - 1)
    if total > 960:
        size = int(64 * 960 / total); font(ctx, size); sp = ctx.text_extents('a a').x_advance - ctx.text_extents('aa').x_advance
        widths = [ctx.text_extents(w['txt']).x_advance for w in chunk]; total = sum(widths) + sp * (len(chunk) - 1)
    x = W / 2 - total / 2; y = 1290
    rrect(ctx, x - 30, y - 68, total + 60, 94, 22); ctx.set_source_rgba(0, 0, 0, .5); ctx.fill()
    for w, wd in zip(chunk, widths):
        active = w['s'] <= T <= w['e'] + .05
        font(ctx, size); ctx.move_to(x, y); ctx.set_source_rgba(*(GOLD if active else WHITE), 1); ctx.show_text(w['txt'])
        x += wd + sp

# ---------------------------------------------------------------- audio
def load_audio(path, sr):
    """any audio file -> mono float array at `sr` (via ffmpeg)"""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def load_audio_array(x, sr, sr_out):
    """resample an array with ffmpeg (clean band-limited resampling)"""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f64le', '-ar', str(sr), '-ac', '1', '-i', '-', '-f', 'f32le', '-ar', str(sr_out), '-'],
                         input=np.asarray(x, np.float64).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def loop_to(m, n, sr, xf=1.5):
    """repeat a music track up to n samples with a cross-fade at every seam (no click, no jump)"""
    if len(m) >= n: return m[:n].copy()
    x = int(xf * sr); out = m.copy(); ramp = np.linspace(0, 1, x)
    while len(out) < n:
        out[-x:] = out[-x:] * (1 - ramp) + m[:x] * ramp
        out = np.concatenate([out, m[x:]])
    return out[:n]

def build_voice(spec, gap=0.35):
    """Narration track. A segment with "voice_file" (e.g. an ElevenLabs take, path relative to the spec) uses that recording;
    segments without one are spoken by Kokoro (loaded only when needed)."""
    base = spec.get('_base', '.'); k = None
    def kokoro():
        nonlocal k
        if k is None:
            from kokoro_onnx import Kokoro
            k = Kokoro(os.path.join(TTS_DIR, 'model.onnx'), os.path.join(TTS_DIR, 'voices.bin'))
        return k
    voice_name = spec.get('voice', 'am_michael'); lang = 'en-gb' if voice_name.startswith('b') else 'en-us'
    sr = 48000 if all(seg.get('voice_file') for seg in spec['segments']) else 24000   # full quality when every line is a recording (Kokoro is 24 kHz)
    parts, timeline, words = [], [], []; t = 0.5
    for si, seg in enumerate(spec['segments']):
        if seg.get('voice_file'):
            vf = seg['voice_file']; vf = vf if os.path.isabs(vf) else os.path.normpath(os.path.join(base, vf))
            s = load_audio(vf, sr); act = s[np.abs(s) > 0.02]
            if len(act): s = s * (0.13 / np.sqrt(np.mean(act ** 2)))          # every recorded line at the same loudness
        else:
            s, sr = kokoro().create(seg['say'], voice=voice_name, speed=seg.get('speed', spec.get('speed', 0.97)), lang=lang)
        s = s.astype(np.float32); nz = np.where(np.abs(s) > 0.01)[0]
        if len(nz): s = s[max(0, nz[0] - sr // 30): nz[-1] + sr // 15]
        fk = min(len(s) // 2, sr // 100); s[:fk] *= np.linspace(0, 1, fk); s[-fk:] *= np.linspace(1, 0, fk)   # 10 ms fades: no clicks at the edges
        d = len(s) / sr; pause = seg.get('pause', gap)
        timeline.append((si, t, d + pause))
        shown = seg.get('caption_text', seg['say']).replace('...', '… ').split()
        shown = [w.replace('…', '...') for w in shown if w]
        tot = sum(len(w) + 2 for w in shown) or 1; acc = 0
        for w in shown:
            a0 = t + d * acc / tot; acc += len(w) + 2; words.append({'txt': w, 's': a0, 'e': t + d * acc / tot, 'seg': si})
        parts.append((t, s)); t += d + pause
    total = t + 0.6; n = int(total * sr) + 1
    voice = np.zeros(n, np.float32)
    for st, s in parts:
        i = int(st * sr); voice[i:i + len(s)] += s
    return voice, sr, timeline, words, total

MOOD_PROG = {
    'wonder':  [(-12, [0, 3, 7]), (-16, [-4, 0, 3]), (-9, [3, 7, 10]), (-14, [-2, 2, 5])],     # Am F C G
    'mystery': [(-12, [0, 3, 7]), (-11, [1, 4, 8]), (-12, [0, 3, 7]), (-13, [-1, 3, 6])],     # Am Bb Am G#dim-ish
    'warm':    [(-9, [3, 7, 10]), (-14, [-2, 2, 5]), (-12, [0, 3, 7]), (-16, [-4, 0, 3])],    # C G Am F
}
def music_bed(n, sr, timeline, mood='wonder'):
    tt = np.arange(n) / sr; out = np.zeros(n)
    def hz(semi): return 220 * 2 ** (semi / 12)
    prog = MOOD_PROG.get(mood, MOOD_PROG['wonder']); per = 4.0
    for i in range(int(tt[-1] / per) + 1):
        root, ch = prog[i % 4]; a = i * per
        m = (tt >= a) & (tt < a + per + 1.5)
        x = tt[m] - a; env = np.minimum(1, x / 1.2) * np.minimum(1, (per + 1.5 - x) / 1.5)
        s = sum(np.sin(2 * np.pi * hz(c) * tt[m]) * .5 + np.sin(2 * np.pi * hz(c) * 2 * tt[m] + .4) * .15 for c in ch)
        s += .6 * np.sin(2 * np.pi * hz(root) * tt[m]); out[m] += env * s
        for b in range(4):
            st = a + b * 1.0; L = int(sr * 1.6); xx = np.arange(L) / sr
            f = hz(ch[(b * 2) % 3] + 12) * (1.0 if mood != 'mystery' or b % 2 == 0 else 1.0595)
            i0 = int(st * sr); j0 = min(n, i0 + L)
            fade = np.minimum(1, (L - np.arange(L)) / (sr * .03))          # de-click: every note ends at zero
            if i0 < n: out[i0:j0] += (.35 * np.exp(-xx * 2.2) * fade * (np.sin(2 * np.pi * f * xx) + .3 * np.sin(4 * np.pi * f * xx)))[:j0 - i0]
    out /= np.max(np.abs(out))
    rng = np.random.default_rng(1); sfx = np.zeros(n)
    for _, st, d in timeline:
        L = int(sr * .45); x = np.arange(L) / sr
        nz = np.convolve(rng.standard_normal(L), np.ones(30) / 30, 'same') * np.sin(np.pi * x / x[-1]) ** 2 * 2.5
        i0 = max(0, int((st - .15) * sr)); j0 = min(n, i0 + L); sfx[i0:j0] += nz[:j0 - i0]
    return out, sfx

# ---------------------------------------------------------------- build
def build(spec_path, outdir, stills=None):
    import soundfile as sf
    spec = json.load(open(spec_path)); sid = spec['id']; os.makedirs(outdir, exist_ok=True)
    cache = os.path.join(outdir, '_img')
    for seg in spec['segments']:
        if seg.get('card', 'photo') == 'photo': seg['_img'] = get_image(seg['image'], cache)
    voice, sr, timeline, words, total = build_voice(spec)
    # photo continuity: same image across consecutive segments keeps zooming
    span_start = {}
    for i, (si, st, d) in enumerate(timeline):
        seg = spec['segments'][si]
        prev = spec['segments'][timeline[i - 1][0]] if i else None
        if prev is not None and seg.get('card', 'photo') == 'photo' and prev.get('image') == seg.get('image'):
            span_start[si] = span_start[timeline[i - 1][0]]
        else:
            span_start[si] = st
    for si, st, d in timeline:
        seg = spec['segments'][si]; ends = [s2 + d2 for s3, s2, d2 in timeline if span_start[s3] == span_start[si]]
        seg['_span'] = max(ends) - span_start[si]
    n = len(voice)
    bed, sfx = music_bed(n, sr, timeline, spec.get('music', 'wonder'))
    env = np.convolve(np.abs(voice), np.ones(int(sr * .2)) / int(sr * .2), 'same')
    duck = 1 - .6 * np.clip(env / (env.max() * .2), 0, 1)
    mix = voice + bed * .11 * duck + sfx * .05; mix /= np.max(np.abs(mix)); mix *= .9
    wav = os.path.join(outdir, f'_{sid}.wav'); sf.write(wav, np.stack([mix, mix], 1), sr)
    hop = sr // FPS
    amp = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) if i * hop < n else 0 for i in range(int(total * FPS) + 2)])
    amp = np.clip(amp / (np.percentile(amp[amp > 0], 90) + 1e-6), 0, 1)
    pal = spec.get('palette', 'space'); series = spec.get('series_title', 'POM TELLS A TRUE STORY')

    def frame(T):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
        backdrop(ctx, T, pal)
        cur = timeline[0]
        for c in timeline:
            if T >= c[1]: cur = c
        si, st, d = cur; seg = spec['segments'][si]; t = max(0, T - st)
        same = span_start[si] != st
        k_in = 1 if same else clamp(t / .45)
        CARDS[seg.get('card', 'photo')](ctx, seg, k_in, t, d, T, st - span_start[si])
        text(ctx, series, W / 2, 140, 40, DIM, .9)
        captions(ctx, words, T)
        pom(ctx, T, amp[min(len(amp) - 1, int(T * FPS))], seg, t)
        if T > total - .5:
            ctx.rectangle(0, 0, W, H); ctx.set_source_rgba(0, 0, 0, clamp((T - (total - .5)) / .5)); ctx.paint()
        return surf

    if stills:
        for s in stills: frame(float(s)).write_to_png(os.path.join(outdir, f'{sid}_still_{s}.png'))
        print(json.dumps([(spec['segments'][si]['say'][:40], round(st, 2), round(d, 2)) for si, st, d in timeline], indent=0)); return
    out = os.path.join(outdir, f'{sid}.mp4'); tmp = out.replace('.mp4', '.part.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-tune', 'animation', '-b:v', '10M', '-minrate', '8M', '-maxrate', '12M', '-bufsize', '20M', '-profile:v', 'high', '-g', '60', '-pix_fmt', 'yuv420p',
                          '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', tmp],
                         stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        p.stdin.write(bytes(frame(f / FPS).get_data()))
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError('ffmpeg failed')
    os.replace(tmp, out); os.remove(wav)
    cov = spec.get('cover_time', 2.0); frame(cov).write_to_png(os.path.join(outdir, f'{sid}_cover.png'))
    c = spec.get('captions', {}); yt = c.get('youtube', {})
    with open(os.path.join(outdir, f'{sid}_captions.md'), 'w') as f:
        f.write(f"# {spec.get('title', sid)}\n\nDuration: {total:.1f} s\n\n")
        f.write("## YouTube Shorts\n\n**Title:**\n```\n" + yt.get('title', '') + "\n```\n\n**Description:**\n```\n" + yt.get('description', '') + "\n```\n\n")
        f.write("## TikTok\n\n```\n" + c.get('tiktok', '') + "\n```\n\n## Instagram Reels\n\n```\n" + c.get('instagram', '') + "\n```\n\n")
        f.write("## Image credits\n\n" + '\n'.join(f"- {cr}" for cr in spec.get('image_credits', [])) + "\n\n## Sources (fact check)\n\n" +
                '\n'.join(f"- {s}" for s in spec.get('sources', [])) + "\n")
    print(f'done: {sid} {total:.1f}s -> {out}')

if __name__ == '__main__':
    if sys.argv[1] == '--setup': setup()
    elif len(sys.argv) > 3 and sys.argv[3] == 'still': build(sys.argv[1], sys.argv[2], stills=sys.argv[4:])
    else: build(sys.argv[1], sys.argv[2])
