"""Code-drawn frames for 'The 3:12 Messages' (Pom series). Flat 2D night style, Pom as 'you'.
python3 draw_frames.py  -> f01.png ... f08.png (1260x2240)"""
import cairo, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
from stickman import stickman, hexc, INK

W, H = 1260, 2240
OUT = os.path.dirname(os.path.abspath(__file__))
NAVY, NAVY2, NAVY3 = hexc('#141b33'), hexc('#1d2747'), hexc('#2a3760')
LINE = hexc('#0b0f1e')
GLOW = hexc('#bfe3ff')
RED = hexc('#ff4b4b')
WARM = hexc('#ffb35c')
SKIN = (1, 1, 1)

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def fill(ctx, col, a=1, stroke=True, lw=7):
    ctx.set_source_rgba(*col, a)
    if stroke: ctx.fill_preserve(); ctx.set_source_rgba(*LINE, 1); ctx.set_line_width(lw); ctx.set_line_join(1); ctx.stroke()
    else: ctx.fill()

def room(ctx, wall=NAVY2, floor=NAVY, floor_y=1650):
    g = cairo.LinearGradient(0, 0, 0, floor_y); g.add_color_stop_rgb(0, *[c * .8 for c in wall]); g.add_color_stop_rgb(1, *wall)
    ctx.rectangle(0, 0, W, floor_y); ctx.set_source(g); ctx.fill()
    ctx.rectangle(0, floor_y, W, H - floor_y); ctx.set_source_rgb(*floor); ctx.fill()
    ctx.move_to(0, floor_y); ctx.line_to(W, floor_y); ctx.set_source_rgb(*LINE); ctx.set_line_width(6); ctx.stroke()

def window(ctx, x, y, w, h, night=True):
    rr(ctx, x, y, w, h, 10); fill(ctx, hexc('#0d1430') if night else hexc('#9fc8ff'))
    if night:
        ctx.arc(x + w * .72, y + h * .25, 38, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, .9, .85); ctx.fill()
    ctx.set_line_width(5)
    for i in range(1, 12):                                        # blinds
        yy = y + h * i / 12; ctx.move_to(x + 8, yy); ctx.line_to(x + w - 8, yy); ctx.set_source_rgba(*NAVY3, .9); ctx.stroke()

def light_cone(ctx, x, y, r, col, a=.35):
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source(g); ctx.fill()

def font(ctx, size, bold=True):
    ctx.select_font_face('Poppins', 0, 1 if bold else 0); ctx.set_font_size(size)

def ctext(ctx, s, x, y, size, col, bold=True):
    font(ctx, size, bold); e = ctx.text_extents(s); ctx.move_to(x - e.x_advance / 2, y); ctx.set_source_rgb(*col); ctx.show_text(s)

def clock(ctx, x, y, s='3:12'):
    rr(ctx, x, y, 230, 120, 18); fill(ctx, hexc('#11131c'))
    light_cone(ctx, x + 115, y + 60, 260, RED, .25)
    ctext(ctx, s, x + 115, y + 92, 78, RED)

def nightstand(ctx, x, y):
    ctx.rectangle(x, y, 280, 330); fill(ctx, hexc('#3a2d33'))
    ctx.rectangle(x + 30, y + 60, 220, 90); fill(ctx, hexc('#46363c'), lw=5)

def bubble(ctx, x, y, w, lines, size=50, col=(1, 1, 1), tcol=INK):
    lh = size * 1.32; h = lh * len(lines) + 46
    rr(ctx, x, y, w, h, 34); ctx.set_source_rgb(*col); ctx.fill()
    for i, ln in enumerate(lines):
        font(ctx, size, bold=False); ctx.move_to(x + 32, y + 26 + size + i * lh); ctx.set_source_rgb(*tcol); ctx.show_text(ln)
    return y + h

def phone(ctx, cx, cy, w, h, msgs, header='Unknown', time='3:12'):
    """big phone held up; msgs = list of (lines) bubbles"""
    light_cone(ctx, cx, cy, 900, GLOW, .28)
    rr(ctx, cx - w / 2, cy - h / 2, w, h, 70); fill(ctx, hexc('#0e0f14'), lw=9)
    sx, sy, sw, sh = cx - w / 2 + 28, cy - h / 2 + 28, w - 56, h - 56
    rr(ctx, sx, sy, sw, sh, 48); ctx.set_source_rgb(*hexc('#eef2f8')); ctx.fill()
    ctx.rectangle(sx, sy + 40, sw, 150); ctx.set_source_rgb(*hexc('#dde3ee')); ctx.fill()
    ctext(ctx, time, sx + 80, sy + 70, 34, INK)
    ctx.arc(cx, sy + 110, 34, 0, 2 * math.pi); ctx.set_source_rgb(*hexc('#9aa3b5')); ctx.fill()
    ctext(ctx, '?', cx, sy + 126, 44, (1, 1, 1))
    ctext(ctx, header, cx, sy + 178, 34, INK)
    y = sy + 240
    for lines in msgs:
        y = bubble(ctx, sx + 30, y, sw - 90, lines, size=52, col=hexc('#d9dde6')) + 26

def hand(ctx, x, y, s=1.0):
    """Pom's stick hand holding the phone from below"""
    ctx.set_line_width(22 * s); ctx.set_line_cap(1); ctx.move_to(x, y); ctx.line_to(x + 40 * s, H + 40); ctx.set_source_rgb(*LINE); ctx.stroke()

def save(surf, name):
    surf.write_to_png(os.path.join(OUT, name)); print('wrote', name)

def new():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); return s, cairo.Context(s)


PS = 1.9                      # Pom scale in every scene
FLOOR = 1820

def desk(c, x0, x1, top, col=hexc('#5b4636')):
    c.rectangle(x0, top, x1 - x0, 46); fill(c, col)
    c.rectangle(x0 + 40, top + 46, 40, FLOOR - top - 46); fill(c, [v * .85 for v in col])
    c.rectangle(x1 - 80, top + 46, 40, FLOOR - top - 46); fill(c, [v * .85 for v in col])

def chair(c, x, seat_y, facing=-1):
    """chair under a sitting Pom; facing -1 = Pom looks left (back of chair on the right)"""
    c.rectangle(x - 110, seat_y, 220, 30); fill(c, hexc('#2c2f3d'))
    bx = x + 95 * (-facing) - 15
    c.rectangle(bx, seat_y - 330, 30, 330); fill(c, hexc('#2c2f3d'))
    c.rectangle(x - 15, seat_y + 30, 30, FLOOR - seat_y - 60); fill(c, hexc('#2c2f3d'))
    c.rectangle(x - 100, FLOOR - 34, 200, 24); fill(c, hexc('#2c2f3d'), lw=5)

def pom_sit(c, x, facing=-1, hands=None, lean=10, **kw):
    """Pom sitting on a chair at x, facing left (-1) or right (+1). Returns hip."""
    seat = FLOOR - 175
    chair(c, x, seat, facing)
    hip = (x, seat - 8)
    feet = ((x + facing * 150, FLOOR - 8), (x + facing * 190, FLOOR - 8))
    stickman(c, hip, s=PS, spine=180 - facing * lean, feet=feet, hands=hands, **kw)
    return hip

def f01():
    s, c = new(); room(c, floor_y=1760)
    window(c, 780, 300, 360, 520)
    rr(c, 330, 1180, 900, 120, 30); fill(c, hexc('#4a3a44'))           # bed frame
    rr(c, 360, 1060, 860, 160, 40); fill(c, hexc('#d7dcea'))           # mattress
    rr(c, 380, 950, 300, 140, 60); fill(c, hexc('#eef1f8'))            # pillow
    # Pom lying on his back, head on the pillow, phone light on his face
    stickman(c, (900, 1010), s=1.6, spine=270, head_tilt=0, hands=((700, 780), (740, 790)), feet=((1180, 1020), (1190, 1030)),
             eyes=1.15, look=.5, mood=-.25, show_legs=False)
    rr(c, 760, 985, 470, 180, 50); fill(c, hexc('#3a4c8c'))            # blanket
    light_cone(c, 720, 760, 460, GLOW, .55)
    c.save(); c.translate(720, 760); c.rotate(.5); rr(c, -45, -75, 90, 150, 14); fill(c, hexc('#cfe9ff'), lw=5); c.restore()   # phone held up, glowing
    nightstand(c, 110, 1430)
    clock(c, 135, 1300)
    c.rectangle(0, 0, W, H); c.set_source_rgba(0, 0, .05, .15); c.fill()
    save(s, 'f01.png')

def fphone(name, msgs, bg=NAVY):
    s, c = new(); c.rectangle(0, 0, W, H); c.set_source_rgb(*bg); c.fill()
    window(c, 60, 240, 280, 400)
    phone(c, W / 2, 1020, 880, 1420, msgs)
    for x in (300, 960):
        c.set_line_width(24); c.set_line_cap(1); c.move_to(x, 1600); c.line_to(x + (x - 630) * .25, H + 60); c.set_source_rgb(*LINE); c.stroke()
        c.arc(x, 1590, 30, 0, 2 * math.pi); c.set_source_rgb(*LINE); c.fill()
    c.rectangle(0, 0, W, H); c.set_source_rgba(0, 0, .05, .1); c.fill()
    save(s, name)

def f03():
    s, c = new(); room(c, wall=hexc('#1f2a4d'), floor_y=FLOOR)
    light_cone(c, 450, 1100, 800, GLOW, .2)
    top = FLOOR - 330
    desk(c, 60, 860, top)
    rr(c, 170, top - 460, 560, 380, 22); fill(c, hexc('#0e0f14'))
    rr(c, 200, top - 430, 500, 320, 12); c.set_source_rgb(*hexc('#2b3a66')); c.fill()
    c.rectangle(420, top - 80, 60, 80); fill(c, hexc('#0e0f14'), lw=5)
    c.save(); c.translate(460, top - 40); c.rotate(-.22); rr(c, -280, -30, 560, 70, 12); fill(c, hexc('#2d2f38')); c.restore()
    c.save(); c.translate(430, top - 14); c.rotate(.04); c.rectangle(-110, -50, 220, 100); fill(c, hexc('#ffe45c'), lw=5)
    c.set_line_width(5); c.set_source_rgba(*LINE, .55)
    for i in range(3): c.move_to(-80, -18 + i * 24); c.line_to(70 - i * 28, -18 + i * 24)
    c.stroke(); c.restore()
    stickman(c, (990, FLOOR - 340), s=PS, spine=188, head_tilt=-8, hands=((730, top - 60), (1080, FLOOR - 560)),
             feet=((940, FLOOR - 6), (1040, FLOOR - 6)), eyes=1.2, look=-.8, mood=-.4)
    c.rectangle(0, 0, W, H); c.set_source_rgba(0, 0, .05, .12); c.fill()
    save(s, 'f03.png')

def laptop(c, x0, top, w, screen_col):
    h = w * .66
    rr(c, x0, top - h - 30, w, h, 20); fill(c, hexc('#cfd5e2'))
    rr(c, x0 + 24, top - h - 6, w - 48, h - 48, 10); c.set_source_rgb(*screen_col); c.fill()
    c.move_to(x0 - 30, top - 30); c.line_to(x0 + w + 30, top - 30); c.line_to(x0 + w + 50, top); c.line_to(x0 - 50, top); c.close_path(); fill(c, hexc('#b9c0cf'), lw=5)
    return (x0 + 24, top - h - 6, w - 48, h - 48)

def f04():
    s, c = new(); room(c, wall=hexc('#22305a'), floor_y=FLOOR)
    c.arc(560, 0, 50, 0, math.pi); c.set_source_rgb(*WARM); c.fill(); light_cone(c, 560, 60, 1000, WARM, .2)
    top = FLOOR - 330
    desk(c, 20, 780, top, hexc('#6a4e38'))
    sx, sy, sw, sh = laptop(c, 50, top, 680, hexc('#f7f9fc'))
    ctext(c, 'SUBSCRIPTIONS', sx + sw / 2, sy + 62, 40, INK)
    items = [('Streaming', '$15.99'), ('Music', '$10.99'), ('Cloud', '$9.99'), ('Gym (never)', '$29.99'),
             ('Game pass', '$16.99'), ('Food box', '$22.99'), ('VPN', '$4.99')]
    for i, (n, p) in enumerate(items):
        y = sy + 92 + i * 46
        font(c, 32, False); c.move_to(sx + 30, y + 30); c.set_source_rgb(*INK); c.show_text(n)
        font(c, 32, True); e = c.text_extents(p); c.move_to(sx + sw - 30 - e.x_advance, y + 30); c.show_text(p)
        c.move_to(sx + 20, y + 19); c.line_to(sx + sw - 20, y + 19); c.set_source_rgb(*RED); c.set_line_width(6); c.stroke()
    pom_sit(c, 940, facing=-1, hands=((740, top - 50), (770, top - 40)), lean=14, eyes=1, look=-.9, mood=.15)
    save(s, 'f04.png')

def f05():
    s, c = new(); room(c, wall=hexc('#18213f'), floor_y=FLOOR)
    window(c, 840, 260, 320, 460)
    top = FLOOR - 330
    desk(c, 20, 780, top, hexc('#4c3b2e'))
    sx, sy, sw, sh = laptop(c, 50, top, 680, hexc('#24345f'))
    light_cone(c, sx + sw / 2, sy + sh / 2, 700, GLOW, .3)
    fx, fy = sx + sw / 2 - 130, sy + 70
    c.move_to(fx, fy); c.line_to(fx + 110, fy); c.line_to(fx + 140, fy + 30); c.line_to(fx + 260, fy + 30); c.line_to(fx + 260, fy + 200); c.line_to(fx, fy + 200); c.close_path(); fill(c, hexc('#ffd15c'), lw=5)
    ctext(c, 'someday', sx + sw / 2, fy + 290, 54, (1, 1, 1))
    clock(c, 560, top - 520 - 130)
    pom_sit(c, 940, facing=-1, hands=((740, top - 50), (770, top - 40)), lean=14, eyes=1, look=-.9, mood=-.05, lids=.35)
    c.rectangle(0, 0, W, H); c.set_source_rgba(0, 0, .05, .12); c.fill()
    save(s, 'f05.png')

def f06():
    s, c = new(); room(c, wall=hexc('#1a2445'), floor_y=FLOOR)
    window(c, 100, 260, 320, 460)
    top = FLOOR - 330
    desk(c, 440, 1220, top, hexc('#4c3b2e'))
    c.move_to(1180, top); c.line_to(1140, top - 380); c.line_to(1020, top - 470); c.set_source_rgb(*LINE); c.set_line_width(14); c.stroke()
    c.move_to(950, top - 510); c.line_to(1090, top - 510); c.line_to(1040, top - 420); c.line_to(1000, top - 420); c.close_path(); fill(c, WARM)
    light_cone(c, 900, top - 200, 650, WARM, .35)
    sx, sy, sw, sh = laptop(c, 470, top, 680, hexc('#f7f9fc'))
    ctext(c, 'NEW ORDER', sx + sw / 2, sy + 130, 54, hexc('#1f9d55'))
    ctext(c, '+ $49.00', sx + sw / 2, sy + 260, 104, hexc('#1f9d55'))
    pom_sit(c, 250, facing=1, hands=((470, top - 50), (390, top - 380)), lean=10, eyes=1.15, look=.9, mood=.8)
    save(s, 'f06.png')

def f07():
    s, c = new(); room(c, wall=hexc('#2b3a66'), floor=hexc('#1c2546'), floor_y=FLOOR)
    rr(c, 560, 560, 520, 1260, 12); fill(c, hexc('#5a4433'))
    rr(c, 640, 690, 360, 220, 10); fill(c, hexc('#e9d7a6'), lw=5)
    ctext(c, 'MANAGER', 820, 825, 56, INK)
    c.arc(1020, 1260, 18, 0, 2 * math.pi); fill(c, WARM, lw=4)
    c.rectangle(560, FLOOR - 14, 520, 14); c.set_source_rgba(*WARM, .9); c.fill(); light_cone(c, 820, FLOOR, 380, WARM, .45)
    stickman(c, (300, FLOOR - 340), s=PS, spine=180, head_tilt=4, hands=((230, FLOOR - 470), (400, FLOOR - 500)),
             feet=((260, FLOOR - 6), (350, FLOOR - 6)), eyes=1, look=.8, mood=-.35)
    save(s, 'f07.png')

if __name__ == '__main__':
    f01()
    fphone('f02.png', [['In 30 days you lose', 'your job.'], ['Do exactly what I say.', 'Tell no one.']])
    f03(); f04(); f05(); f06(); f07()
    fphone('f08.png', [['Your boss will call you', 'in on Friday.'], ['Whatever he offers...', 'say NO.'], ["Don't ask who I am.", 'You already know.']])
