"""SlipLab - Studio ya Mkeka wa Kisasa

Mtiririko: 1) Pakia screenshots -> 2) Hakiki mechi -> 3) Studio ya bango
Inahitaji: streamlit>=1.50, google-genai, pillow>=10.1, pydantic>=2, pandas
"""
from __future__ import annotations

import hashlib
import io
import os
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from pydantic import BaseModel, Field

# ============================================================
# 1. USANIDI
# ============================================================
st.set_page_config(page_title="SlipLab", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")

TZ = ZoneInfo("Africa/Dar_es_Salaam")  # saa za server mara nyingi ni UTC
MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
BACKGROUND_PHOTO = Path("profile.jpg")
STEPS = ["Pakia", "Hakiki mechi", "Studio ya bango"]
PICK_COUNTS = {2: "Mechi 2", 4: "Mechi 4", 6: "Mechi 6"}
STYLES = ["Tiketi", "Story", "Minimal"]

SANS = [
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]
MONO = [
    "DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
    "couB.ttf",
    "/Library/Fonts/Courier New Bold.ttf",
]

REASONS = {
    "quota": "Quota imeisha (429): kikomo cha matumizi cha key hii kimejaa",
    "invalid_key": "API key si sahihi, imefutwa au imeisha muda",
    "permission": "Key hii haina ruhusa ya kipengele au model hii (403)",
    "not_found": "Model haipatikani kwa akaunti hii (404)",
    "network": "Tatizo la mtandao au seva ya Google",
    "other": "Kosa lingine",
}
ADVICE = {
    "quota": "Weka API key mpya kwenye upau wa pembeni (🔑), au subiri kikomo kifunguke.",
    "invalid_key": "Hakikisha key imenakiliwa vyote bila nafasi, au tengeneza mpya kwenye ai.google.dev.",
    "permission": "Washa Gemini API kwenye project ya key hiyo, au tumia key ya project nyingine.",
    "not_found": "App inajaribu models zinazofuata yenyewe.",
    "network": "Jaribu tena baada ya muda mfupi.",
    "other": "Angalia maelezo ya kiufundi.",
}
OFFLINE_NOTE = (
    "\n\nONYO: Huna ufikiaji wa mtandao sasa. Tumia ujuzi wako tu. Kwa mechi ambazo huna taarifa za uhakika "
    "za majeruhi na fomu ya sasa, toa alama ya chini na sema wazi kwamba haijathibitishwa."
)


# ============================================================
# 2. DATA
# ============================================================
class Match(BaseModel):
    home: str = Field(description="Timu ya nyumbani kama ilivyoandikwa")
    away: str = Field(description="Timu ya ugenini kama ilivyoandikwa")
    league: str = Field(description="Ligi au mashindano; tupu kama haionekani")
    kickoff: str = Field(description="Saa ya kuanza kama inavyoonekana; tupu kama haionekani")
    odds: str = Field(description="Odds kama zinaonekana; tupu kama hazionekani")
    status: str = Field(description="NS = haijaanza, LIVE = inaendelea, FT = imeisha")


class Extraction(BaseModel):
    matches: list[Match]


class Pick(BaseModel):
    match: str = Field(description="Mechi kamili, mfano 'Roma vs Lazio'")
    label: str = Field(description="Chaguo fupi la bango (chini ya herufi 26), mfano 'Roma Win', 'Spurs or Draw'")
    why_safe: str = Field(description="Kwa nini soko hili ni salama kuliko ushindi wa moja kwa moja")
    confidence: int = Field(description="Alama ya usalama 0 hadi 100")
    risk: str = Field(description="Low au Medium")
    reasons: list[str] = Field(description="Sababu 3 hadi 5 zenye ushahidi (fomu, majeruhi, motisha, H2H, takwimu)")


class Analysis(BaseModel):
    picks: list[Pick]
    skipped: list[str] = Field(description="Mechi zilizotupwa, kila moja na sababu fupi")
    summary: str = Field(description="Muhtasari wa Kiswahili wa kwa nini hizi ndizo bora za leo")


@dataclass(frozen=True)
class Attempt:
    key_tag: str
    model: str
    kind: str
    message: str


class AllAttemptsFailed(RuntimeError):
    def __init__(self, attempts: list[Attempt]):
        self.attempts = attempts
        super().__init__("Majaribio yote yameshindwa")


# ============================================================
# 3. API KEYS + GEMINI
# ============================================================
def key_tag(key: str) -> str:
    return f"…{key[-4:]}"


def collect_api_keys() -> list[str]:
    keys: list[str] = []
    typed = (st.session_state.get("custom_key") or "").strip()
    if typed:
        keys.append(typed)
    try:
        many = st.secrets.get("GEMINI_API_KEYS", None)
        if many:
            keys.extend(str(k).strip() for k in list(many))
        single = st.secrets.get("GEMINI_API_KEY", "")
        if single:
            keys.append(str(single).strip())
    except Exception:
        pass
    env = os.environ.get("GEMINI_API_KEY", "").strip()
    if env:
        keys.append(env)
    return list(dict.fromkeys(k for k in keys if k))


def classify(exc: Exception) -> str:
    t = str(exc).upper()
    if "RESOURCE_EXHAUSTED" in t or t.startswith("429"):
        return "quota"
    if any(s in t for s in ("API_KEY_INVALID", "API KEY NOT VALID", "API KEY EXPIRED", "UNAUTHENTICATED")) or t.startswith("401"):
        return "invalid_key"
    if "PERMISSION_DENIED" in t or t.startswith("403"):
        return "permission"
    if "NOT_FOUND" in t or t.startswith("404"):
        return "not_found"
    if any(s in t for s in ("TIMEOUT", "TIMED OUT", "CONNECTION", "UNAVAILABLE", "503", "DEADLINE")):
        return "network"
    return "other"


def explain(attempts: list[Attempt]) -> str:
    grouped: dict[tuple[str, str], list[str]] = {}
    for a in attempts:
        grouped.setdefault((a.key_tag, a.kind), []).append(a.model)
    lines = [f"- **Key {tag}**: {REASONS[kind]} _(models: {', '.join(models)})_" for (tag, kind), models in grouped.items()]
    kinds = list(dict.fromkeys(a.kind for a in attempts))
    return "\n".join(lines + ["", "**Cha kufanya:**"] + [f"- {ADVICE[k]}" for k in kinds])


def show_failure(exc: AllAttemptsFailed) -> None:
    st.error("❌ Imeshindikana. Sababu kwa kila key:")
    st.markdown(explain(exc.attempts))
    with st.expander("Maelezo ya kiufundi"):
        for a in exc.attempts:
            st.code(f"{a.model} · key {a.key_tag} · {a.kind}\n{a.message}")


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def list_models(key: str, client: genai.Client) -> list[str]:
    cache = st.session_state.setdefault("_models_cache", {})
    digest = hashlib.sha256(key.encode()).hexdigest()
    if digest not in cache:
        try:
            cache[digest] = [m.name.removeprefix("models/") for m in client.models.list()]
        except Exception:
            return []
    return cache[digest]


def generate(keys: list[str], contents, config: types.GenerateContentConfig):
    """Kila key kwa zamu, na kwa kila key models zake. Inarudisha (jibu, 'model · key')."""
    attempts: list[Attempt] = []
    for key in keys:
        tag, client = key_tag(key), get_client(key)
        names = list_models(key, client)
        for model in [m for m in MODELS if m in names] or MODELS:
            try:
                response = client.models.generate_content(model=model, contents=contents, config=config)
                if response.text or response.parsed:
                    return response, f"{model} · key {tag}"
                attempts.append(Attempt(tag, model, "other", "jibu tupu"))
            except Exception as exc:
                kind = classify(exc)
                attempts.append(Attempt(tag, model, kind, str(exc)[:250]))
                if kind == "invalid_key":
                    break
    raise AllAttemptsFailed(attempts)


def extract_matches(keys: list[str], images: list[Image.Image]) -> Extraction:
    prompt = (
        "Soma screenshots zote na orodhesha KILA mechi inayoonekana. Usibuni mechi wala taarifa. "
        "Andika majina ya timu kama yalivyoandikwa. status: NS kama haijaanza, LIVE kama ina matokeo au dakika "
        "zinaendelea, FT kama imeisha. Acha sehemu tupu kama taarifa haionekani."
    )
    config = types.GenerateContentConfig(
        response_mime_type="application/json", response_schema=Extraction, temperature=0.0
    )
    response, _ = generate(keys, [prompt, *images], config)
    if isinstance(response.parsed, Extraction):
        return response.parsed
    return Extraction.model_validate_json(response.text)


def research_prompt(day: str, date: str, matches_text: str) -> str:
    return f"""
Wewe ni mchambuzi mkuu wa soka wa kiwango cha juu. Lengo la mteja: kuchagua mechi chache SALAMA kuliko zote
ili mkeka usichanike. Ubora ni muhimu kuliko wingi. Leo ni {day}, tarehe {date} (saa za Afrika Mashariki).

MECHI ZA KUCHAMBUA:
{matches_text}

Kwa kila mechi, tafuta taarifa za SASA na uchambue kwa kina:
1. Fomu ya mechi 5-6 za mwisho za kila timu (nyumbani na ugenini kando kando).
2. Rekodi ya mechi za hivi karibuni kati yao (H2H).
3. Majeruhi, adhabu, wachezaji muhimu kukosekana, kikosi kinachotarajiwa.
4. Motisha: msimamo, kushuka daraja, ubingwa, mechi ya kombe, timu kupumzisha wachezaji.
5. Uchovu na ratiba: mechi za katikati ya wiki, safari ndefu.
6. Mbinu za makocha, mechi-ups, takwimu za magoli (wastani, xG, clean sheets).
7. Mazingira: uwanja, hali ya hewa, mwamuzi kama inahusika.
8. Odds: je zinaendana na uwezekano halisi? Epuka mitego ya odds ndogo kwa timu kubwa yenye matatizo.
9. Soko salama zaidi: Double Chance, Draw No Bet, Over 1.5, Under 4.5, n.k., badala ya ushindi wa moja kwa moja pale una hatari.

Kila mechi ipe alama ya usalama 0-100 na sababu zake. Kuwa mkali: ukiona shaka kubwa, ipe alama ya chini.
Usibuni takwimu; kama huna uhakika, sema wazi. Toa ripoti kamili kwa Kiswahili.
""".strip()


def selection_prompt(report: str, count: int, min_conf: int) -> str:
    return f"""
Ripoti ya uchambuzi:

{report}

KAZI: Chagua mechi BORA ZA SIKU, zisizozidi {count}.
- Chukua TU zenye confidence ya {min_conf} au zaidi. Kama hazifiki {count}, toa chache. Usijaze nafasi kwa mechi dhaifu.
- Panga kuanzia yenye confidence kubwa zaidi.
- 'label' iwe fupi na iseme soko wazi.
- Weka kwenye 'skipped' mechi zilizotupwa pamoja na sababu fupi.
- Usibuni taarifa ambazo hazipo kwenye ripoti.
""".strip()


def analyse(keys, matches_text, day, date, count, min_conf, use_search):
    """Inarudisha (Analysis, ripoti, 'model · key', ilitumia_utafutaji)."""
    prompt = research_prompt(day, date, matches_text)
    report, used, searched = "", "", False
    if use_search:
        cfg = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())], temperature=0.2)
        try:
            response, used = generate(keys, prompt, cfg)
            report, searched = response.text or "", True
        except AllAttemptsFailed as exc:
            if {a.kind for a in exc.attempts} <= {"invalid_key", "network"}:
                raise
            st.warning("🔎 Utafutaji wa mtandaoni umeshindikana. Sababu:\n\n" + explain(exc.attempts))
            st.write("Inaendelea bila mtandao (alama zitakuwa za tahadhari zaidi)...")
    if not report:
        response, used = generate(keys, prompt + OFFLINE_NOTE, types.GenerateContentConfig(temperature=0.2))
        report = response.text or ""

    cfg = types.GenerateContentConfig(response_mime_type="application/json", response_schema=Analysis, temperature=0.2)
    response, _ = generate(keys, selection_prompt(report, count, min_conf), cfg)
    result = response.parsed if isinstance(response.parsed, Analysis) else Analysis.model_validate_json(response.text)
    return result, report, used, searched


# ============================================================
# 4. MABANGO
# ============================================================
def font(size: int, mono: bool = False):
    for path in (MONO if mono else SANS):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def fit(draw, text: str, max_w: int, start: int, minimum: int = 16, mono: bool = False):
    for size in range(start, minimum, -2):
        f = font(size, mono)
        l, _, r, _ = draw.textbbox((0, 0), text, font=f)
        if r - l <= max_w:
            return f
    return font(minimum, mono)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def mix(a, b, t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def on_color(c) -> tuple[int, int, int]:
    return (15, 15, 22) if (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) > 150 else (255, 255, 255)


def dashed(draw, x1, x2, y, color, dash=14, gap=10, width=3):
    x = x1
    while x < x2:
        draw.line((x, y, min(x + dash, x2), y), fill=color, width=width)
        x += dash + gap


def backdrop(size, accent, photo: bytes | None) -> Image.Image:
    dark = (6, 6, 16)
    base = ImageOps.colorize(
        Image.linear_gradient("L").resize(size), black=mix(accent, dark, 0.5), white=mix(accent, dark, 0.92)
    ).convert("RGBA")
    if photo:
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(photo))).convert("RGBA")
            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
            img = ImageEnhance.Brightness(img).enhance(0.55)
            base.putalpha(200)
            base = Image.alpha_composite(img, base)
        except Exception:
            pass
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-300, -300, 600, 500), fill=(*accent, 90))
    return Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(130)))


def poster_ticket(labels, matches, confs, title, date_label, accent, watermark, photo) -> Image.Image:
    n, W = len(labels), 1080
    row_h, head_h, foot_h = 118, 330, 440
    paper_h = head_h + n * row_h + foot_h
    H = max(1350, paper_h + 220)
    canvas = backdrop((W, H), accent, photo)
    x1, x2 = 110, W - 110
    y1 = (H - paper_h) // 2
    y2 = y1 + paper_h

    # Karatasi yenye kingo za zigzag
    k, amp = 28, 16
    step = (x2 - x1) / k
    top_pts = [(x1 + i * step, y1 + (amp if i % 2 else 0)) for i in range(k + 1)]
    bot_pts = [(x1 + i * step, y2 - (amp if i % 2 else 0)) for i in range(k + 1)]
    polygon = top_pts + bot_pts[::-1]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(x, y + 18) for x, y in polygon], fill=(0, 0, 0, 140))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(canvas)
    d.polygon(polygon, fill=(252, 250, 245))

    ink, grey, line = (22, 22, 28), (110, 110, 120), (200, 198, 190)
    cx = W // 2
    d.text((cx, y1 + 62), "*  BETSLIP  *", fill=grey, font=font(28, True), anchor="mm")
    d.text((cx, y1 + 130), title.upper(), fill=ink, font=fit(d, title.upper(), x2 - x1 - 80, 68, 28, True), anchor="mm")
    d.text((x1 + 44, y1 + 215), "DATE", fill=grey, font=font(24, True), anchor="lm")
    d.text((x2 - 44, y1 + 215), date_label.upper(), fill=ink, font=font(24, True), anchor="rm")
    dashed(d, x1 + 40, x2 - 40, y1 + head_h - 36, line)

    ty = y1 + head_h
    for i, label in enumerate(labels):
        cy = ty + i * row_h + row_h // 2
        d.text((x1 + 44, cy), f"{i + 1:02d}", fill=accent, font=font(34, True), anchor="lm")
        pill_t = f"{confs[i]}%"
        pf = font(30, True)
        l, _, r, _ = d.textbbox((0, 0), pill_t, font=pf)
        pw = (r - l) + 36
        d.rounded_rectangle((x2 - 44 - pw, cy - 26, x2 - 44, cy + 26), radius=12, fill=accent)
        d.text((x2 - 44 - pw // 2, cy), pill_t, fill=on_color(accent), font=pf, anchor="mm")
        max_w = (x2 - 44 - pw - 24) - (x1 + 130)
        d.text((x1 + 130, cy - 14), label, fill=ink, font=fit(d, label, max_w, 38, 20, True), anchor="lm")
        d.text((x1 + 130, cy + 24), matches[i], fill=grey, font=fit(d, matches[i], max_w, 22, 14, True), anchor="lm")
        dashed(d, x1 + 40, x2 - 40, ty + (i + 1) * row_h, line, 8, 8, 2)

    fy = ty + n * row_h + 40
    avg = round(sum(confs) / max(1, len(confs)))
    d.text((x1 + 44, fy + 10), "SELECTIONS", fill=grey, font=font(26, True), anchor="lm")
    d.text((x2 - 44, fy + 10), str(n), fill=ink, font=font(30, True), anchor="rm")
    d.text((x1 + 44, fy + 62), "AVG CONFIDENCE", fill=grey, font=font(26, True), anchor="lm")
    d.text((x2 - 44, fy + 62), f"{avg}%", fill=ink, font=font(30, True), anchor="rm")
    dashed(d, x1 + 40, x2 - 40, fy + 110, line)

    # Barcode (inatokana na chaguo, kwa hiyo kila bango lina lake)
    rnd = random.Random(int(hashlib.md5("|".join(labels).encode()).hexdigest()[:8], 16))
    bx, by, bh = x1 + 90, fy + 140, 100
    while bx < x2 - 90:
        bw = rnd.choice((3, 3, 5, 8))
        d.rectangle((bx, by, bx + bw, by + bh), fill=ink)
        bx += bw + rnd.choice((4, 6, 9))
    code = "".join(rnd.choice("0123456789") for _ in range(14))
    d.text((cx, by + bh + 30), code, fill=grey, font=font(22, True), anchor="mm")
    mark = watermark.strip() or "SLIPLAB"
    d.text((cx, by + bh + 80), mark, fill=ink, font=fit(d, mark, x2 - x1 - 100, 28, 16, True), anchor="mm")
    d.text((cx, y2 - 46), "18+  CHEZA KWA UWAJIBIKAJI", fill=grey, font=font(20, True), anchor="mm")
    return canvas


def poster_story(labels, matches, confs, title, date_label, accent, watermark, photo) -> Image.Image:
    W, H = 1080, 1920
    canvas = backdrop((W, H), accent, photo)
    d = ImageDraw.Draw(canvas)
    soft = mix(accent, (255, 255, 255), 0.35)

    d.text((90, 150), date_label.upper(), fill=soft, font=font(32), anchor="lm")
    d.text((90, 290), title, fill=(255, 255, 255), font=fit(d, title, W - 180, 128, 40), anchor="lm")
    d.rectangle((90, 380, 330, 392), fill=accent)

    n = max(1, len(labels))
    top, bottom = 470, H - 330
    row_h = min(230, (bottom - top) // n)
    for i, label in enumerate(labels):
        y = top + i * row_h
        cy = y + row_h // 2
        d.text((90, cy), f"{i + 1:02d}", fill=accent, font=font(int(row_h * 0.46)), anchor="lm")
        tx = 90 + int(row_h * 0.62) + 40
        pct = f"{confs[i]}%"
        pf = font(int(row_h * 0.26))
        d.text((W - 90, cy), pct, fill=soft, font=pf, anchor="rm")
        max_w = (W - 90 - 170) - tx
        d.text((tx, cy - row_h * 0.1), label, fill=(255, 255, 255), font=fit(d, label, max_w, int(row_h * 0.32), 24), anchor="lm")
        d.text((tx, cy + row_h * 0.22), matches[i], fill=mix(accent, (255, 255, 255), 0.6), font=fit(d, matches[i], max_w, int(row_h * 0.15), 16), anchor="lm")
        d.line((90, y + row_h, W - 90, y + row_h), fill=(*mix(accent, (255, 255, 255), 0.25), 255), width=2)

    mark = watermark.strip() or "SLIPLAB"
    d.text((W // 2, H - 190), mark, fill=(255, 255, 255), font=fit(d, mark, W - 200, 40, 20), anchor="mm")
    d.text((W // 2, H - 130), "18+ · Cheza kwa uwajibikaji · Hakuna ushindi wa uhakika", fill=soft, font=font(24), anchor="mm")
    return canvas


def poster_minimal(labels, matches, confs, title, date_label, accent, watermark, photo) -> Image.Image:
    W, H = 1080, 1350
    canvas = Image.new("RGBA", (W, H), (248, 248, 250, 255))
    if photo:  # picha inaonekana kama utepe laini juu
        try:
            img = ImageOps.fit(ImageOps.exif_transpose(Image.open(io.BytesIO(photo))).convert("RGBA"), (W, 300), Image.Resampling.LANCZOS)
            canvas.paste(img, (0, 0))
        except Exception:
            pass
    d = ImageDraw.Draw(canvas)
    ink, grey = (18, 18, 24), (120, 120, 132)
    d.rectangle((0, 0, W, 16), fill=accent)
    d.text((90, 130), date_label.upper(), fill=grey if not photo else (255, 255, 255), font=font(28), anchor="lm")
    d.text((90, 215), title, fill=ink if not photo else (255, 255, 255), font=fit(d, title, W - 180, 96, 36), anchor="lm")

    n = max(1, len(labels))
    top, bottom = 360, H - 210
    row_h = min(170, (bottom - top) // n)
    for i, label in enumerate(labels):
        y = top + i * row_h
        cy = y + row_h // 2
        d.rounded_rectangle((90, y + 14, 104, y + row_h - 14), radius=7, fill=accent)
        d.text((140, cy - row_h * 0.1), label, fill=ink, font=fit(d, label, W - 140 - 90 - 190, int(row_h * 0.34), 22), anchor="lm")
        d.text((140, cy + row_h * 0.2), matches[i], fill=grey, font=fit(d, matches[i], W - 140 - 90 - 190, int(row_h * 0.17), 14), anchor="lm")
        d.text((W - 90, cy), f"{confs[i]}%", fill=accent, font=font(int(row_h * 0.3)), anchor="rm")
        d.line((140, y + row_h, W - 90, y + row_h), fill=(226, 226, 232), width=2)

    mark = watermark.strip() or "SLIPLAB"
    d.text((90, H - 120), mark, fill=ink, font=fit(d, mark, W - 180, 30, 16), anchor="lm")
    d.text((90, H - 70), "18+ · Cheza kwa uwajibikaji · Hakuna ushindi wa uhakika", fill=grey, font=font(22), anchor="lm")
    return canvas


RENDERERS = {"Tiketi": poster_ticket, "Story": poster_story, "Minimal": poster_minimal}


@st.cache_data(show_spinner=False, max_entries=24)
def render_poster(style, labels, matches, confs, title, date_label, accent_hex, watermark, photo: bytes | None) -> bytes:
    image = RENDERERS[style](labels, matches, confs, title, date_label, hex_rgb(accent_hex), watermark, photo)
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def prepare_images(files) -> list[Image.Image]:
    images = []
    for file in files:
        img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
        img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        images.append(img)
    return images


# ============================================================
# 5. MUONEKANO
# ============================================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    .stApp { background: radial-gradient(1000px 600px at 85% -10%, rgba(139,92,246,.22), transparent 60%), #0b0a14; color: #f1f0fa; }
    #MainMenu, footer, .stAppDeployButton { display: none; }
    section[data-testid="stSidebar"] { background: #100e1d; border-right: 1px solid rgba(255,255,255,.07); }
    .brand { font-size: 2rem; font-weight: 700; letter-spacing: -1px; margin: 0; }
    .brand span { background: linear-gradient(90deg,#a78bfa,#f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .tag { color: #9b97b8; margin: 2px 0 18px; }
    .stepper { display: flex; gap: 10px; margin: 6px 0 22px; flex-wrap: wrap; }
    .step { padding: 8px 16px; border-radius: 999px; border: 1px solid rgba(255,255,255,.12); color: #8f8bad; font-size: .85rem; }
    .step.on { color: #fff; border-color: #a78bfa; background: linear-gradient(135deg, rgba(167,139,250,.28), rgba(244,114,182,.2)); }
    .step.done { color: #c4b5fd; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(255,255,255,.09) !important; border-radius: 16px; background: rgba(255,255,255,.025); }
    .stButton > button[kind="primary"], .stDownloadButton > button {
        background: linear-gradient(135deg,#8b5cf6,#ec4899); color: #fff; border: 0; border-radius: 12px; font-weight: 700;
        padding: .7rem 1.4rem; box-shadow: 0 8px 24px rgba(139,92,246,.35); }
    .stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover { filter: brightness(1.1); color: #fff; }
</style>
""",
    unsafe_allow_html=True,
)

now = datetime.now(TZ)
day_name, date_short, date_long = now.strftime("%A"), now.strftime("%d-%m-%Y"), now.strftime("%d %B %Y")

ss = st.session_state
ss.setdefault("step", 1)

# ---------------- Upau wa pembeni ----------------
with st.sidebar:
    st.markdown("### 🔑 API Key")
    st.text_input(
        "Weka key mpya ikiisha quota", type="password", key="custom_key", placeholder="AIza...",
        help="Inatumika kwa kikao hiki tu na haihifadhiwi.",
    )
    keys = collect_api_keys()
    if keys:
        st.caption("Keys zinazotumika kwa mpangilio: " + ", ".join(key_tag(k) for k in keys))
    else:
        st.warning("Hakuna API key. Iweke hapa au kwenye Secrets.")
    st.caption('Keys nyingi kwenye Secrets: `GEMINI_API_KEYS = ["key1", "key2"]`. Ya kwanza ikiisha, inahamia inayofuata.')
    st.divider()
    if st.button("🗑️ Anza upya kabisa", width="stretch"):
        for k in ("step", "matches_df", "analysis", "report", "used", "searched", "title"):
            ss.pop(k, None)
        st.rerun()

keys = collect_api_keys()

# ---------------- Kichwa + stepper ----------------
st.markdown('<p class="brand">Slip<span>Lab</span> 🧪</p>', unsafe_allow_html=True)
st.markdown(f'<p class="tag">Studio ya mkeka wa kisasa · {day_name}, {date_short}</p>', unsafe_allow_html=True)


def stepper(current: int) -> None:
    pills = "".join(
        f'<span class="step {"on" if i == current else "done" if i < current else ""}">{i}. {name}</span>'
        for i, name in enumerate(STEPS, start=1)
    )
    st.markdown(f'<div class="stepper">{pills}</div>', unsafe_allow_html=True)


if ss.step > 1 and "matches_df" not in ss:
    ss.step = 1
if ss.step > 2 and "analysis" not in ss:
    ss.step = 2
stepper(ss.step)

# ============================================================
# HATUA 1: PAKIA
# ============================================================
if ss.step == 1:
    with st.container(border=True):
        st.markdown("#### 📸 Pakia screenshots za mechi")
        st.caption("AI itasoma mechi zote kwanza, kisha wewe utazihakiki kabla ya uchambuzi.")
        files = st.file_uploader("Screenshots", type=["png", "jpg", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            images = prepare_images(files)
            st.image(images, width=140)
            if st.button("📖 Soma mechi kwenye picha", type="primary"):
                if not keys:
                    st.error("Hakuna API key. Iweke kwenye upau wa pembeni.")
                else:
                    try:
                        with st.spinner("Inasoma mechi..."):
                            extraction = extract_matches(keys, images)
                        rows = [
                            {
                                "Chagua": m.status.upper() == "NS",
                                "Nyumbani": m.home, "Ugenini": m.away, "Ligi": m.league,
                                "Muda": m.kickoff, "Odds": m.odds,
                                "Hali": m.status.upper() if m.status.upper() in ("NS", "LIVE", "FT") else "NS",
                            }
                            for m in extraction.matches
                        ]
                        if not rows:
                            st.warning("Hakuna mechi iliyoonekana kwenye picha. Jaribu picha iliyo wazi zaidi.")
                        else:
                            ss.matches_df = pd.DataFrame(rows)
                            ss.step = 2
                            st.rerun()
                    except AllAttemptsFailed as exc:
                        show_failure(exc)
                    except Exception as exc:
                        st.error(f"Hitilafu isiyotarajiwa: {exc}")

# ============================================================
# HATUA 2: HAKIKI
# ============================================================
elif ss.step == 2:
    with st.container(border=True):
        st.markdown("#### ✅ Hakiki mechi")
        st.caption("Rekebisha majina, ondoa mechi usizotaka, au ongeza mpya. Mechi zenye hali ya NS tu (hazijaanza) ndizo zitachambuliwa.")
        edited = st.data_editor(
            ss.matches_df,
            num_rows="dynamic",
            width="stretch",
            hide_index=True,
            column_config={
                "Chagua": st.column_config.CheckboxColumn("Chagua", default=True),
                "Hali": st.column_config.SelectboxColumn("Hali", options=["NS", "LIVE", "FT"], default="NS"),
            },
            key="match_editor",
        )

    with st.container(border=True):
        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            count = st.segmented_control("Idadi ya juu ya mechi", list(PICK_COUNTS), format_func=PICK_COUNTS.get, default=4) or 4
        with c2:
            min_conf = st.slider("Usalama wa chini (%)", 60, 95, 80, 5, help="Mechi chini ya kiwango hiki zinatupwa.")
        with c3:
            use_search = st.toggle("🔎 Utafutaji wa mtandaoni", value=True, help="Uchambuzi bora zaidi, lakini unatumia quota nyingi.")

    left, right = st.columns([1, 3])
    if left.button("← Rudi"):
        ss.step = 1
        st.rerun()

    if right.button("🧠 Chambua mechi zilizochaguliwa", type="primary"):
        chosen = edited[(edited["Chagua"] == True) & (edited["Hali"] == "NS")].dropna(subset=["Nyumbani", "Ugenini"])  # noqa: E712
        if chosen.empty:
            st.warning("Chagua angalau mechi moja yenye hali ya NS.")
        elif not keys:
            st.error("Hakuna API key. Iweke kwenye upau wa pembeni.")
        else:
            matches_text = "\n".join(
                f"- {r.Nyumbani} vs {r.Ugenini} | {r.Ligi or '-'} | {r.Muda or '-'} | odds: {r.Odds or '-'}"
                for r in chosen.itertuples()
            )
            try:
                with st.status("Uchambuzi wa kina unaendelea (dakika 1-2)...", expanded=True) as status:
                    st.write(f"🔎 Inachambua mechi {len(chosen)}: fomu, majeruhi, motisha, takwimu...")
                    result, report, used, searched = analyse(keys, matches_text, day_name, date_short, count, min_conf, use_search)
                    picks = sorted((p for p in result.picks if p.confidence >= min_conf), key=lambda p: -p.confidence)[:count]
                    if not picks:
                        status.update(label="Hakuna mechi iliyofikia kiwango", state="error")
                        st.warning(
                            f"Hakuna mechi iliyofikia usalama wa {min_conf}%. Bora kutoweka leo kuliko kuchana mkeka. "
                            "Ongeza mechi au punguza kiwango kidogo."
                        )
                    else:
                        ss.analysis = Analysis(picks=picks, skipped=result.skipped, summary=result.summary)
                        ss.report, ss.used, ss.searched = report, used, searched
                        ss.matches_df = edited
                        ss.step = 3
                        status.update(label="Uchambuzi umekamilika ✅", state="complete", expanded=False)
                        st.rerun()
            except AllAttemptsFailed as exc:
                show_failure(exc)
            except Exception as exc:
                st.error(f"Hitilafu isiyotarajiwa: {exc}")

# ============================================================
# HATUA 3: STUDIO
# ============================================================
else:
    analysis: Analysis = ss.analysis
    picks = analysis.picks
    st.caption(
        f"Model: {ss.used} · Utafutaji wa mtandaoni: "
        f"{'umetumika ✅' if ss.searched else 'haukutumika (alama ni za tahadhari)'}"
    )
    poster_col, detail_col = st.columns([1, 1.15], gap="large")

    with poster_col:
        with st.container(border=True):
            st.markdown("##### 🎨 Studio (haitumii quota)")
            style = st.pills("Mtindo", STYLES, default="Tiketi") or "Tiketi"
            c1, c2 = st.columns([1, 2])
            accent = c1.color_picker("Rangi kuu", "#8b5cf6")
            title = c2.text_input("Kichwa", value=ss.get("title") or f"{day_name} Picks")
            ss.title = title
            watermark = st.text_input("Watermark / jina lako", value="SLIPLAB")
            photo_file = st.file_uploader("Picha yako (hiari)", type=["png", "jpg", "jpeg"], key="bg_photo")

        if photo_file:
            photo = photo_file.getvalue()
        elif BACKGROUND_PHOTO.exists():
            photo = BACKGROUND_PHOTO.read_bytes()
        else:
            photo = None

        png = render_poster(
            style,
            tuple(p.label for p in picks),
            tuple(p.match for p in picks),
            tuple(int(p.confidence) for p in picks),
            title or f"{day_name} Picks",
            date_long,
            accent,
            watermark,
            photo,
        )
        st.image(png, width="stretch")
        st.download_button(
            "📥 Pakua bango (PNG)", data=png, file_name=f"SlipLab_{day_name}_{style}.png",
            mime="image/png", width="stretch",
        )

    with detail_col:
        st.markdown("#### 📊 Uchambuzi wa kila chaguo")
        for i, p in enumerate(picks, start=1):
            with st.container(border=True):
                st.markdown(f"**{i}. {p.label}** · {p.match}")
                st.progress(min(max(p.confidence, 0), 100) / 100, text=f"Usalama: {p.confidence}% · Hatari: {p.risk}")
                st.caption(f"Kwa nini soko hili: {p.why_safe}")
                for reason in p.reasons:
                    st.markdown(f"- {reason}")
        st.info(analysis.summary)
        with st.expander("🗑️ Mechi zilizotupwa na sababu"):
            for item in analysis.skipped or ["Hakuna taarifa."]:
                st.markdown(f"- {item}")
        with st.expander("📄 Ripoti kamili"):
            st.write(ss.report)

    if st.button("← Rudi kuhariri mechi"):
        ss.step = 2
        st.rerun()
    st.caption("Hakuna mechi yenye uhakika wa 100%. AI inapunguza hatari, haiiondoi. Weka kiasi unachoweza kukipoteza.")
