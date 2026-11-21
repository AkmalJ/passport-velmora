"""Draw one open passport spread of the Republic of Velmora.

Data page (left): portrait, bilingual Velmoran/English fields, observations.
Visa page (right): the High Pass endorsement, a Kordavia visa sticker, and
eight border stamps telling two journeys — the Sarn Pass on foot in July
2022 and the lake ferry to Sorrenne in May 2024. Every date agrees with the
issue date (Ostrev, 14 March 2021) and with the season the endorsement
allows. The machine-readable zone carries true ICAO check digits.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1024, 1024
TEAL = (18, 74, 63)
TEAL_SOFT = (84, 128, 116)
PAPER = (247, 243, 230)
INK = (28, 30, 34)
LABEL = (96, 104, 96)
RED = (178, 34, 40)
BACKDROP = (35, 42, 48)


def F(path, size):
    return ImageFont.truetype(path, size)


def icao_check(data: str) -> str:
    """ICAO 9303 check digit: weights 7-3-1 over '<'-padded values."""
    vals = {c: i for i, c in enumerate("0123456789")}
    vals.update({c: 10 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")})
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(data):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    doc = "VM0488217"
    dob = "940602"
    exp = "310314"
    personal = "94060222148"
    line1 = "P<VLMMARIK<<LENA"
    line1 = line1 + "<" * (44 - len(line1))
    body = (
        doc + icao_check(doc) + "VLM" + dob + icao_check(dob) + "F"
        + exp + icao_check(exp) + personal + icao_check(personal)
    )
    composite_src = body[:10] + body[13:20] + body[21:43]
    line2 = body + icao_check(composite_src)
    return line1[:44], line2[:44]


def grain(page: Image.Image, seed: int) -> None:
    """Fine wavy security lines across the paper, like the real thing."""
    rnd = random.Random(seed)
    overlay = Image.new("RGBA", page.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    w, h = page.size
    phase = rnd.uniform(0, 6.28)
    for y in range(-4, h, 7):
        pts = []
        for x in range(0, w + 8, 8):
            pts.append((x, y + 1.6 * math.sin(x / 46.0 + phase + y / 130.0)))
        od.line(pts, fill=(176, 164, 128, 16), width=1)
    page.alpha_composite(overlay)


def guilloche(page: Image.Image, cx: int, cy: int) -> None:
    """Pale rosette of wavy rings behind the data fields."""
    overlay = Image.new("RGBA", page.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for k in range(30):
        r = 26 + k * 7
        pts = []
        for a in range(0, 361, 6):
            rad = math.radians(a)
            rr = r + 9 * math.sin(rad * 5 + k / 3.0)
            pts.append((cx + rr * math.cos(rad) * 1.25, cy + rr * math.sin(rad)))
        od.line(pts + [pts[0]], fill=(38, 110, 96, 22), width=1)
    page.alpha_composite(overlay)


def emblem(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    """Line emblem: two peaks and a star inside a double ring."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL, width=3)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=TEAL, width=1)
    base = cy + r * 0.42
    d.line([(cx - r * 0.62, base), (cx - r * 0.18, cy - r * 0.34),
            (cx + r * 0.08, base)], fill=TEAL, width=3)
    d.line([(cx + r * 0.02, base), (cx + r * 0.34, cy - r * 0.12),
            (cx + r * 0.62, base)], fill=TEAL, width=3)
    sx, sy, sr = cx + r * 0.05, cy - r * 0.52, r * 0.13
    for a in (90, 162, 234, 306, 18):
        rad = math.radians(a)
        d.line([(sx, sy), (sx + sr * math.cos(rad), sy - sr * math.sin(rad))],
               fill=TEAL, width=2)


def field(d, x, y, label, value, vfont=None, lw=300):
    d.text((x, y), label, font=F(SANS, 10), fill=LABEL)
    d.text((x, y + 13), value, font=vfont or F(SANS_B, 17), fill=INK)
    return y + 44


STAMPS = [
    # (country line, kind, place, date, ink, round?)
    ("VELMORA", "EXIT", "SARN PASS · ON FOOT", "03 JUL 2022", (16, 92, 110), False),
    ("KORDAVIA", "ENTRY", "BRANIK", "03 JUL 2022", (30, 64, 160), False),
    ("KORDAVIA", "EXIT", "BRANIK", "18 JUL 2022", (30, 64, 160), False),
    ("VELMORA", "ENTRY", "SARN PASS", "18 JUL 2022", (16, 92, 110), False),
    ("VELMORA", "EXIT", "PORT AUBIN · FERRY", "11 MAY 2024", (110, 44, 140), False),
    ("SORRENNE", "ENTRÉE", "VILLEFRANCHE-SUR-LAC", "11 MAY 2024", (24, 116, 62), False),
    ("SORRENNE", "SORTIE", "VILLEFRANCHE-SUR-LAC", "25 MAY 2024", (24, 116, 62), False),
    ("VELMORA", "ENTRY", "PORT AUBIN", "25 MAY 2024", (110, 44, 140), False),
]


def stamp_tile(lines, ink, w=196, h=86):
    tile = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle([4, 4, w + 4, h + 4], radius=10, outline=ink + (215,), width=3)
    y = 13
    for text, font, dy in lines:
        tw = td.textlength(text, font=font)
        td.text(((w + 8 - tw) / 2, y), text, font=font, fill=ink + (225,))
        y += dy
    return tile


def build(out_path: str) -> str:
    img = Image.new("RGB", (W, H), BACKDROP)
    # soft vignette on the backdrop
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -200, W + 260, H + 200], fill=90)
    img = Image.composite(Image.new("RGB", (W, H), (52, 61, 68)), img, vig.filter(ImageFilter.GaussianBlur(120)))

    px, py, pw, ph = 34, 46, 956, 932
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([px + 10, py + 16, px + pw + 10, py + ph + 16], radius=8, fill=(0, 0, 0, 150))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(10))).convert("RGB"), (0, 0))

    page_w = pw // 2
    left = Image.new("RGBA", (page_w, ph), PAPER + (255,))
    right = Image.new("RGBA", (page_w, ph), (250, 246, 234, 255))
    grain(left, 7)
    grain(right, 19)
    guilloche(left, 300, 560)

    # ---------- LEFT: data page ----------
    d = ImageDraw.Draw(left)
    d.text((page_w - 118, 16), "VM 0488217", font=F(SANS_B, 14), fill=RED)
    emblem(d, 78, 66, 34)
    d.text((126, 34), "REPUBLIC OF VELMORA", font=F(SERIF_B, 27), fill=TEAL)
    d.text((128, 68), "V E L M O R S K A   R E P U B L I K A", font=F(SANS, 11), fill=TEAL_SOFT)
    d.text((128, 86), "PASSPORT  ·  PAS  ·  PASSEPORT", font=F(SANS, 11), fill=TEAL_SOFT)
    d.line([(24, 112), (page_w - 24, 112)], fill=TEAL, width=2)

    photo = Image.open(os.path.join(HERE, "portrait.jpg")).convert("RGB")
    photo = photo.crop((190, 40, 1090, 1180)).resize((168, 214))
    left.paste(photo, (24, 128))
    d.rectangle([24, 128, 192, 342], outline=(90, 90, 90), width=1)
    sig = Image.new("RGBA", (220, 54), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    sd.text((6, 6), "Lena Marik", font=F(SERIF_I, 34), fill=(26, 54, 168, 235))
    left.alpha_composite(sig.rotate(2, expand=True), (14, 348))
    d.text((24, 398), "SIGNATURE / PODPIS", font=F(SANS, 9), fill=LABEL)

    fx = 216
    d.text((fx, 128), "TYPE / VRSTA", font=F(SANS, 10), fill=LABEL)
    d.text((fx + 92, 128), "CODE / KOD", font=F(SANS, 10), fill=LABEL)
    d.text((fx + 156, 128), "PASSPORT No", font=F(SANS, 10), fill=LABEL)
    d.text((fx, 142), "P", font=F(SANS_B, 17), fill=INK)
    d.text((fx + 92, 142), "VLM", font=F(SANS_B, 17), fill=INK)
    d.text((fx + 156, 142), "VM 0488217", font=F(SANS_B, 16), fill=INK)
    y = 176
    y = field(d, fx, y, "SURNAME / PREZIME", "MARIK")
    y = field(d, fx, y, "GIVEN NAMES / IMENA", "LENA")
    y = field(d, fx, y, "NATIONALITY / DRZAVLJANSTVO", "VELMORAN")
    d.text((fx, y), "DOB / DATUM RODJENJA", font=F(SANS, 10), fill=LABEL)
    d.text((fx, y + 13), "02 JUN 1994", font=F(SANS_B, 17), fill=INK)
    d.text((fx + 168, y), "SEX / SPOL", font=F(SANS, 10), fill=LABEL)
    d.text((fx + 168, y + 13), "F", font=F(SANS_B, 17), fill=INK)
    y += 44
    y = field(d, fx, y, "PLACE OF BIRTH / MJESTO RODJENJA", "OSTREV")
    y = field(d, fx, y, "PERSONAL No / OSOBNI BROJ", "940602 2214 8")
    y = field(d, fx, y, "PROFESSION / ZANIMANJE", "MOUNTAIN GUIDE")
    d.text((fx, y), "ISSUE / DATUM IZDAVANJA", font=F(SANS, 10), fill=LABEL)
    d.text((fx, y + 13), "14 MAR 2021", font=F(SANS_B, 17), fill=INK)
    d.text((fx + 168, y), "EXPIRY / VAZI DO", font=F(SANS, 10), fill=LABEL)
    d.text((fx + 168, y + 13), "14 MAR 2031", font=F(SANS_B, 17), fill=INK)
    y += 44
    y = field(d, fx, y, "AUTHORITY / IZDAVAČ", "PASSPORT OFFICE, OSTREV")

    d.line([(24, 660), (page_w - 24, 660)], fill=TEAL_SOFT, width=1)
    d.text((24, 670), "OBSERVATIONS / NAPOMENE", font=F(SANS_B, 11), fill=TEAL)
    obs = ("Holder is a licensed guide of the Velmora Alpine Register,\n"
           "licence HG-2214. Crossings of the Sarn Pass on foot only:\n"
           "see endorsement on page 5.")
    d.multiline_text((24, 690), obs, font=F(SANS, 12.5), fill=INK, spacing=5)

    ghost = Image.open(os.path.join(HERE, "portrait.jpg")).convert("L")
    ghost = ghost.crop((190, 40, 1090, 1180)).resize((84, 107))
    ghost_rgba = Image.merge("RGBA", (ghost, ghost, ghost, ghost.point(lambda v: 46)))
    left.alpha_composite(ghost_rgba, (page_w - 116, 668))
    d.text((page_w - 40, ph - 118), "2", font=F(SANS, 12), fill=LABEL)

    l1, l2 = mrz_lines()
    d.line([(0, ph - 96), (page_w, ph - 96)], fill=(200, 194, 170), width=1)
    d.text((22, ph - 84), l1, font=F(MONO, 16.5), fill=(20, 20, 20))
    d.text((22, ph - 58), l2, font=F(MONO, 16.5), fill=(20, 20, 20))

    # ---------- RIGHT: visas page ----------
    d = ImageDraw.Draw(right)
    d.text((24, 26), "VISAS · VIZE", font=F(SERIF_B, 24), fill=TEAL)
    d.text((page_w - 40, 16), "5", font=F(SANS, 12), fill=LABEL)
    d.line([(24, 62), (page_w - 24, 62)], fill=TEAL, width=2)

    d.rectangle([24, 76, page_w - 24, 208], outline=TEAL, width=2)
    d.text((36, 86), "HIGH PASS ENDORSEMENT — No 7 / 2021", font=F(SANS_B, 13), fill=TEAL)
    d.text((36, 106), "OSTREV · 14 MAR 2021", font=F(SANS, 11), fill=LABEL)
    endorse = ("The holder is licensed to lead parties across the Sarn\n"
               "Pass (2,914 m), on foot only, 15 May – 15 October.\n"
               "Outside that season the pass is closed and no exit\n"
               "stamp may be issued for it. The guide's register card\n"
               "must be carried with this passport.")
    d.multiline_text((36, 124), endorse, font=F(SANS, 12), fill=INK, spacing=4)

    visa = Image.new("RGBA", (page_w - 48, 118), (214, 234, 208, 255))
    vd = ImageDraw.Draw(visa)
    vd.rectangle([0, 0, page_w - 49, 117], outline=(52, 96, 60), width=2)
    vd.text((12, 10), "REPUBLIC OF KORDAVIA", font=F(SANS_B, 15), fill=(24, 70, 34))
    vd.text((page_w - 150, 10), "VISA B", font=F(SANS_B, 15), fill=(24, 70, 34))
    vd.text((page_w - 150, 30), "No KD 2214 778", font=F(SANS, 10.5), fill=RED)
    vd.text((12, 34), "VALID 01 JUN 2022 – 01 JUN 2023 · ENTRIES: MULTIPLE", font=F(SANS, 11), fill=INK)
    vd.text((12, 52), "MARIK LENA · VM0488217", font=F(SANS_B, 12), fill=INK)
    vd.text((12, 70), "FEE 25 KDC — PAID", font=F(SANS_B, 11), fill=(24, 70, 34))
    bx = 12
    for ch in "KD2214778":
        wdt = 2 + (ord(ch) % 4)
        vd.rectangle([bx, 90, bx + wdt, 110], fill=(20, 20, 20))
        bx += wdt + 2
    right.alpha_composite(visa, (24, 222))

    toll = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    tod = ImageDraw.Draw(toll)
    tod.ellipse([6, 6, 144, 144], outline=(196, 92, 20, 220), width=4)
    tod.ellipse([18, 18, 132, 132], outline=(196, 92, 20, 200), width=2)
    for i, (t, f) in enumerate([("VELMORA", F(SANS_B, 13)), ("SARN PASS", F(SANS_B, 13)),
                                ("TOLL PAID", F(SANS_B, 15)), ("12 VMC", F(SANS_B, 13))]):
        tw = tod.textlength(t, font=f)
        tod.text(((150 - tw) / 2, 40 + i * 19), t, font=f, fill=(196, 92, 20, 230))
    right.alpha_composite(toll.rotate(-11, expand=True), (30, 776))

    positions = [(24, 348), (248, 356), (24, 452), (248, 460),
                 (24, 556), (248, 564), (24, 660), (248, 668)]
    rots = [-3, 2, 3, -2, -2, 3, 2, -3]
    for (country, kind, place, date, ink, _), (sx, sy), rot in zip(STAMPS, positions, rots):
        lines = [
            (country, F(SANS_B, 14), 17),
            (kind, F(SANS_B, 15), 18),
            (date, F(SANS_B, 14), 16),
            (place, F(SANS, 9.5), 12),
        ]
        tile = stamp_tile(lines, ink)
        right.alpha_composite(tile.rotate(rot, expand=True, resample=Image.BICUBIC), (sx, sy))
    d.text((page_w - 118, ph - 34), "VM 0488217", font=F(SANS_B, 13), fill=RED)

    # ---------- assemble ----------
    img.paste(left.convert("RGB"), (px, py))
    img.paste(right.convert("RGB"), (px + page_w, py))
    seam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdd = ImageDraw.Draw(seam)
    for i in range(26):
        alpha = int(70 * (1 - i / 26))
        sdd.line([(px + page_w - i, py), (px + page_w - i, py + ph)], fill=(0, 0, 0, alpha))
        sdd.line([(px + page_w + i, py), (px + page_w + i, py + ph)], fill=(255, 255, 255, alpha // 3))
    img = Image.alpha_composite(img.convert("RGBA"), seam).convert("RGB")

    img.save(out_path, optimize=True)
    if os.path.getsize(out_path) > 1_000_000:
        img.convert("P", palette=Image.ADAPTIVE, colors=256).save(out_path, optimize=True)
    return out_path
