"""
Stickman character — the channel's recurring hero.
Signature look: orange ribbed beanie with a cream pom-pom (tilted slightly)
+ orange scarf with two white stripes on the tail. Everything else is a
classic black stickman with a white round face.

Usage:
    stickman(ctx, hip=(x, y), s=1.4, spine=180, hands=((x,y),(x,y)), feet=(...),
             eyes=1, look=0.5, mood=0.3)
All targets (hands/feet) are in world coordinates; arms and legs are solved
with 2-bone IK, so a pose = hip position + spine angle + where hands/feet go.
Angles: dir(a) = (sin a, cos a) in screen space -> 0 = down, 90 = right,
180 = up, 270 = left.  The character faces right by default.
"""
import math

PI = math.pi

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

INK = hexc('#1a1a1c')
FACE = (1, 1, 1)
ORANGE = hexc('#ff6a2b')
ORANGE_D = hexc('#e0501a')
CREAM = hexc('#fff3df')

L_SPINE, L_UA, L_FA, L_TH, L_SH = 150, 68, 66, 86, 86
R_HEAD, NECK, LW = 58, 12, 11

def d(a):
    r = math.radians(a); return (math.sin(r), math.cos(r))

def ik(p, tgt, l1, l2, sign):
    dx, dy = tgt[0] - p[0], tgt[1] - p[1]
    dist = math.hypot(dx, dy)
    dc = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, dist))
    th = math.atan2(dy, dx)
    a = math.acos(max(-1, min(1, (l1 * l1 + dc * dc - l2 * l2) / (2 * l1 * dc))))
    e = (p[0] + l1 * math.cos(th + sign * a), p[1] + l1 * math.sin(th + sign * a))
    end = (p[0] + dc * math.cos(th), p[1] + dc * math.sin(th))
    return e, end

def _rgb(ctx, c, a=1): ctx.set_source_rgba(c[0], c[1], c[2], a)

def _rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2); ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, PI / 2)
    ctx.arc(x + r, y + h - r, r, PI / 2, PI); ctx.arc(x + r, y + r, r, PI, 3 * PI / 2); ctx.close_path()

def beanie(ctx, R):
    ctx.save(); ctx.rotate(-0.13)
    lw = LW * 0.7
    ctx.set_line_width(lw); ctx.set_line_join(1)
    # dome
    ctx.move_to(-R * 1.0, -R * 0.42)
    ctx.curve_to(-R * 0.98, -R * 1.62, R * 0.98, -R * 1.62, R * 1.0, -R * 0.42)
    ctx.close_path(); _rgb(ctx, ORANGE); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()
    # pom-pom
    ctx.arc(R * 0.04, -R * 1.47, R * 0.27, 0, 2 * PI); _rgb(ctx, CREAM); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()
    # ribbed cuff
    _rrect(ctx, -R * 1.12, -R * 0.62, R * 2.24, R * 0.4, R * 0.14)
    _rgb(ctx, ORANGE_D); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()
    ctx.set_line_width(lw * 0.45)
    for i in range(-4, 5):
        x = i * R * 0.22
        ctx.move_to(x, -R * 0.56); ctx.line_to(x, -R * 0.28)
    _rgb(ctx, INK, 0.35); ctx.stroke()
    ctx.restore()

def head(ctx, R, eyes=1.0, look=0.0, mood=0.0, lids=0.0):
    ctx.set_line_width(LW * 0.8)
    ctx.arc(0, 0, R, 0, 2 * PI); _rgb(ctx, FACE); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()
    lx = look * R * 0.3
    for sx in (-1, 1):
        ex, ey = sx * R * 0.3 + lx, R * 0.1
        if eyes > 0.25:
            ry = R * 0.115 * eyes
            cut = ey - ry + 2 * ry * lids * 0.55
            ctx.save()
            if lids > 0:
                ctx.rectangle(ex - R, cut, 2 * R, R); ctx.clip()
            ctx.translate(ex, ey); ctx.scale(R * 0.085, ry)
            ctx.arc(0, 0, 1, 0, 2 * PI); ctx.restore(); _rgb(ctx, INK); ctx.fill()
            if lids > 0:
                ctx.set_line_width(LW * 0.42); ctx.set_line_cap(1)
                ctx.move_to(ex - R * 0.13, cut); ctx.line_to(ex + R * 0.13, cut); _rgb(ctx, INK); ctx.stroke()
        else:
            ctx.set_line_width(LW * 0.45); ctx.set_line_cap(1)
            ctx.arc(ex, ey - R * 0.04, R * 0.1, PI * 0.15, PI * 0.85); _rgb(ctx, INK); ctx.stroke()
    ctx.set_line_width(LW * 0.5); ctx.set_line_cap(1); _rgb(ctx, INK)
    mx, my, w = lx, R * 0.48, R * 0.2
    if mood > 0.05:
        ctx.move_to(mx - w, my); ctx.curve_to(mx - w * 0.4, my + w * mood * 1.1, mx + w * 0.4, my + w * mood * 1.1, mx + w, my)
    elif mood < -0.05:
        ctx.move_to(mx - w, my + w * 0.5); ctx.curve_to(mx - w * 0.4, my + w * 0.5 + w * mood, mx + w * 0.4, my + w * 0.5 + w * mood, mx + w, my + w * 0.5)
    else:
        ctx.move_to(mx - w * 0.8, my + w * 0.15); ctx.line_to(mx + w * 0.8, my + w * 0.15)
    ctx.stroke()
    beanie(ctx, R)

def scarf_band(ctx):
    ctx.set_line_width(LW * 0.6)
    _rrect(ctx, -34, -15, 68, 28, 13); _rgb(ctx, ORANGE); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()

def scarf_tail(ctx, ang, length=80, width=25):
    ctx.save(); ctx.rotate(-math.radians(ang))  # 0 = hanging down
    ctx.set_line_width(LW * 0.6); ctx.set_line_join(1)
    ctx.move_to(-width / 2, 0); ctx.line_to(width / 2, 0)
    ctx.line_to(width / 2 + 3, length); ctx.line_to(-width / 2 + 3, length); ctx.close_path()
    _rgb(ctx, ORANGE); ctx.fill_preserve(); _rgb(ctx, INK); ctx.stroke()
    for f in (0.62, 0.8):
        ctx.rectangle(-width / 2 + 2, length * f, width - 1, 8); _rgb(ctx, CREAM); ctx.fill()
    # fringe
    ctx.set_line_width(LW * 0.4); ctx.set_line_cap(1)
    for i in range(4):
        x = -width / 2 + 6 + i * (width - 6) / 3
        ctx.move_to(x, length + 2); ctx.line_to(x + 2, length + 12)
    _rgb(ctx, INK); ctx.stroke()
    ctx.restore()

def stickman(ctx, hip, s=1.4, spine=180, head_tilt=0, hands=None, feet=None, eyes=1.0, look=0.4,
             mood=0.0, lids=0.0, scarf_ang=12, show_legs=True):
    ctx.save(); ctx.translate(*hip); ctx.scale(s, s)
    loc = lambda p: ((p[0] - hip[0]) / s, (p[1] - hip[1]) / s)
    sd = d(spine)
    neck = (sd[0] * L_SPINE, sd[1] * L_SPINE)
    sh = (neck[0] - sd[0] * 14, neck[1] - sd[1] * 14)
    hl, hr = (loc(hands[0]), loc(hands[1])) if hands else (
        (sh[0] - 46, sh[1] + L_UA + L_FA - 14), (sh[0] + 46, sh[1] + L_UA + L_FA - 14))
    fl, fr = (loc(feet[0]), loc(feet[1])) if feet else ((-24, L_TH + L_SH - 4), (24, L_TH + L_SH - 4))
    ctx.set_line_cap(1); ctx.set_line_join(1); ctx.set_line_width(LW)

    def limb(p, t, l1, l2, sign, alpha=1):
        e, end = ik(p, t, l1, l2, sign)
        ctx.move_to(*p); ctx.line_to(*e); ctx.line_to(*end); _rgb(ctx, INK, alpha); ctx.stroke()
        return end

    if show_legs: limb((0, 0), fl, L_TH, L_SH, -1)
    limb(sh, hl, L_UA, L_FA, 1)
    ctx.move_to(0, 0); ctx.line_to(*neck); _rgb(ctx, INK); ctx.stroke()
    if show_legs: limb((0, 0), fr, L_TH, L_SH, -1)
    # head
    ha = spine + head_tilt; hd = d(ha)
    hc = (neck[0] + hd[0] * (NECK + R_HEAD), neck[1] + hd[1] * (NECK + R_HEAD))
    ctx.move_to(*neck); ctx.line_to(neck[0] + hd[0] * NECK * 1.5, neck[1] + hd[1] * NECK * 1.5); ctx.stroke()
    ctx.save(); ctx.translate(*hc); ctx.rotate(math.radians(180 - ha))
    head(ctx, R_HEAD, eyes, look, mood, lids)
    ctx.restore()
    # scarf
    ctx.save(); ctx.translate(*neck); ctx.rotate(math.radians(180 - spine))
    scarf_band(ctx); ctx.restore()
    anchor = (neck[0] - sd[0] * 4 - sd[1] * 18, neck[1] - sd[1] * 4 + sd[0] * 18)
    ctx.save(); ctx.translate(*anchor); scarf_tail(ctx, scarf_ang); ctx.restore()
    # front arm last
    ctx.set_line_width(LW)
    limb(sh, hr, L_UA, L_FA, 1)
    ctx.restore()
    # world-space helpers for callers
    return {
        'neck': (hip[0] + neck[0] * s, hip[1] + neck[1] * s),
        'shoulder': (hip[0] + sh[0] * s, hip[1] + sh[1] * s),
        'head': (hip[0] + hc[0] * s, hip[1] + hc[1] * s),
    }

def shoulder_of(hip, s, spine):
    sd = d(spine); k = (L_SPINE - 14) * s
    return (hip[0] + sd[0] * k, hip[1] + sd[1] * k)

def head_of(hip, s, spine, head_tilt=0):
    sd = d(spine); hd = d(spine + head_tilt)
    return (hip[0] + (sd[0] * L_SPINE + hd[0] * (NECK + R_HEAD)) * s,
            hip[1] + (sd[1] * L_SPINE + hd[1] * (NECK + R_HEAD)) * s)
