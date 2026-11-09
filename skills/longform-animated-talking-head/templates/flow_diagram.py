"""Flow diagrams v2 for long-form explainers (Kevin 2026-10-27: "this diagram looks horrible ... the flow
for the diagram and the text not fitting in the boxes ... that happened in almost all diagrams").

What v1 (dm_diagrams.graph_card / loop_ring) got wrong, and what this module guarantees instead:
  * Text never leaves its box. Every node is sized FROM its text: the label shrinks (34 -> 22px) and the
    sub line wraps to two lines (then ellipsizes) before the box may exceed `max_node_w`.
  * Nothing clips the panel. `at=(fx, fy)` places the node's CENTER inside the content box minus the
    node's own half size, so fx=1.0 is "flush right", not "half off the card".
  * Nodes never overlap. A relax pass pushes colliding boxes apart (and clear of the hub circle).
  * Edges are real connectors: they leave the facing SIDE of the source box, enter the facing side of the
    target box, curve with tangents perpendicular to those sides, end in an arrowhead, and several edges on
    one side get spread into ports. No more vertical "bus" lines running behind boxes, no arrows mid-wire.
  * Reveal on the spoken word: a node scales/fades in at `on`, an edge draws from source to target over
    0.45 s at its T, then carries two light pulses toward the target. Future nodes are NOT drawn (v1's grey
    ghost boxes were unreadable noise).

API (absolute spoken seconds everywhere, same shape as v1 so call sites barely change):
  flow_card(t, nodes, edges, w, h, title=None, sub=None, acc=COS, active=None) -> RGBA w x h
      nodes: [dict(k, label, sub=None, icon=slug|Image|None, col, at=(fx, fy), on=T, hub=False, size=)]
      edges: [(ka, kb, T, {label=, col=, side=("r","l")})]   side forces (source side, target side)
  loop_card(t, steps, w, h, title=None, active=None, core="creatoros") -> RGBA
      steps: [(label, sub, icon, col, T)]  nodes on an ellipse, arrowed arcs between neighbours
  node_card(label, sub, icon, col, ...) -> the shared text-block design (also usable on its own)
"""
import math
from PIL import Image, ImageDraw, ImageFilter
from longform_engine import cached, F, AR, INK, SILVER, STEEL, WHITE
from fonts import ML
from media_marks import logo_mark

COS = (34, 211, 238)
PANEL = (17, 19, 25)
CARD_TOP = (32, 35, 45)
CARD_BOT = (22, 24, 31)


def _clamp(p):
    return 0.0 if p < 0 else (1.0 if p > 1 else p)


def _ease(p):
    p = _clamp(p)
    return 1 - (1 - p) ** 3


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def _tw(txt, font):
    return _MEASURE.textlength(txt, font=font)


def _wrap(txt, font, maxw, lines=2):
    words, out, cur = txt.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if _tw(test, font) <= maxw or not cur:
            cur = test
        else:
            out.append(cur)
            cur = wd
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        last = out[-1]
        while last and _tw(last + "…", font) > maxw:
            last = last[:-1]
        out[-1] = last.rstrip() + "…"
    # a single word wider than maxw: hard ellipsize
    fixed = []
    for ln in out:
        while _tw(ln, font) > maxw and len(ln) > 2:
            ln = ln[:-2] + "…"
        fixed.append(ln)
    return fixed


def _icon(icon, size):
    if icon is None:
        return None
    if isinstance(icon, Image.Image):
        im = icon.copy()
        im.thumbnail((size, size), Image.LANCZOS)
        return im
    return logo_mark(icon, size, punch=False)


# ───────────────────────── the text block (node) ─────────────────────────
NODE_PAD = 40          # transparent margin around the box (glow + shadow live here)


# node metrics (sized for a ~1240 x 820 panel on a 1920 x 1080 frame: readable at phone size)
LABEL_PX, LABEL_MIN, SUB_PX, SUB_LH = 44, 28, 22, 28
ICON_BOX, ICON_PX, NODE_R = 78, 52, 24


def node_layout(label, sub, max_w=470, icon=True, lsz=LABEL_PX):
    """Measure a node: returns (box_w, box_h, label_font_size, sub_lines)."""
    isz = ICON_BOX if icon else 0
    inner_max = max_w - 24 - isz - (18 if icon else 0) - 28
    fs = lsz
    while fs > LABEL_MIN and _tw(label, F(AR, fs)) > inner_max:
        fs -= 2
    lw = _tw(label, F(AR, fs))
    sub_lines = []
    sw = 0
    if sub:
        sf = F(ML, SUB_PX)
        sub_lines = [sub] if _tw(sub, sf) <= max(inner_max, lw) else _wrap(sub, sf, inner_max, 2)
        sw = max(_tw(x, sf) for x in sub_lines)
    text_w = min(inner_max, max(lw, sw))
    box_w = int(24 + isz + (18 if icon else 0) + text_w + 30)
    box_w = max(box_w, 250)
    box_h = 104 if not sub_lines else (122 if len(sub_lines) == 1 else 150)
    return box_w, box_h, fs, sub_lines


def node_card(label, sub, icon, col, max_w=470, active=False, num=None):
    """The shared text block: dark glass card, accent border, icon tile, fitted label + sub."""
    bw, bh, fs, sub_lines = node_layout(label, sub, max_w, icon is not None)
    key = ("fnode2", label, sub, str(icon) if not isinstance(icon, Image.Image) else id(icon), col, max_w, active, num)

    def build():
        P = NODE_PAD
        im = Image.new("RGBA", (bw + 2 * P, bh + 2 * P), (0, 0, 0, 0))
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.rounded_rectangle([P, P + 12, P + bw, P + bh + 12], NODE_R, fill=(0, 0, 0, 150))
        if active:
            gd.rounded_rectangle([P - 8, P - 8, P + bw + 8, P + bh + 8], NODE_R + 6, fill=col + (150,))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(14 if active else 11)))
        body = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        for y in range(bh):
            f = y / max(1, bh - 1)
            c = tuple(int(CARD_TOP[i] + (CARD_BOT[i] - CARD_TOP[i]) * f) for i in range(3))
            bd.line([0, y, bw, y], fill=c + (255,))
        m = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], NODE_R, fill=255)
        body.putalpha(m)
        im.alpha_composite(body, (P, P))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([P, P, P + bw, P + bh], NODE_R, outline=col + (255 if active else 190,),
                            width=3 if active else 2)
        d.line([P + NODE_R, P + 2, P + bw - NODE_R, P + 2], fill=(255, 255, 255, 34), width=1)
        x = P + 22
        if icon is not None:
            iy = P + (bh - ICON_BOX) // 2
            d.rounded_rectangle([x, iy, x + ICON_BOX, iy + ICON_BOX], 18,
                                fill=tuple(int(c * 0.2) for c in col) + (255,), outline=col + (130,), width=2)
            ic = _icon(icon, ICON_PX)
            if ic is not None:
                im.alpha_composite(ic, (x + (ICON_BOX - ic.width) // 2, iy + (ICON_BOX - ic.height) // 2))
            x += ICON_BOX + 18
        lf = F(AR, fs)
        if sub_lines:
            sf = F(ML, SUB_PX)
            block = fs + 8 + SUB_LH * len(sub_lines)
            y0 = P + (bh - block) / 2
            d.text((x, y0 + fs / 2), label, font=lf, fill=WHITE + (255,), anchor="lm")
            for i, sl in enumerate(sub_lines):
                d.text((x, y0 + fs + 8 + SUB_LH / 2 + i * SUB_LH), sl, font=sf, fill=SILVER + (225,), anchor="lm")
        else:
            d.text((x, P + bh / 2), label, font=lf, fill=WHITE + (255,), anchor="lm")
        if num is not None:
            d.ellipse([P - 16, P - 16, P + 20, P + 20], fill=col + (255,), outline=PANEL + (255,), width=3)
            d.text((P + 2, P + 2), str(num), font=F(AR, 22), fill=INK + (255,), anchor="mm")
        return im
    return cached(key, build), (bw, bh)


def hub_card(size, col=COS, logo="creatoros", t=0.0, label=None):
    """Round core with the logo + a slowly rotating dashed ring (no text under the Creator OS mark)."""
    def base():
        pad = 56
        s = size + pad * 2
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([pad - 12, pad - 12, pad + size + 12, pad + size + 12], fill=col + (110,))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(24)))
        d = ImageDraw.Draw(im)
        d.ellipse([pad, pad, pad + size, pad + size], fill=(12, 16, 22, 255), outline=col + (255,), width=4)
        lg = _icon(logo, int(size * (0.62 if label else 0.7)))
        if lg is not None:
            im.alpha_composite(lg, ((s - lg.width) // 2, (s - lg.height) // 2 - (int(size * 0.1) if label else 0)))
        if label:
            f = F(AR, max(16, size // 9))
            d.text((s / 2, pad + size * 0.8), label, font=f, fill=WHITE + (255,), anchor="mm")
        return im
    im = cached(("fhub", size, col, str(logo), label), base).copy()
    d = ImageDraw.Draw(im)
    c = im.width / 2
    r = size / 2 + 20
    n = 30
    for i in range(n):
        a0 = (i / n) * 2 * math.pi + t * 0.35
        a1 = a0 + (2 * math.pi / n) * 0.5
        d.arc([c - r, c - r, c + r, c + r], math.degrees(a0), math.degrees(a1), fill=col + (200,), width=3)
    return im


# ───────────────────────── geometry ─────────────────────────
def _bez(p0, p1, p2, p3, n=48):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u ** 2, u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def _cum(pts):
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    return cum


def _at(pts, cum, f):
    L = cum[-1] * _clamp(f)
    for i in range(1, len(pts)):
        if cum[i] >= L:
            seg = cum[i] - cum[i - 1] or 1
            u = (L - cum[i - 1]) / seg
            return (pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * u, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * u), i
    return pts[-1], len(pts) - 1


def _arrow(d, tip, prev, col, size=17):
    ang = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
    p1 = (tip[0] - size * math.cos(ang - 0.45), tip[1] - size * math.sin(ang - 0.45))
    p2 = (tip[0] - size * math.cos(ang + 0.45), tip[1] - size * math.sin(ang + 0.45))
    d.polygon([tip, p1, p2], fill=col + (255,))


def _pill(txt, col):
    def build():
        f = F(ML, 17)
        w = int(_tw(txt, f)) + 28
        im = Image.new("RGBA", (w, 34), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, 33], 17, fill=(14, 16, 21, 245), outline=col + (230,), width=2)
        d.text((w / 2, 17), txt, font=f, fill=col + (255,), anchor="mm")
        return im
    return cached(("fpill", txt, col), build)


# ───────────────────────── flow card ─────────────────────────
def flow_card(t, nodes, edges, w=1240, h=820, title=None, sub=None, acc=COS, active=None, max_node_w=470,
              panel=True):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if panel:
        def build_panel():
            p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle([16, 24, w - 16, h - 8], 32, fill=(0, 0, 0, 150))
            p = Image.alpha_composite(p, sh.filter(ImageFilter.GaussianBlur(12)))
            d = ImageDraw.Draw(p)
            d.rounded_rectangle([10, 10, w - 10, h - 16], 32, fill=PANEL + (240,), outline=(255, 255, 255, 30), width=2)
            for yy in range(70 if title else 40, h - 40, 32):
                for xx in range(40, w - 30, 32):
                    d.point((xx, yy), fill=(255, 255, 255, 20))
            if title:
                d.rounded_rectangle([36, 34, 46, 74], 4, fill=acc + (255,))
                tf = F(AR, 36)
                d.text((62, 54), title, font=tf, fill=WHITE + (255,), anchor="lm")
                if sub:
                    x = 62 + _tw(title, tf) + 20
                    sf = F(ML, 19)
                    if x + _tw(sub, sf) < w - 40:
                        d.text((x, 57), sub, font=sf, fill=SILVER + (200,), anchor="lm")
                d.line([36, 92, w - 36, 92], fill=(255, 255, 255, 22), width=1)
            return p
        img.alpha_composite(cached(("fpanel", w, h, title, sub, acc), build_panel))
    top = 112 if title else 40
    X0, Y0, X1, Y1 = 44, top, w - 44, h - 52

    # measure + place (centers inside the content box, nodes never clip the panel)
    geo = {}
    for n in nodes:
        if n.get("hub"):
            s = n.get("size", 170)
            bw = bh = s
        else:
            bw, bh, _f, _s = node_layout(n["label"], n.get("sub"), n.get("w", max_node_w), n.get("icon") is not None)
        fx, fy = n["at"]
        cx = X0 + bw / 2 + 4 + fx * ((X1 - X0) - bw - 8)
        cy = Y0 + bh / 2 + 4 + fy * ((Y1 - Y0) - bh - 8)
        geo[n["k"]] = [cx, cy, bw, bh, bool(n.get("hub"))]
    # relax overlaps (12 px gutter), keep inside the box
    keys = list(geo)
    for _ in range(40):
        moved = False
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = geo[keys[i]], geo[keys[j]]
                ox = (a[2] + b[2]) / 2 + 24 - abs(a[0] - b[0])
                oy = (a[3] + b[3]) / 2 + 24 - abs(a[1] - b[1])
                if ox > 0 and oy > 0:
                    moved = True
                    if oy <= ox:
                        s = 1 if a[1] <= b[1] else -1
                        a[1] -= s * oy / 2
                        b[1] += s * oy / 2
                    else:
                        s = 1 if a[0] <= b[0] else -1
                        a[0] -= s * ox / 2
                        b[0] += s * ox / 2
        for g in geo.values():
            g[0] = min(max(g[0], X0 + g[2] / 2), X1 - g[2] / 2)
            g[1] = min(max(g[1], Y0 + g[3] / 2), Y1 - g[3] / 2)
        if not moved:
            break

    # ports: decide sides, then spread edges that share a side
    def side_of(ka, kb):
        a, b = geo[ka], geo[kb]
        dx, dy = b[0] - a[0], b[1] - a[1]
        gx = abs(dx) - (a[2] + b[2]) / 2       # clear horizontal gap between the boxes
        gy = abs(dy) - (a[3] + b[3]) / 2       # clear vertical gap
        # horizontal when there is real room beside; vertical when the target sits mostly above/below
        if gx > 40 or gx >= gy:
            return ("r", "l") if dx > 0 else ("l", "r")
        return ("b", "t") if dy > 0 else ("t", "b")

    plan = []
    use = {}
    for e in edges:
        ka, kb, Te = e[0], e[1], e[2]
        opt = e[3] if len(e) > 3 else {}
        if ka not in geo or kb not in geo:
            continue
        sa, sb = opt.get("side") or side_of(ka, kb)
        plan.append([ka, kb, Te, opt, sa, sb])
        use.setdefault((ka, sa), []).append((len(plan) - 1, 0))
        use.setdefault((kb, sb), []).append((len(plan) - 1, 1))
    port = {}
    for (k, s), lst in use.items():
        g = geo[k]
        # order ports by where the other end is, so wires never cross at the box
        def other(item):
            pe = plan[item[0]]
            ok = pe[1] if item[1] == 0 else pe[0]
            return geo[ok][1] if s in ("l", "r") else geo[ok][0]
        lst = sorted(lst, key=other)
        n = len(lst)
        span = (g[3] if s in ("l", "r") else g[2]) * 0.6
        for i, item in enumerate(lst):
            off = 0 if n == 1 else (-span / 2 + span * i / (n - 1))
            port[item] = off

    def anchor(k, s, off):
        cx, cy, bw, bh, hub = geo[k]
        if hub:
            ang = {"r": 0, "l": math.pi, "b": math.pi / 2, "t": -math.pi / 2}[s]
            ang += off / max(1, bw / 2) * 0.9
            r = bw / 2 + 6
            return (cx + r * math.cos(ang), cy + r * math.sin(ang))
        if s == "r":
            return (cx + bw / 2 + 2, cy + off)
        if s == "l":
            return (cx - bw / 2 - 2, cy + off)
        if s == "b":
            return (cx + off, cy + bh / 2 + 2)
        return (cx + off, cy - bh / 2 - 2)

    NORM = {"r": (1, 0), "l": (-1, 0), "b": (0, 1), "t": (0, -1)}
    wires = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd, gd = ImageDraw.Draw(wires), ImageDraw.Draw(glow)
    labels = []
    col_of = {n["k"]: n.get("col", acc) for n in nodes}
    for i, (ka, kb, Te, opt, sa, sb) in enumerate(plan):
        if t < Te - 0.05:
            continue
        p0 = anchor(ka, sa, port[(i, 0)])
        p3 = anchor(kb, sb, port[(i, 1)])
        dist = math.dist(p0, p3)
        k = max(46, dist * 0.42)
        n0, n3 = NORM[sa], NORM[sb]
        p1 = (p0[0] + n0[0] * k, p0[1] + n0[1] * k)
        p2 = (p3[0] + n3[0] * k, p3[1] + n3[1] * k)
        pts = _bez(p0, p1, p2, p3)
        cum = _cum(pts)
        f = _ease((t - Te) / 0.45)
        col = opt.get("col") or col_of.get(ka, acc)
        tip, idx = _at(pts, cum, f)
        drawn = pts[:idx] + [tip]
        if len(drawn) > 1:
            gd.line(drawn, fill=col + (150,), width=12, joint="curve")
            wd.line(drawn, fill=col + (255,), width=4, joint="curve")
            wd.line(drawn, fill=(255, 255, 255, 90), width=1)
        if f >= 1:
            _arrow(wd, pts[-1], pts[-4], col)
            for q in range(2):
                ph = ((t - Te) * 0.55 + q * 0.5) % 1.0
                (px, py), _ = _at(pts, cum, ph)
                gd.ellipse([px - 9, py - 9, px + 9, py + 9], fill=col + (200,))
                wd.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255, 255))
            if opt.get("label"):
                (mx, my), _ = _at(pts, cum, 0.5)
                labels.append((_pill(opt["label"], col), mx, my))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7)))
    img.alpha_composite(wires)

    # nodes on top of wires
    for n in nodes:
        on = n.get("on", -99)
        if t < on - 0.05:
            continue
        cx, cy, bw, bh, hub = geo[n["k"]]
        p = _ease((t - on) / 0.35)
        if hub:
            spr = hub_card(int(bw), n.get("col", COS), n.get("icon", "creatoros"), t,
                           label=n.get("label") if n.get("icon", "creatoros") != "creatoros" else None)
        else:
            spr, _sz = node_card(n["label"], n.get("sub"), n.get("icon"), n["col"], n.get("w", max_node_w),
                                 active=(active == n["k"]), num=n.get("num"))
        if p < 1:
            s = 0.88 + 0.12 * p
            spr = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)
            a = spr.split()[3].point(lambda v: int(v * p))
            spr.putalpha(a)
        img.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))
    for pill, mx, my in labels:
        img.alpha_composite(pill, (int(mx - pill.width / 2), int(my - pill.height / 2)))
    return img


# ───────────────────────── loop card ─────────────────────────
def loop_card(t, steps, w=1240, h=880, title=None, active=None, core="creatoros", acc=COS, max_node_w=400,
              core_size=200, comet=True):
    """Steps around an ellipse, arrowed arcs between neighbours (clockwise from 12 o'clock), core in the
    middle. steps: [(label, sub, icon, col, T)]; a step (and the arc into it) appears at T."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def build_panel():
        p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([16, 24, w - 16, h - 8], 32, fill=(0, 0, 0, 150))
        p = Image.alpha_composite(p, sh.filter(ImageFilter.GaussianBlur(12)))
        d = ImageDraw.Draw(p)
        d.rounded_rectangle([10, 10, w - 10, h - 16], 32, fill=PANEL + (240,), outline=(255, 255, 255, 30), width=2)
        for yy in range(70 if title else 40, h - 40, 32):
            for xx in range(40, w - 30, 32):
                d.point((xx, yy), fill=(255, 255, 255, 20))
        if title:
            d.rounded_rectangle([36, 34, 46, 74], 4, fill=acc + (255,))
            d.text((62, 54), title, font=F(AR, 36), fill=WHITE + (255,), anchor="lm")
            d.line([36, 92, w - 36, 92], fill=(255, 255, 255, 22), width=1)
        return p
    img.alpha_composite(cached(("lpanel2", w, h, title, acc), build_panel))
    top = 104 if title else 30
    n = len(steps)
    sizes = [node_layout(s[0], s[1], max_node_w, s[2] is not None)[:2] for s in steps]
    mw = max(s[0] for s in sizes)
    mh = max(s[1] for s in sizes)
    cx, cy = w / 2, top + (h - 40 - top) / 2
    rx = (w - 60) / 2 - mw / 2 - 10
    ry = (h - 40 - top) / 2 - mh / 2 - 6
    pos = []
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        pos.append((cx + rx * math.cos(a), cy + ry * math.sin(a), a))

    def inside(pt, j, m=10):
        x, y, _a = pos[j]
        bw, bh = sizes[j]
        return abs(pt[0] - x) < bw / 2 + m and abs(pt[1] - y) < bh / 2 + m

    wires = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd, gd = ImageDraw.Draw(wires), ImageDraw.Draw(glow)
    # faint full ellipse guide
    wd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=(255, 255, 255, 26), width=2)
    arcs = []
    for i in range(n):
        j = (i + 1) % n
        a0, a1 = pos[i][2], pos[j][2] + (2 * math.pi if j == 0 else 0)
        pts = []
        for q in range(81):
            a = a0 + (a1 - a0) * q / 80
            pt = (cx + rx * math.cos(a), cy + ry * math.sin(a))
            if not inside(pt, i) and not inside(pt, j):
                pts.append(pt)
        arcs.append(pts)
        T_on = steps[j][4]
        if len(pts) < 4 or t < T_on - 0.05:
            continue
        col = steps[j][3]
        f = _ease((t - T_on) / 0.4)
        cum = _cum(pts)
        tip, idx = _at(pts, cum, f)
        drawn = pts[:idx] + [tip]
        if len(drawn) > 1:
            gd.line(drawn, fill=col + (140,), width=12, joint="curve")
            wd.line(drawn, fill=col + (255,), width=4, joint="curve")
        if f >= 1:
            _arrow(wd, pts[-1], pts[-4], col)
    if comet and all(t >= s[4] for s in steps):
        lap = (t * 0.22) % 1.0
        seg = int(lap * n)
        pts = arcs[seg]
        if len(pts) > 3:
            cum = _cum(pts)
            for q in range(8):
                (px, py), _ = _at(pts, cum, _clamp((lap * n - seg) - q * 0.03))
                r = 8 - q * 0.8
                gd.ellipse([px - r * 2, py - r * 2, px + r * 2, py + r * 2], fill=WHITE + (int(160 * (1 - q / 8)),))
                wd.ellipse([px - r, py - r, px + r, py + r], fill=WHITE + (int(255 * (1 - q / 8)),))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7)))
    img.alpha_composite(wires)
    hub = hub_card(core_size, acc, core, t)
    img.alpha_composite(hub, (int(cx - hub.width / 2), int(cy - hub.height / 2)))
    for i, (lab, sub, icon, col, T_on) in enumerate(steps):
        if t < T_on - 0.05:
            continue
        spr, _ = node_card(lab, sub, icon, col, max_node_w, active=(active == i), num=i + 1)
        p = _ease((t - T_on) / 0.35)
        if p < 1:
            s = 0.88 + 0.12 * p
            spr = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)
            spr.putalpha(spr.split()[3].point(lambda v: int(v * p)))
        x, y, _a = pos[i]
        img.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
    return img


# ───────────────────────── tag (replaces the flat chip) ─────────────────────────
def tag(txt, accent=None, fsz=26):
    """Glass pill: dark gradient body, accent hairline border, glowing accent dot, white Oswald text.
    Kevin 2026-10-27: the old chip (flat grey slab + side bar, grey text) "design of these text blocks are bad"."""
    accent = accent or COS

    def build():
        f = F(AR, fsz)
        tw = int(_tw(txt, f))
        h = fsz + 30
        dot = max(10, fsz // 2.6)
        w = int(tw + 30 + dot + 16 + 26)
        P = 16
        im = Image.new("RGBA", (w + 2 * P, h + 2 * P), (0, 0, 0, 0))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([P, P + 6, P + w, P + h + 6], h // 2, fill=(0, 0, 0, 140))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8)))
        body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bd = ImageDraw.Draw(body)
        for y in range(h):
            fz = y / max(1, h - 1)
            c = tuple(int((30 + accent[i] * 0.10) * (1 - fz) + (18 + accent[i] * 0.05) * fz) for i in range(3))
            bd.line([0, y, w, y], fill=c + (245,))
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=255)
        body.putalpha(m)
        im.alpha_composite(body, (P, P))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([P, P, P + w, P + h], h // 2, outline=accent + (200,), width=2)
        d.line([P + h // 2, P + 2, P + w - h // 2, P + 2], fill=(255, 255, 255, 40), width=1)
        dx, dy = P + 22 + dot / 2, P + h / 2
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([dx - dot, dy - dot, dx + dot, dy + dot], fill=accent + (170,))
        im = Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(5)))
        d = ImageDraw.Draw(im)
        d.ellipse([dx - dot / 2, dy - dot / 2, dx + dot / 2, dy + dot / 2], fill=accent + (255,))
        d.text((dx + dot / 2 + 14, dy), txt, font=f, fill=WHITE + (255,), anchor="lm")
        return im
    return cached(("tag", txt, accent, fsz), build)
