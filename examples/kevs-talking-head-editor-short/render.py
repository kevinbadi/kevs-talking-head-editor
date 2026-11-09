#!/usr/bin/env python3
"""Split animated talking-head: Kev's Talking Head Editor skill (Claude edits, Giphy GIFs, sync, free skill CTA). 1080x1920."""
import json
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = open("animation_assets_and_beats.py").read()
ASSETS = SRC.split('os.makedirs("frames/out2"')[0]
exec(compile(ASSETS, "animation_assets", "exec"), globals())

from hyper_edits import (  # noqa: E402
    caption_impact,
    clamp01,
    guarded_conveyor,
    hyperframe,
    lanes,
    punch_scale,
    punch_zoom,
    shake_offset,
    whip_dir,
    whip_wipe,
)
from media_marks import figure_round, gif_card, name_plate  # noqa: E402
from light_fx import (  # noqa: E402
    bloom_orb,
    caption_bloom,
    hud_scan,
    light_hit,
    light_rays,
    neon_grid,
    scanlines,
    slot_vignette,
    speed_streaks,
)
from claude_marks import load_sphinx, place_claude_invader, place_claude_sphinx, skill_chip  # noqa: E402

def bloom_orb(layer, cx, cy, r, color, a=70):
    """Padded orb: the stock one clips its blur at the canvas edge and shows a square."""
    r = max(24, int(r))

    def build():
        pad = r
        s_ = r * 2 + pad * 2
        m = Image.new("L", (s_, s_), 0)
        ImageDraw.Draw(m).ellipse([pad, pad, s_ - pad, s_ - pad], fill=a)
        m = m.filter(ImageFilter.GaussianBlur(r // 2 + 8))
        out = Image.new("RGBA", (s_, s_), color + (0,))
        out.putalpha(m)
        return out
    orb = cached(("orb2", r, color, a), build)
    layer.alpha_composite(orb, (int(cx - orb.width / 2), int(cy - orb.height / 2)))


if (W, H) != (1080, 1920):
    raise SystemExit(f"must be 1080x1920, got {W}x{H}")

INK = (10, 11, 14)
SILVER = (198, 204, 214)
STEEL = (92, 98, 108)
GRAPHITE = (36, 38, 46)
CHAR = (48, 50, 58)
NEON = (57, 255, 132)
ORANGE = (255, 122, 24)
RED = (255, 48, 64)
CYAN = (56, 220, 236)          # CreatorOS teal
PINK = (236, 64, 122)          # Instagram
PURPLE = (153, 120, 255)
GOLD = (255, 214, 90)
CORAL = ORANGE
PAPER = GRAPHITE
WHITE = (255, 252, 248)
TERM_BG = (27, 28, 32)

AH = 770
LAYER_Y = 90
PACK_DY = 210
BAND_Y = 936
BAND_W, BAND_H = 1056, 960
SAFE_X = (36, 1044)

meta = json.load(open("source/meta.json"))
DUR = float(meta["DUR"])
words = json.load(open("audio/words.json"))
N = int(round(DUR * FPS))


def trel(word, after=0.0):
    for w, a, b in words:
        if a >= after - 0.01 and w.strip().rstrip(".,!?").lower() == word:
            return a
    raise SystemExit(f"word not found: {word} after {after}")


def tend(word, after=0.0):
    for w, a, b in words:
        if a >= after - 0.01 and w.strip().rstrip(".,!?").lower() == word:
            return b
    raise SystemExit(f"word not found: {word} after {after}")

def textured_bg(base, seed, glow=ORANGE):
    rng = np.random.default_rng(seed)
    arr = np.tile(np.array(base, np.float32), (H + 160, W + 160, 1))
    arr += rng.normal(0, 2.4, (H + 160, W + 160, 1))
    arr += rng.normal(0, 6.0, (H + 160, 1, 1)) * 0.22
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    sh = Image.new("L", (W + 160, H + 160), 0)
    d = ImageDraw.Draw(sh)
    for cx, cy, rx, ry in [(180, 220, 460, 300), (720, 980, 480, 340), (540, 80, 360, 220)]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=48)
    sh = sh.filter(ImageFilter.GaussianBlur(90))
    lift = Image.new("RGB", (W + 160, H + 160), tuple(min(255, c + 18) for c in base))
    base_img = Image.composite(lift, img, sh)
    glow_l = Image.new("L", (W + 160, H + 160), 0)
    gd = ImageDraw.Draw(glow_l)
    gd.ellipse([W // 2 - 500, 0, W // 2 + 660, 820], fill=70)
    glow_l = glow_l.filter(ImageFilter.GaussianBlur(140))
    glow_rgb = Image.new("RGB", (W + 160, H + 160), glow)
    return Image.composite(glow_rgb, base_img, glow_l)

def place(frame, img, cx, cy, lt, t0, dur=0.3, frm="up", tilt=0.0, idle=0, scale_pop=False, exit_at=None):
    if img is None:
        return
    p = ease((lt - t0) / dur) if dur else 1.0
    if p <= 0:
        return
    alpha = p
    p2 = 0
    if exit_at is not None:
        q = (lt - exit_at) / 0.22
        if q >= 1:
            return
        if q > 0:
            alpha = min(alpha, 1 - q)
            p2 = ease(q)
    off = 90 * (1 - p)
    dx, dy = {"up": (0, off), "down": (0, -off), "left": (off, 0), "right": (-off, 0)}.get(frm, (0, off))
    dy -= 120 * p2
    im = img
    if scale_pop:
        pop = outp((lt - t0) / max(0.05, dur))
        im = im.resize((max(1, int(im.width * pop)), max(1, int(im.height * pop))), Image.BICUBIC)
    if tilt:
        im = im.rotate(tilt * (1 - p) if p < 1 else 0, expand=True, resample=Image.BICUBIC) if p < 1 else im
    if alpha < 1:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    x = int(cx - im.width / 2 + dx)
    y = int(cy + PACK_DY - im.height / 2 + dy)
    max_w = SAFE_X[1] - SAFE_X[0]
    if im.width <= max_w:
        x = max(SAFE_X[0], min(SAFE_X[1] - im.width, x))
    else:
        x = max(0, min(W - im.width, x))
    y = max(0, min(AH - min(im.height, AH), y))
    frame.alpha_composite(im, (x, y))


def put(layer, img, cx, cy, a=1.0):
    """Direct composite at layer coords (cx, cy = centre)."""
    if img is None or a <= 0:
        return
    if a < 1:
        img = img.copy()
        img.putalpha(img.split()[3].point(lambda v: int(v * a)))
    layer.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


def fade(lt, t0, d=0.16):
    return clamp01((lt - t0) / d)


def _mask(w, h, r):
    def build():
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
        return m
    return cached(("mask", w, h, r), build)


# ───────────────────────────── generic cards ─────────────────────────────

def os_chip(txt, accent=ORANGE, fsz=28):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + 48, fsz + 28
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 8, h], fill=accent + (255,))
        d.text((28, h / 2), txt, font=fnt, fill=SILVER + (255,), anchor="lm")
        return img
    return cached(("oschip", txt, accent, fsz), build)


def title_card(txt, accent=ORANGE, fsz=72, w=960, h=150, fg=WHITE):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 28, fill=GRAPHITE + (255,))
        d.rectangle([0, 0, 14, h], fill=accent + (255,))
        d.text((w / 2 + 6, h / 2 - 2), txt, font=F(AR, fsz), fill=fg + (255,), anchor="mm")
        return img
    return cached(("title", txt, accent, fsz, w, h, fg), build)


def stamp(txt, col=RED, fsz=64, pad=34):
    def build():
        fnt = F(AR, fsz)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=fnt))
        w, h = tw + pad * 2, fsz + 44
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 16, fill=INK + (210,), outline=col + (255,), width=8)
        d.rounded_rectangle([12, 12, w - 13, h - 13], 10, outline=col + (150,), width=2)
        d.text((w / 2, h / 2 - 2), txt, font=fnt, fill=col + (255,), anchor="mm")
        return img
    return cached(("stamp", txt, col, fsz), build)


def ghost_word(text, size=120, alpha=50):
    def build():
        fnt = F(AR, size)
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=fnt))
        img = Image.new("RGBA", (tw + 20, size + 20), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((10, 4), text, font=fnt, fill=SILVER + (alpha,))
        return img
    return cached(("ghost", text, size, alpha), build)


def ghost(layer, txt, size=84):
    gw = ghost_word(txt, size, 40)
    layer.alpha_composite(gw, (W - gw.width - 30, 6))


def big_text(txt, size, col, stroke=6):
    def build():
        fnt = F(AR, size)
        bb = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
        img = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((10 - bb[0], 10 - bb[1]), txt, font=fnt, fill=col + (255,),
                                 stroke_width=stroke, stroke_fill=INK + (255,))
        return img
    return cached(("big", txt, size, col, stroke), build)


def arrow(layer, x0, y0, x1, y1, col, p=1.0, width=10):
    p = clamp01(p)
    if p <= 0:
        return
    d = ImageDraw.Draw(layer)
    ex, ey = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
    d.line([(x0, y0), (ex, ey)], fill=col + (255,), width=width)
    if p >= 1:
        ang = math.atan2(y1 - y0, x1 - x0)
        s_ = 26
        d.polygon([(x1 + math.cos(ang) * 10, y1 + math.sin(ang) * 10),
                   (x1 - math.cos(ang - 0.5) * s_, y1 - math.sin(ang - 0.5) * s_),
                   (x1 - math.cos(ang + 0.5) * s_, y1 - math.sin(ang + 0.5) * s_)], fill=col + (255,))


def flow_dots(layer, x0, y0, x1, y1, lt, col, n=3, speed=1.3, r=9):
    d = ImageDraw.Draw(layer)
    for i in range(n):
        ph = (lt * speed + i / n) % 1.0
        x, y = x0 + (x1 - x0) * ph, y0 + (y1 - y0) * ph
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,), outline=WHITE + (255,), width=2)


def ripple(layer, x, y, age, col=NEON, r0=14, r1=64, dur=0.4):
    if not 0 <= age < dur:
        return
    p = age / dur
    r = r0 + (r1 - r0) * p
    a = int(255 * (1 - p))
    d = ImageDraw.Draw(layer)
    d.ellipse([x - r, y - r, x + r, y + r], outline=col + (a,), width=6)


# ───────────────────────────── brand marks ─────────────────────────────

def badge_img(img, size, fill=GRAPHITE):
    def build():
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(out).rounded_rectangle([0, 0, size - 1, size - 1], int(size * 0.22), fill=fill + (255,))
        k = int(size * 0.74)
        im = img.copy()
        im.thumbnail((k, k), Image.LANCZOS)
        out.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
        return out
    return cached(("badgeimg", id(img), size, fill), build)


def _logo(slug):
    return cached(("logo", slug), lambda: Image.open(f"assets/logos/{slug}.png").convert("RGBA"))



# ───────────────────────────── this edit ─────────────────────────────

from hyper_edits import ease_back_out, punch_beats  # noqa: E402
from apple_counter import apple_counter  # noqa: E402
from media_marks import logo_badge, logo_mark, topic_marks  # noqa: E402

BLUE = (64, 140, 255)
XGREEN = (48, 209, 88)
GIPHY_COLS = [(0, 255, 153), (153, 51, 255), (0, 204, 255), (255, 243, 92), (255, 102, 102)]
T = trel


def hit(t_word):
    """Payoff lands in the pause: if >=0.35 s of silence precedes the word, start at the silence."""
    prev = max((b for w, a, b in words if b <= t_word + 0.001 and a < t_word - 0.001), default=0.0)
    return prev if t_word - prev >= 0.35 else t_word - 0.05


# word anchors (cut timeline)
T_CLAUDE = T("claude"); T_EDITING = T("editing"); T_VIDEOS = T("videos"); T_SOCIALS = T("socials")
T_TAKEN = T("taken"); T_OFF = T("off")
T_AND1 = T("and", 4.0); T_THIS = T("this", 4.3); T_STYLE = T("style"); T_RIGHT = T("right"); T_NUMBER = T("number")
T_ONE_END = tend("one", 6.5); T_INSTA = T("instagram"); T_CALLED = T("called"); T_KEVS = T("kev's")
T_TALKING = T("talking"); T_HEAD = T("head"); T_EDITOR = T("editor")
T_HERES = T("here's"); T_GRAB = T("grab"); T_TRANSCRIPT = T("transcript"); T_CONCEPT = T("concept")
T_ITLL2 = T("it'll", 14.0); T_GIPHY = T("giphy"); T_API = T("api"); T_BEST = T("best"); T_GIFS = T("gifs")
T_MEMES = T("memes"); T_INTERNET = T("internet"); T_RELATED = T("related")
T_AND3 = T("and", 19.9); T_SYNC = T("sync"); T_SAYING = T("saying"); T_CAPTIONS = T("captions")
T_VIDEO4 = T("video", 24.5); T_EDITS = T("edits")
T_THE5 = T("the", 26.5); T_ANIM = T("animations"); T_TEXT = T("text"); T_LOGOS = T("logos")
T_THATS = T("that's"); T_ENTERTAINING = T("entertaining"); T_ALGO = T("algorithm"); T_WATCH = T("watch", 36)
T_HIGH = T("high")
T_AND7 = T("and", 37.5); T_ACCESS = T("access"); T_SKILL = T("skill"); T_FREE = T("free"); T_COMMENT = T("comment")
T_EDITW = T("edit", 40.6)

H_ENT = hit(T_ENTERTAINING)

SECT = [
    ("hook", 0.00, T_AND1),
    ("style", T_AND1, T_HERES),
    ("how", T_HERES, T_ITLL2),
    ("giphy", T_ITLL2, T_AND3),
    ("sync", T_AND3, T_THE5),
    ("list", T_THE5, T_THATS),
    ("result", T_THATS, T_AND7),
    ("cta", T_AND7, DUR + 0.05),
]
KEY_COL = {
    "claude": ORANGE, "editing": CYAN, "videos": CYAN, "socials": PINK, "taken": NEON, "off": NEON,
    "style": CYAN, "number": GOLD, "one": GOLD, "instagram": PINK, "kev's": NEON, "talking": NEON, "head": NEON,
    "editor": NEON, "transcript": CYAN, "concept": CYAN, "giphy": PURPLE, "api": PURPLE, "gifs": PURPLE,
    "memes": PURPLE, "internet": PURPLE, "related": XGREEN, "sync": NEON, "captions": GOLD, "edits": GOLD,
    "animations": ORANGE, "text": ORANGE, "logos": ORANGE, "entertaining": PINK, "algorithm": CYAN,
    "watch": NEON, "time": NEON, "high": NEON, "skill": ORANGE, "free": NEON, "comment": NEON, "edit": NEON,
}
KEYWORDS = set(KEY_COL)
SECT_ACCENT = {"hook": NEON, "style": CYAN, "how": CYAN, "giphy": PURPLE, "sync": NEON, "list": ORANGE,
               "result": PINK, "cta": NEON}
BGS = {
    "hook": textured_bg((34, 48, 42), 7, NEON),
    "style": textured_bg((34, 44, 52), 11, CYAN),
    "how": textured_bg((34, 44, 52), 19, CYAN),
    "giphy": textured_bg((42, 36, 54), 13, PURPLE),
    "sync": textured_bg((34, 48, 42), 29, NEON),
    "list": textured_bg((50, 40, 32), 31, ORANGE),
    "result": textured_bg((50, 34, 44), 37, PINK),
    "cta": textured_bg((34, 48, 44), 53, NEON),
}

LIGHT_TILE = (244, 244, 247)


def mark(slug, size):
    if slug == "claude-invader":
        return badge_img(_logo("claude-invader"), size)
    if slug == "sphinx":
        return badge_img(load_sphinx(size), size)
    if slug == "giphy":
        return giphy_badge(size)
    if slug == "creatoros":
        return badge_img(_logo("creatoros"), size, GRAPHITE)
    return badge_img(_logo(slug), size, LIGHT_TILE)


def giphy_mark(size):
    """GIPHY bracket mark, drawn from the simple-icons path in its five brand colours."""
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        k = size / 24
        g, p, b, y, r = GIPHY_COLS
        R = lambda x0, y0, x1, y1, c: d.rectangle([x0 * k + 1.5 * k, y0 * k, x1 * k + 1.5 * k, y1 * k], fill=c + (255,))
        R(2.666 - 1.5, 0, 5.334 - 1.5, 24, g)
        R(2.666 - 1.5, 21.332, 21.334 - 1.5, 24, p)
        R(18.666 - 1.5, 8.666, 21.334 - 1.5, 24, b)
        R(2.666 - 1.5, 0, 12.0 - 1.5, 2.668, y)
        R(13.334 - 1.5, 0, 16.0 - 1.5, 8.0, r)
        R(16.0 - 1.5, 2.668, 18.666 - 1.5, 5.334, r)
        R(18.666 - 1.5, 5.334, 21.334 - 1.5, 8.0, r)
        return img
    return cached(("giphy", size), build)


def giphy_badge(size):
    def build():
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(out).rounded_rectangle([0, 0, size - 1, size - 1], int(size * 0.22), fill=(18, 18, 20, 255))
        m = giphy_mark(int(size * 0.62))
        out.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
        return out
    return cached(("giphyb", size), build)


def giphy_wordmark(h=150):
    def build():
        mk = giphy_mark(h)
        fnt = F(AR, int(h * 0.95))
        tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength("GIPHY", font=fnt))
        img = Image.new("RGBA", (h + 30 + tw + 10, h + 10), (0, 0, 0, 0))
        img.alpha_composite(mk, (0, 5))
        ImageDraw.Draw(img).text((h + 30, h / 2 + 5), "GIPHY", font=fnt, fill=WHITE + (255,), anchor="lm")
        return img
    return cached(("giphyw", h), build)


def lane_marks(size=120):
    return cached(("lane", size), lambda: [mark(s, size) for s in
                                           ["claude-invader", "instagram", "giphy", "tiktok", "sphinx", "youtube",
                                            "creatoros"]])


def lane(layer, lt, y=488, size=120):
    guarded_conveyor(layer, y + PACK_DY, max(0, lt), lane_marks(size), conveyor_marks, name="lane", speed=200, gap=22)


def check_badge(size=54, col=NEON):
    def build():
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([0, 0, size - 1, size - 1], fill=col + (255,), outline=INK + (255,), width=4)
        d.line([(size * 0.27, size * 0.52), (size * 0.44, size * 0.68), (size * 0.74, size * 0.34)], fill=INK + (255,),
               width=max(4, size // 9), joint="curve")
        return img
    return cached(("check", size, col), build)


def scaled(img, k):
    if img is None or abs(k - 1) < 0.01:
        return img
    return img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.BICUBIC)


# ── video player card (hook atmosphere, frame 0) ──
def video_card(lt, w=900, h=520, accent=NEON, label="MY_VIDEO.mp4", edited=0.0):
    q = int(lt * 10) % 200
    e = int(clamp01(edited) * 10)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=TERM_BG + (250,), outline=accent + (255,), width=4)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse([22 + i * 26, 20, 38 + i * 26, 36], fill=c + (255,))
        d.text((120, 28), label, font=F(AR, 28), fill=SILVER + (255,), anchor="lm")
        sx0, sy0, sx1, sy1 = 30, 60, w - 30, h - 90
        d.rounded_rectangle([sx0, sy0, sx1, sy1], 16, fill=(18, 19, 23, 255))
        # edited picture: coloured split (animation slot over a band)
        if e:
            mid = sy0 + (sy1 - sy0) * 0.55
            d.rounded_rectangle([sx0 + 14, sy0 + 14, sx1 - 14, mid - 6], 10, fill=(40, 44, 54, 255))
            for k in range(min(e, 6)):
                cx = sx0 + 80 + k * (sx1 - sx0 - 160) / 5
                d.rounded_rectangle([cx - 46, sy0 + 50, cx + 46, sy0 + 142], 14,
                                    fill=GIPHY_COLS[k % 5] + (255,))
            d.rounded_rectangle([sx0 + 14, mid + 6, sx1 - 14, sy1 - 14], 10, fill=(70, 74, 86, 255))
        cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2 + (40 if e else 0)
        d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=WHITE + (235,))
        d.polygon([(cx - 20, cy - 32), (cx - 20, cy + 32), (cx + 36, cy)], fill=INK + (255,))
        d.rounded_rectangle([30, h - 56, w - 30, h - 44], 6, fill=(60, 62, 72, 255))
        px = 30 + (w - 60) * (q / 200)
        d.rounded_rectangle([30, h - 56, px, h - 44], 6, fill=accent + (255,))
        d.ellipse([px - 12, h - 62, px + 12, h - 38], fill=WHITE + (255,))
        return img
    return cached(("vid", q, e, w, h, accent, label), build)


# ── growth arrow chart (taken off / watch time) ──
def chart_card(p, w=960, h=430, col=NEON, title="FOLLOWERS", sub=""):
    q = int(clamp01(p) * 80)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=TERM_BG + (245,), outline=SILVER + (120,), width=3)
        d.text((30, 36), title, font=F(AR, 34), fill=SILVER + (255,), anchor="lm")
        if sub:
            d.text((w - 30, 36), sub, font=F(AR, 28), fill=col + (255,), anchor="rm")
        x0, y0, x1, y1 = 70, h - 50, w - 40, 80
        for k in range(5):
            yy = y0 - (y0 - y1) * k / 4
            d.line([(x0, yy), (x1, yy)], fill=STEEL + (90,), width=2)
        d.line([(x0, y0), (x1, y0)], fill=SILVER + (255,), width=4)
        d.line([(x0, y0), (x0, y1 - 10)], fill=SILVER + (255,), width=4)
        pts = []
        for i in range(q + 1):
            u = i / 80
            v = 0.06 + 0.94 * (math.exp(u * 3.6) - 1) / (math.exp(3.6) - 1)
            pts.append((x0 + (x1 - x0) * u * 0.9, y0 - (y0 - y1) * v))
        if len(pts) > 1:
            poly = pts + [(pts[-1][0], y0), (pts[0][0], y0)]
            d.polygon(poly, fill=col + (40,))
            d.line(pts, fill=col + (255,), width=10, joint="curve")
            d.ellipse([pts[-1][0] - 14, pts[-1][1] - 14, pts[-1][0] + 14, pts[-1][1] + 14], fill=WHITE + (255,))
        return img
    return cached(("chart", q, w, h, col, title, sub), build)


# ── the split-format mock: "this editing style that you're seeing" ──
def phone_mock(lt, w=330, h=600, live=True):
    q = int(lt * 8) % 40

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 46, fill=(14, 15, 18, 255), outline=SILVER + (255,), width=6)
        sx0, sy0, sx1, sy1 = 16, 16, w - 16, h - 16
        d.rounded_rectangle([sx0, sy0, sx1, sy1], 34, fill=(48, 50, 58, 255))
        mid = sy0 + (sy1 - sy0) * 0.48
        for k in range(3):
            cx = sx0 + 60 + k * (sx1 - sx0 - 120) / 2
            yy = sy0 + 90 + 26 * math.sin(q / 40 * 2 * math.pi + k)
            d.rounded_rectangle([cx - 36, yy - 36, cx + 36, yy + 36], 12, fill=GIPHY_COLS[k + 1] + (255,))
        d.rounded_rectangle([sx0 + 20, sy0 + 170, sx1 - 20, sy0 + 210], 10, fill=GRAPHITE + (255,))
        d.rectangle([sx0 + 20, sy0 + 170, sx0 + 28, sy0 + 210], fill=CYAN + (255,))
        d.rectangle([sx0 + 16, mid - 4, sx1 - 16, mid], fill=CYAN + (255,))
        d.text(((sx0 + sx1) / 2, mid - 14), "CAPTIONS", font=F(CAP, 34), fill=WHITE + (255,), anchor="ls",
               stroke_width=3, stroke_fill=(0, 0, 0, 255))
        d.rounded_rectangle([sx0 + 8, mid + 6, sx1 - 8, sy1 - 8], 22, fill=(176, 132, 96, 255))
        hx, hy = (sx0 + sx1) / 2, mid + 110
        d.ellipse([hx - 52, hy - 60, hx + 52, hy + 60], fill=(226, 180, 150, 255))
        d.chord([hx - 58, hy - 76, hx + 58, hy + 10], 180, 360, fill=(26, 28, 34, 255))
        d.pieslice([hx - 110, hy + 60, hx + 110, hy + 260], 180, 360, fill=(220, 168, 136, 255))
        if live and q % 20 < 14:
            d.ellipse([sx1 - 74, sy0 + 18, sx1 - 56, sy0 + 36], fill=RED + (255,))
            d.text((sx1 - 50, sy0 + 27), "LIVE", font=F(AR, 20), fill=WHITE + (255,), anchor="lm")
        return img
    return cached(("phone", q, w, h, live), build)


# ── transcript doc with a reading beam ──
TRANSCRIPT = ["ever since claude has been editing", "my videos, my socials have just", "been taken off. this editing",
              "style is my number one style", "on instagram, called kev's", "talking head editor ..."]


def transcript_card(n, scan=-1.0, w=960, h=430, accent=CYAN):
    total = sum(len(x) for x in TRANSCRIPT)
    n = min(int(n), total)
    sc = int(scan * 40) if scan >= 0 else -1

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=(250, 249, 245, 255))
        d.rounded_rectangle([0, 0, w - 1, 64], 24, fill=(30, 32, 38, 255))
        d.rectangle([0, 40, w - 1, 64], fill=(30, 32, 38, 255))
        d.text((28, 33), "transcript.txt", font=F(ML, 28), fill=WHITE + (255,), anchor="lm")
        d.text((w - 28, 33), "WHISPER", font=F(AR, 26), fill=accent + (255,), anchor="rm")
        left, y = n, 96
        for ln in TRANSCRIPT:
            if left <= 0:
                break
            d.text((34, y), ln[:left], font=F(ML, 34), fill=INK + (255,))
            left -= len(ln)
            y += 54
        if sc >= 0:
            yy = 86 + (h - 110) * sc / 40
            ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(ov).rectangle([20, 80, w - 20, yy], fill=accent + (60,))
            img.alpha_composite(ov)
            ImageDraw.Draw(img).rectangle([20, yy - 3, w - 20, yy + 3], fill=accent + (255,))
        return img
    return cached(("tx", n, sc, w, h, accent), build)


TX_TOTAL = sum(len(x) for x in TRANSCRIPT)


def term_card(lines, n, title="terminal", w=960, h=220, accent=PURPLE):
    total = sum(len(x) for x, _ in lines)
    n = min(n, total)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=TERM_BG + (255,), outline=accent + (255,), width=3)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse([20 + i * 24, 18, 34 + i * 24, 32], fill=c + (255,))
        d.text((110, 25), title, font=F(AR, 26), fill=SILVER + (255,), anchor="lm")
        left, y = n, 58
        for ln, col in lines:
            if left <= 0:
                break
            d.text((26, y), ln[:left], font=F(ML, 30), fill=col + (255,))
            left -= len(ln)
            y += 46
        return img
    return cached(("term", id(lines), n, w, h, accent), build)


API_LINES = [
    ("GET api.giphy.com/v1/gifs/search", WHITE),
    ("  ?q=taken+off&rating=pg-13", PURPLE),
    ("  200 OK   25 gifs matched", NEON),
]
API_TOTAL = sum(len(x) for x, _ in API_LINES)


# ── NLE timeline: voice / gifs / captions / edits ──
_wr = np.random.default_rng(9)
WAVE = np.abs(_wr.normal(0, 1, 160)) * 0.6 + 0.25
TRACKS = [("VOICE", CYAN), ("GIFS", PURPLE), ("CAPTIONS", GOLD), ("EDITS", NEON)]
GIF_CLIPS = [(0.06, 0.20), (0.30, 0.44), (0.55, 0.66), (0.78, 0.92)]
CAP_CLIPS = [(0.03 + k * 0.062, 0.03 + k * 0.062 + 0.05) for k in range(15)]
EDIT_MARKS = [0.12, 0.27, 0.41, 0.52, 0.63, 0.74, 0.86]


def timeline_card(lt, snap=0.0, cap_on=0.0, edit_on=0.0, hot=None, w=980, h=470):
    ph = int((lt * 0.12 % 1.0) * 120)
    sn, cn, en = int(clamp01(snap) * 12), int(clamp01(cap_on) * 15), int(clamp01(edit_on) * 7)

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=TERM_BG + (250,), outline=NEON + (255,), width=3)
        d.text((28, 34), "KEV'S TALKING HEAD EDITOR", font=F(AR, 30), fill=SILVER + (255,), anchor="lm")
        d.text((w - 28, 34), "AUTO SYNC", font=F(AR, 28), fill=NEON + (255,), anchor="rm")
        x0, x1 = 190, w - 26
        tw_ = x1 - x0
        for i, (nm, col) in enumerate(TRACKS):
            y = 74 + i * 96
            on = hot == nm
            d.rounded_rectangle([18, y, 176, y + 80], 12, fill=(col if on else GRAPHITE) + (255,))
            d.text((97, y + 40), nm, font=F(AR, 26), fill=(INK if on else SILVER) + (255,), anchor="mm")
            d.rounded_rectangle([x0, y, x1, y + 80], 12, fill=(34, 36, 44, 255))
            if nm == "VOICE":
                for k, v in enumerate(WAVE):
                    xx = x0 + 8 + k * (tw_ - 16) / len(WAVE)
                    d.line([(xx, y + 40 - v * 30), (xx, y + 40 + v * 30)], fill=col + (255,), width=3)
            elif nm == "GIFS":
                for k, (a_, b_) in enumerate(GIF_CLIPS):
                    off = 0 if sn >= 3 * (k + 1) else (1 - sn / (3 * (k + 1))) * 260
                    if sn == 0:
                        continue
                    d.rounded_rectangle([x0 + a_ * tw_ + off, y + 8, x0 + b_ * tw_ + off, y + 72], 10,
                                        fill=GIPHY_COLS[k] + (255,))
            elif nm == "CAPTIONS":
                for k, (a_, b_) in enumerate(CAP_CLIPS[:cn]):
                    d.rounded_rectangle([x0 + a_ * tw_, y + 18, x0 + b_ * tw_, y + 62], 8, fill=col + (255,))
            else:
                for k, m_ in enumerate(EDIT_MARKS[:en]):
                    xx = x0 + m_ * tw_
                    d.polygon([(xx, y + 14), (xx + 18, y + 40), (xx, y + 66), (xx - 18, y + 40)], fill=col + (255,))
        px = x0 + tw_ * ph / 120
        d.rectangle([px - 2, 64, px + 2, h - 16], fill=RED + (255,))
        d.polygon([(px - 14, 58), (px + 14, 58), (px, 76)], fill=RED + (255,))
        return img
    return cached(("tl", ph, sn, cn, en, hot, w, h), build)


ITEMS = ["ANIMATIONS", "TEXT ON SCREEN", "LOGOS"]


def checklist(n_done, w=470, h=300):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=GRAPHITE + (250,))
        d.rectangle([0, 0, 10, h], fill=ORANGE + (255,))
        d.text((w - 26, 36), f"{n_done}/3", font=F(AR, 40), fill=ORANGE + (255,), anchor="rm")
        d.text((34, 36), "AUTO", font=F(AR, 34), fill=STEEL + (255,), anchor="lm")
        for i, tx in enumerate(ITEMS):
            y = 110 + i * 70
            if i < n_done:
                img.alpha_composite(check_badge(50, ORANGE), (30, y - 25))
            else:
                d.ellipse([30, y - 25, 80, y + 25], outline=STEEL + (255,), width=4)
            d.text((100, y), tx, font=F(AR, 38), fill=(WHITE if i < n_done else SILVER) + (255,), anchor="lm")
        return img
    return cached(("cl", n_done, w, h), build)


def comment_card(word, tt, w=600, h=250):
    n = int(clamp01(tt / 0.3) * len(word))
    replied = tt > 0.45

    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(250, 250, 252, 255))
        d.ellipse([24, 26, 84, 86], fill=NEON + (255,))
        d.text((54, 56), "U", font=F(AR, 34), fill=INK + (255,), anchor="mm")
        d.text((104, 40), "you", font=F(AR, 26), fill=STEEL + (255,), anchor="lm")
        d.text((104, 80), word[:n], font=F(AR, 46), fill=INK + (255,), anchor="lm")
        if replied:
            d.line([(54, 96), (54, 160), (96, 160)], fill=(200, 202, 210, 255), width=4)
            d.ellipse([104, 132, 156, 184], fill=ORANGE + (255,))
            d.text((130, 158), "K", font=F(AR, 30), fill=WHITE + (255,), anchor="mm")
            d.text((172, 142), "kevbuildsapps", font=F(AR, 24), fill=STEEL + (255,), anchor="lm")
            d.text((172, 180), "Sent! Check your DMs", font=F(AR, 34), fill=INK + (255,), anchor="lm")
        return img
    return cached(("ccard", word, n, replied, w, h), build)



def skill_file(w=440, h=170):
    def build():
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=(217, 119, 87, 255), outline=INK + (255,), width=5)
        fx, fy, fw, fh = 26, 24, int(h * 0.62), h - 48
        d.polygon([(fx, fy), (fx + fw - 26, fy), (fx + fw, fy + 26), (fx + fw, fy + fh), (fx, fy + fh)],
                  fill=(250, 249, 245, 255))
        for k in range(4):
            d.rectangle([fx + 14, fy + 42 + k * 18, fx + fw - 16 - (k % 2) * 20, fy + 50 + k * 18], fill=STEEL + (255,))
        d.text((fx + fw + 26, h / 2), "SKILL.md", font=F(AR, int(h * 0.42)), fill=WHITE + (255,), anchor="lm",
               stroke_width=3, stroke_fill=INK + (255,))
        return img
    return cached(("skillfile", w, h), build)


# ───────────────────────────── scenes ─────────────────────────────

def hook(layer, lt, a):
    """Frame 0: a giant video player already up. Claude lands on its word and grabs the file."""
    if lt < T_SOCIALS - 0.05:
        ex = T_SOCIALS - 0.12
        bloom_orb(layer, 540, 330, 320, NEON, a=70)
        ed = clamp01((lt - T_EDITING) / 0.9) if lt >= T_EDITING else 0.0
        place(layer, video_card(lt, w=760, h=470, edited=ed), 620, 150, lt, -0.4, dur=0.01, exit_at=ex)
        place(layer, os_chip("EVER SINCE", SILVER, 52), 620, -150, lt, -0.4, dur=0.01, exit_at=T_CLAUDE - 0.08)
        if lt >= T_CLAUDE - 0.05:
            bloom_orb(layer, 190, 260, 200, ORANGE, a=90)
            gt = clamp01((lt - T_EDITING) / 0.5) if lt >= T_EDITING else 0.0
            place_claude_invader(layer, 190, 250 + PACK_DY, lt, size=300, look_at=(620, 360),
                                 grab="right", grab_at=(400, 300), grab_t=gt * 0.6)
            place(layer, stamp("CLAUDE EDITS IT", ORANGE, 70, pad=30), 620, -150, lt, T_CLAUDE - 0.05, dur=0.12,
                  frm="down", scale_pop=True, exit_at=ex)
            place_claude_sphinx(layer, 175, 470 + PACK_DY, lt, size=150)
        return
    if lt < T_TAKEN - 0.05:
        ghost(layer, "MY SOCIALS")
        for k, (slug, cx) in enumerate([("instagram", 200), ("tiktok", 540), ("youtube", 880)]):
            t0 = T_SOCIALS - 0.05 + k * 0.1
            place(layer, mark(slug, 300), cx, 150, lt, t0, dur=0.12, frm=["left", "up", "right"][k], scale_pop=True,
                  exit_at=T_TAKEN - 0.1)
        place(layer, os_chip("MY SOCIALS", PINK, 56), 540, -130, lt, T_SOCIALS, dur=0.14, frm="down",
              exit_at=T_TAKEN - 0.1)
        lane(layer, lt)
        return
    ghost(layer, "TAKEN OFF")
    p = clamp01((lt - T_TAKEN) / 0.6)
    place(layer, chart_card(p, w=600, h=430, title="REACH", col=NEON), 360, 160, lt, T_TAKEN - 0.05, dur=0.12,
          frm="left", scale_pop=True)
    place(layer, gif_card("rocket", lt - T_TAKEN, w=400, frame="round"), 830, 150, lt, T_TAKEN - 0.05, dur=0.12,
          frm="right", scale_pop=True)
    place(layer, stamp("TAKEN OFF", NEON, 96, pad=34), 540, 455, lt, T_OFF - 0.05, dur=0.12, frm="up", scale_pop=True)
    light_hit(layer, 540, 455 + PACK_DY, lt, T_OFF - 0.05, NEON)


def style(layer, lt, a):
    tt, tr, tn, toe, ti, tc = T_THIS - a, T_RIGHT - a, T_NUMBER - a, T_ONE_END - a, T_INSTA - a, T_CALLED - a
    tk, tta, th, te = T_KEVS - a, T_TALKING - a, T_HEAD - a, T_EDITOR - a
    if lt < ti - 0.05:
        ghost(layer, "THIS EDIT")
        ex = ti - 0.12
        place(layer, phone_mock(lt + a, live=lt >= tr - 0.05), 270, 160, lt, -0.05, dur=0.14, frm="left",
              scale_pop=True, exit_at=ex)
        place(layer, os_chip("THIS EDITING STYLE", CYAN, 44), 740, -150, lt, tt - 0.05, dur=0.14, frm="down",
              exit_at=ex)
        if lt >= tr - 0.05:
            place(layer, os_chip("YOU'RE WATCHING IT", RED, 40), 740, -40, lt, tr - 0.05, dur=0.14, frm="right",
                  exit_at=ex)
        if lt >= tn - 0.05:
            p = clamp01((lt - tn) / max(0.2, toe - tn))
            cnt = apple_counter({"value": 1, "prefix": "#"}, p, w=500, h=320, label="STYLE I USE", accent=GOLD)
            place(layer, cnt, 740, 230, lt, tn - 0.05, dur=0.12, frm="up", scale_pop=True, exit_at=ex)
        return
    if lt < tc - 0.05:
        ghost(layer, "INSTAGRAM")
        bloom_orb(layer, 540, 300, 280, PINK, a=90)
        place(layer, mark("instagram", 420), 540, 140, lt, ti - 0.05, dur=0.12, frm="up", scale_pop=True,
              exit_at=tc - 0.1)
        place(layer, os_chip("MY #1 STYLE ON", SILVER, 46), 540, -165, lt, ti - 0.05, dur=0.14, frm="down",
              exit_at=tc - 0.1)
        return
    # the one kinetic word of the video: the product name fills the slot
    bloom_orb(layer, 540, 300, 380, NEON, a=70)
    place(layer, os_chip("IT'S CALLED", SILVER, 44), 540, -175, lt, tc - 0.05, dur=0.14, frm="down")
    for txt, t0, cy, col, hh in [("KEV'S", tk, 70, WHITE, 190), ("TALKING HEAD", tta, 270, NEON, 190),
                                 ("EDITOR", te, 470, WHITE, 190)]:
        if lt < t0 - 0.05:
            continue
        pp = outp(clamp01((lt - t0 + 0.05) / 0.16))
        word = big_text(txt, 230, col, stroke=10)
        tgt = min((1040 + 30 * clamp01((lt - t0) / 1.0)) / word.width, hh / word.height)
        put(layer, scaled(word, tgt * (0.7 + 0.3 * pp)), 540, cy + PACK_DY - 60)
    light_hit(layer, 540, 270 + PACK_DY - 60, lt, tta - 0.05, NEON)


def how(layer, lt, a):
    tg, ttr, tco = T_GRAB - a, T_TRANSCRIPT - a, T_CONCEPT - a
    ghost(layer, "STEP 1")
    place(layer, os_chip("HERE'S HOW IT WORKS", SILVER, 46), 600, -170, lt, -0.05, dur=0.14, frm="down")
    place(layer, title_card("1", CYAN, fsz=70, w=110, h=100), 110, -170, lt, -0.05, dur=0.14, frm="left")
    if lt < tg - 0.05:
        lane(layer, lt)
        bloom_orb(layer, 540, 300, 220, ORANGE, a=70)
        place_claude_invader(layer, 540, 330 + PACK_DY - 60, lt, size=260, look_at=(540, 600))
        return
    n = clamp01((lt - tg) / 2.2) * TX_TOTAL
    sc = clamp01((lt - tco) / 0.9) if lt >= tco - 0.05 else -1.0
    place(layer, transcript_card(max(1, n), scan=sc, w=760, h=430), 600, 140, lt, tg - 0.05, dur=0.14, frm="right",
          scale_pop=True)
    bloom_orb(layer, 120, 230, 140, ORANGE, a=70)
    place_claude_invader(layer, 120, 260 + PACK_DY, lt, size=190, look_at=(500, 360))
    if lt >= ttr - 0.05:
        place(layer, os_chip("ENTIRE TRANSCRIPT", CYAN, 42), 600, 410, lt, ttr - 0.05, dur=0.14, frm="up",
              exit_at=tco - 0.1)
    if lt >= tco - 0.05:
        place(layer, stamp("GETS THE CONCEPT", CYAN, 70, pad=30), 600, 420, lt, tco - 0.05, dur=0.12, frm="up",
              scale_pop=True)


def giphy(layer, lt, a):
    tgp, tap, tgf, tme, tin, tre = T_GIPHY - a, T_API - a, T_GIFS - a, T_MEMES - a, T_INTERNET - a, T_RELATED - a
    place(layer, title_card("2", PURPLE, fsz=70, w=110, h=100), 110, -170, lt, -0.05, dur=0.14, frm="left")
    if lt < tgf - 0.05:
        ghost(layer, "GIPHY API")
        ex = tgf - 0.12
        if lt < tgp - 0.05:
            lane(layer, lt)
            place(layer, os_chip("THEN IT USES", SILVER, 52), 600, -170, lt, -0.05, dur=0.14, frm="down",
                  exit_at=tgp - 0.1)
            return
        bloom_orb(layer, 540, 200, 300, PURPLE, a=90)
        place(layer, giphy_wordmark(200), 560, 60, lt, tgp - 0.05, dur=0.12, frm="up", scale_pop=True, exit_at=ex)
        light_hit(layer, 540, 60 + PACK_DY, lt, tgp - 0.05, PURPLE)
        if lt >= tap - 0.05:
            n = int(clamp01((lt - tap) / 1.0) * API_TOTAL)
            place(layer, term_card(API_LINES, max(1, n), title="giphy api"), 540, 340, lt, tap - 0.05, dur=0.14,
                  frm="up", exit_at=ex)
        return
    ghost(layer, "BEST GIFS")
    place(layer, giphy_badge(110), 260, -170, lt, tgf - 0.05, dur=0.12, frm="left")
    place(layer, os_chip("THE BEST GIFS + MEMES", PURPLE, 44), 680, -170, lt, tgf - 0.05, dur=0.14, frm="down")
    for k, (slug, cx, t0) in enumerate([("lets-go", 200, tgf), ("wire-wow", 540, tme), ("this-is-fine", 880, tin)]):
        if lt >= t0 - 0.05:
            frm = ["left", "up", "right"][k]
            place(layer, gif_card(slug, lt - t0, w=320, frame="round"), cx, 150, lt, t0 - 0.05, dur=0.12, frm=frm,
                  scale_pop=True)
            if lt >= tre - 0.05 + k * 0.1:
                put(layer, check_badge(70, XGREEN), cx + 130, 150 + PACK_DY - 100, a=fade(lt, tre - 0.05 + k * 0.1))
    if lt >= tre - 0.05:
        place(layer, stamp("MATCHED TO WHAT I SAY", XGREEN, 64, pad=28), 540, 420, lt, tre - 0.05, dur=0.12, frm="up",
              scale_pop=True)


def sync(layer, lt, a):
    tsy, tsa, tca, tvi, ted = T_SYNC - a, T_SAYING - a, T_CAPTIONS - a, T_VIDEO4 - a, T_EDITS - a
    place(layer, title_card("3", NEON, fsz=70, w=110, h=100), 110, -170, lt, -0.05, dur=0.14, frm="left")
    ghost(layer, "AUTO SYNC")
    snap = clamp01((lt - tsy) / 1.2) if lt >= tsy else 0.0
    cap_on = clamp01((lt - tca) / 0.8) if lt >= tca else 0.0
    ed_on = clamp01((lt - tvi) / 1.0) if lt >= tvi else 0.0
    hot = "EDITS" if lt >= tvi else "CAPTIONS" if lt >= tca else "GIFS" if lt >= tsy else "VOICE"
    place(layer, timeline_card(lt + a, snap, cap_on, ed_on, hot), 540, 190, lt, -0.05, dur=0.14, frm="up",
          scale_pop=True)
    if lt < tca - 0.05:
        place(layer, os_chip("SYNCS IT TO MY VOICE", NEON, 44), 600, -170, lt, tsy - 0.05, dur=0.14, frm="down",
              exit_at=tca - 0.1)
        return
    place(layer, os_chip("+ CAPTIONS + EDITS", GOLD, 46), 600, -170, lt, tca - 0.05, dur=0.14, frm="down")
    if lt >= ted - 0.05:
        place(layer, stamp("ALL AUTOMATIC", NEON, 70, pad=30), 540, 470, lt, ted - 0.05, dur=0.12, frm="up",
              scale_pop=True)


def list_(layer, lt, a):
    tan, ttx, tlo = T_ANIM - a, T_TEXT - a, T_LOGOS - a
    nd = (lt >= tan - 0.05) + (lt >= ttx - 0.05) + (lt >= tlo - 0.05)
    place(layer, checklist(nd), 290, 90, lt, -0.05, dur=0.14, frm="left", scale_pop=True)
    if lt < ttx - 0.05:
        ghost(layer, "ANIMATIONS")
        bloom_orb(layer, 790, 300, 220, ORANGE, a=80)
        for k in range(3):
            ang = lt * 2.2 + k * 2.094
            put(layer, mark(["claude-invader", "giphy", "instagram"][k], 130),
                790 + 150 * math.cos(ang), 90 + PACK_DY + 120 * math.sin(ang), a=fade(lt, tan - 0.05 + k * 0.08))
        place_claude_sphinx(layer, 790, 90 + PACK_DY, lt, size=150)
        return
    if lt < tlo - 0.05:
        ghost(layer, "TEXT")
        pp = outp(clamp01((lt - ttx + 0.05) / 0.16))
        for k, (txt, col) in enumerate([("TEXT", ORANGE), ("ON", WHITE), ("SCREEN", ORANGE)]):
            w_ = big_text(txt, 150, col, stroke=8)
            if lt >= ttx - 0.05 + k * 0.12:
                put(layer, scaled(w_, min(1.0, 420 / w_.width) * (0.75 + 0.25 * pp)), 790, PACK_DY - 40 + k * 140)
        return
    ghost(layer, "LOGOS")
    for k, (slug, cx, cy) in enumerate([("claude-invader", 690, 0), ("instagram", 890, 0), ("giphy", 690, 190),
                                        ("youtube", 890, 190)]):
        place(layer, mark(slug, 170), cx, cy, lt, tlo - 0.05 + k * 0.07, dur=0.12, frm=["up", "right", "left",
                                                                                          "down"][k], scale_pop=True)
    lane(layer, lt - tlo, y=430)


def result(layer, lt, a):
    te, tal, tw, th = H_ENT - a, T_ALGO - a, T_WATCH - a, T_HIGH - a
    if lt < tal - 0.05:
        ex = tal - 0.12
        if lt < te:
            ghost(layer, "THAT'S WHY")
            place(layer, video_card(lt + a, w=760, h=440, edited=1.0, accent=PINK, label="EDITED.mp4"), 540, 160, lt,
                  -0.05, dur=0.14, frm="up", scale_pop=True, exit_at=te - 0.06)
            place(layer, os_chip("THAT'S WHAT MAKES THE VIDEOS", SILVER, 42), 540, -170, lt, -0.05, dur=0.14,
                  frm="down", exit_at=te - 0.06)
            return
        ghost(layer, "ENTERTAINING")
        place(layer, gif_card("popcorn", lt - te, w=520, frame="round"), 540, 130, lt, te, dur=0.12, frm="down",
              scale_pop=True, exit_at=ex)
        place(layer, stamp("SO ENTERTAINING", PINK, 80, pad=30), 540, 460, lt, te + 0.1, dur=0.12, frm="up",
              scale_pop=True, exit_at=ex)
        light_hit(layer, 540, 460 + PACK_DY, lt, te + 0.1, PINK)
        return
    ghost(layer, "ALGORITHM")
    p = clamp01((lt - tw) / max(0.4, th + 0.3 - tw)) if lt >= tw else 0.04
    place(layer, chart_card(p, w=960, h=450, col=NEON, title="WATCH TIME", sub="THE ALGORITHM SEES IT"), 540, 150, lt,
          tal - 0.05, dur=0.14, frm="up", scale_pop=True)
    if lt >= th - 0.05:
        place(layer, stamp("WAY UP", NEON, 100, pad=36), 700, 40, lt, th - 0.05, dur=0.12, frm="down", scale_pop=True)
        light_hit(layer, 700, 40 + PACK_DY, lt, th - 0.05, NEON)


def cta(layer, lt, a):
    tac, tsk, tfr, tc, tew = T_ACCESS - a, T_SKILL - a, T_FREE - a, T_COMMENT - a, T_EDITW - a
    if lt < tc - 0.05:
        ex = tc - 0.12
        ghost(layer, "FREE SKILL")
        if lt < tfr - 0.05:
            lane(layer, lt)
            place(layer, os_chip("WANT ACCESS?", SILVER, 52), 540, -170, lt, -0.05, dur=0.14, frm="down",
                  exit_at=tfr - 0.1)
            if lt >= tac - 0.05:
                bloom_orb(layer, 300, 250, 220, ORANGE, a=90)
                place_claude_invader(layer, 300, 300 + PACK_DY - 40, lt, size=300, look_at=(760, 200))
            if lt >= tsk - 0.05:
                bloom_orb(layer, 760, 200, 220, ORANGE, a=80)
                place(layer, skill_file(460, 180), 740, 120, lt, tsk - 0.05, dur=0.12, frm="right",
                      scale_pop=True)
                place(layer, os_chip("THIS SKILL", ORANGE, 44), 760, 280, lt, tsk, dur=0.14, frm="up")
            return
        place(layer, gif_card("oprah-car", lt - tfr, w=560, frame="round"), 540, 120, lt, tfr - 0.05, dur=0.12,
              frm="up", scale_pop=True, exit_at=ex)
        place(layer, stamp("COMPLETELY FREE", NEON, 84, pad=32), 540, 440, lt, tfr - 0.05, dur=0.12, frm="up",
              scale_pop=True, exit_at=ex)
        light_hit(layer, 540, 440 + PACK_DY, lt, tfr - 0.05, NEON)
        return
    ghost(layer, "LINK IN DMS")
    place(layer, title_card('COMMENT "EDIT"', NEON, fsz=104, h=170), 540, -60, lt, tc - 0.05, dur=0.14, frm="down",
          scale_pop=True)
    light_hit(layer, 540, -60 + PACK_DY, lt, tc - 0.05, NEON)
    light_rays(layer, 540, -60 + PACK_DY, lt, NEON)
    place(layer, scaled(comment_card("EDIT", lt - tew), 1.3), 400, 270, lt, tc + 0.08, dur=0.2, frm="left")
    put(layer, scaled(skill_file(), 0.62), 880, 270 + PACK_DY, a=fade(lt, tc + 0.12))


SCENES = {"hook": hook, "style": style, "how": how, "giphy": giphy, "sync": sync, "list": list_, "result": result,
          "cta": cta}

# ───────────────────────────── compose ─────────────────────────────

if not os.path.isfile("renders/talking_band45.mp4"):
    raise SystemExit("missing renders/talking_band45.mp4")

band_cap = cv2.VideoCapture("renders/talking_band45.mp4")
band_mask = Image.new("L", (BAND_W, BAND_H), 0)
ImageDraw.Draw(band_mask).rounded_rectangle([0, 0, BAND_W - 1, BAND_H - 1], 60, fill=255)


def word_at(t):
    for w, a, b in words:
        if a <= t <= b + 0.08:
            return w.strip().rstrip(".,!?").lower(), a
    return None, None


def cap_label(wd):
    return wd.upper()


PUNCH_T = [T_OFF - 0.05, T_GIPHY - 0.05, T_CAPTIONS - 0.05, T_HIGH - 0.05]   # one hero word per section, >=8 s apart
HIT_T = [T_OFF - 0.05, T_TALKING - 0.05, T_HIGH - 0.05, T_COMMENT - 0.05]
CUT_T = [s[1] for s in SECT[1:]]
WHIP_T, HF_T = CUT_T[::2], CUT_T[1::2]
print("sections", [(s[0], round(s[1], 2)) for s in SECT])

os.makedirs("frames/out5", exist_ok=True)
PREVIEW = os.environ.get("PREVIEW")
if PREVIEW:
    todo = [min(N - 1, int(round(float(x) * FPS))) for x in PREVIEW.split(",")]
else:
    todo = list(range(N))
    if os.environ.get("RANGE"):
        _a, _b = os.environ["RANGE"].split(":")
        todo = list(range(int(_a), min(N, int(_b))))

last_band = None
if todo and not PREVIEW:
    band_cap.set(cv2.CAP_PROP_POS_FRAMES, todo[0])
prev_layer = None
prev_name = None

for n in todo:
    t = n / FPS
    name_, a, b = next(s for s in SECT if s[1] <= t < s[2] or s is SECT[-1])
    lt, sd = t - a, max(0.01, b - a)
    z = 1.0 + 0.05 * (lt / sd)
    bg = BGS[name_]
    bw, bh = int((W + 160) / z), int((H + 160) / z)
    ox, oy = (bg.width - bw) // 2, (bg.height - bh) // 2
    frame = bg.crop((ox, oy, ox + bw, oy + bh)).resize((W, H), Image.BICUBIC).convert("RGBA")
    layer = Image.new("RGBA", (W, AH), (0, 0, 0, 0))
    lanes.reset()

    scanlines(layer, t)
    hud_scan(layer, t, SECT_ACCENT[name_])
    neon_grid(layer, t, STEEL)
    SCENES[name_](layer, lt, a)
    slot_vignette(layer, a=22)
    speed_streaks(layer, t, PUNCH_T, NEON)

    if name_ != prev_name:
        prev_layer = None if name_ == "hook" else prev_layer
        prev_name = name_
    if lt < 0.16 and a in WHIP_T and prev_layer is not None:
        layer = whip_wipe(prev_layer, layer, lt / 0.16, direction=whip_dir(name_))
    else:
        prev_layer = layer.copy()

    layer = punch_zoom(layer, punch_scale(t, PUNCH_T, amt=0.045))
    sx, sy = shake_offset(t, HIT_T, amp=14)
    frame.alpha_composite(layer, (sx, LAYER_Y + sy))
    acc = SECT_ACCENT[name_]
    hd = ImageDraw.Draw(frame)
    hd.rectangle([48, BAND_Y - 8, W - 48, BAND_Y - 4], fill=acc + (200,))
    hd.rectangle([48, LAYER_Y + 2, W - 48, LAYER_Y + 4], fill=SILVER + (70,))
    if name_ != "hook":
        hyperframe(frame, t, HF_T, FPS, region=(0, LAYER_Y, W, AH))

    if PREVIEW:
        band_cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = band_cap.read()
    if ok:
        bf = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
        bf.putalpha(band_mask)
        last_band = bf
    if last_band is not None:
        frame.alpha_composite(last_band, (12, BAND_Y))

    wd, ons = word_at(t)
    if wd:
        d = ImageDraw.Draw(frame)
        key = wd in KEYWORDS
        col = (KEY_COL.get(wd, ORANGE) + (255,)) if key else (255, 255, 255, 255)
        fs = int(66 * caption_impact(t, ons, key))
        cf = F(CAP, fs)
        label = cap_label(wd)
        tw = d.textlength(label, font=cf)
        x = (W - tw) / 2
        y = BAND_Y - 8 - 7 - 3
        if key:
            caption_bloom(frame, x, y - fs, tw, fs, KEY_COL.get(wd, NEON))
        d.text((x, y), label, font=cf, fill=col, anchor="ls", stroke_width=7, stroke_fill=(0, 0, 0, 255))

    frame.convert("RGB").save(f"frames/out5/f{n:05d}.jpg", quality=92)
    if PREVIEW:
        print(f"preview t={t:.2f} {name_}", flush=True)
    elif n % 60 == 0:
        print(f"{n}/{N}", flush=True)

band_cap.release()
print("frames done", len(todo), flush=True)
