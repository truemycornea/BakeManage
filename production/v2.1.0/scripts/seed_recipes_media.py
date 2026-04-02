# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
"""
Seed Script: 13 Rich Bakery Recipes + Media Library
=====================================================
Generates:
  - 13 authentic Indian-bakery recipes with real ingredient costs
  - PIL-rendered recipe card thumbnails (PNG, stored as base64)
  - 13 recipe PDF cards (multi-row Pillow images stored as JPEG data URI)
  - 18 media library entries: recipe PDFs + instructional video metadata
  - Updates recipe-linked sale records to use proper product names

Run via:
    docker cp scripts/seed_recipes_media.py bakemanage-api-1:/tmp/
    docker exec bakemanage-api-1 python /tmp/seed_recipes_media.py
"""
from __future__ import annotations

import base64
import io
import os
import sys
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# ── DB connection ────────────────────────────────────────────────────────────
url = os.environ.get("DATABASE_URL", "postgresql://bakemanage:bakemanage@db:5432/bakemanage")
engine = create_engine(url)

# ── Import models ─────────────────────────────────────────────────────────────
sys.path.insert(0, "/app")
from app.models import Base, InventoryItem, MediaAsset, Recipe, RecipeIngredient

Base.metadata.create_all(bind=engine)

# ── PIL import ───────────────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: Pillow not available — thumbnails will be skipped")


# ── Colour palette (warm bakery tones) ───────────────────────────────────────
COLOURS = {
    "card_bg":    (254, 247, 237),   # warm cream
    "header_bg":  (120,  53,  15),   # deep brown
    "accent":     (217, 119,   6),   # amber
    "text_dark":  ( 28,  25,  23),   # near-black
    "text_mid":   ( 87,  83,  78),   # warm grey
    "text_light": (168, 162, 158),   # lighter grey
    "divider":    (231, 213, 199),   # light tan
    "tag_bg":     (255, 237, 213),   # peach
    "tag_text":   (154,  52,  18),   # rust
    "white":      (255, 255, 255),
}


def _font(size: int):
    """Return a font, falling back gracefully."""
    for name in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _font_reg(size: int):
    for name in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def generate_recipe_card(recipe: dict) -> str:
    """Render a 600×800 recipe card and return base64 JPEG data URI."""
    if not PIL_AVAILABLE:
        return ""

    W, H = 600, 820
    img = Image.new("RGB", (W, H), COLOURS["card_bg"])
    draw = ImageDraw.Draw(img)

    # ── Header bar ────────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 110)], fill=COLOURS["header_bg"])

    # Logo mark — small circle
    draw.ellipse([(20, 20), (70, 70)], fill=COLOURS["accent"])
    draw.text((28, 30), "BM", font=_font(22), fill=COLOURS["white"])

    # Recipe name
    name = recipe["name"]
    draw.text((90, 20), "BakeManage", font=_font(13), fill=COLOURS["accent"])
    draw.text((90, 40), name, font=_font(26), fill=COLOURS["white"])

    # Tags row
    tags = recipe.get("tags", [])
    tx = 90
    ty = 82
    for tag in tags[:4]:
        tw = len(tag) * 7 + 12
        draw.rounded_rectangle([(tx, ty), (tx + tw, ty + 18)], radius=9, fill=COLOURS["accent"])
        draw.text((tx + 6, ty + 2), tag, font=_font_reg(10), fill=COLOURS["white"])
        tx += tw + 8

    # ── KPI strip ─────────────────────────────────────────────────────────────
    y = 118
    draw.rectangle([(0, y), (W, y + 58)], fill=COLOURS["tag_bg"])
    kpis = [
        ("Yield", f"{recipe['yield_amount']} units"),
        ("Total Cost", f"Rs. {recipe['total_cost']:.0f}"),
        ("Sell Price", f"Rs. {recipe['sell_price']:.0f}"),
        ("Margin", f"{recipe['margin_pct']:.0f}%"),
        ("Overhead", f"Rs. {recipe['overhead_cost']:.0f}"),
    ]
    kw = W // len(kpis)
    for i, (lbl, val) in enumerate(kpis):
        x = i * kw + kw // 2
        draw.text((x, y + 8), lbl, font=_font_reg(10), fill=COLOURS["text_mid"], anchor="mm")
        draw.text((x, y + 28), val, font=_font(13), fill=COLOURS["tag_text"], anchor="mm")

    # ── Section: Description ─────────────────────────────────────────────────
    y = 188
    draw.text((20, y), "Description", font=_font(14), fill=COLOURS["accent"])
    draw.line([(20, y + 20), (W - 20, y + 20)], fill=COLOURS["divider"], width=1)
    y += 28
    desc = recipe.get("description", "")
    # word-wrap at 70 chars
    words = desc.split()
    lines, line = [], []
    for w in words:
        if sum(len(x) + 1 for x in line) + len(w) > 70:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    for ln in lines[:3]:
        draw.text((20, y), ln, font=_font_reg(12), fill=COLOURS["text_mid"])
        y += 17

    # ── Section: Ingredients ─────────────────────────────────────────────────
    y += 10
    draw.text((20, y), "Ingredients", font=_font(14), fill=COLOURS["accent"])
    draw.line([(20, y + 20), (W - 20, y + 20)], fill=COLOURS["divider"], width=1)
    y += 28

    # Column headers
    draw.text((20, y), "Ingredient", font=_font_reg(11), fill=COLOURS["text_light"])
    draw.text((310, y), "Qty", font=_font_reg(11), fill=COLOURS["text_light"])
    draw.text((400, y), "Cost (Rs.)", font=_font_reg(11), fill=COLOURS["text_light"])
    draw.text((500, y), "Yield%", font=_font_reg(11), fill=COLOURS["text_light"])
    y += 18

    row_h = 24
    for i, ing in enumerate(recipe["ingredients"]):
        row_bg = COLOURS["card_bg"] if i % 2 == 0 else COLOURS["divider"]
        draw.rectangle([(16, y - 2), (W - 16, y + row_h - 4)], fill=row_bg)
        draw.text((20, y), ing["ingredient_name"][:28], font=_font_reg(11), fill=COLOURS["text_dark"])
        draw.text((310, y), f"{ing['required_quantity']:.2f}", font=_font_reg(11), fill=COLOURS["text_mid"])
        draw.text((400, y), f"{ing['cost']:.2f}", font=_font_reg(11), fill=COLOURS["text_mid"])
        draw.text((500, y), f"{ing['yield_amount'] * 100:.0f}%", font=_font_reg(11), fill=COLOURS["text_mid"])
        y += row_h
        if y > 690:
            draw.text((20, y), f"  ... +{len(recipe['ingredients']) - i - 1} more", font=_font_reg(10), fill=COLOURS["text_light"])
            y += 16
            break

    # ── Section: Method (abbreviated) ────────────────────────────────────────
    if y < 680:
        y += 10
        draw.text((20, y), "Method", font=_font(14), fill=COLOURS["accent"])
        draw.line([(20, y + 20), (W - 20, y + 20)], fill=COLOURS["divider"], width=1)
        y += 28
        for step_num, step in enumerate(recipe.get("method", [])[:4], 1):
            step_text = f"{step_num}. {step}"
            if len(step_text) > 72:
                step_text = step_text[:69] + "..."
            draw.text((20, y), step_text, font=_font_reg(11), fill=COLOURS["text_mid"])
            y += 17
            if y > 760:
                break

    # ── Footer ────────────────────────────────────────────────────────────────
    draw.rectangle([(0, H - 40), (W, H)], fill=COLOURS["header_bg"])
    draw.text((20, H - 26), "BakeManage ERP  •  Bakery Operations Platform  •  2026", font=_font_reg(10), fill=COLOURS["accent"])
    draw.text((W - 140, H - 26), f"v1.5 | {datetime.now().strftime('%d %b %Y')}", font=_font_reg(10), fill=COLOURS["text_light"])

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def generate_video_thumbnail(title: str, category: str, duration: str) -> str:
    """Render a video thumbnail card (400×225 = 16:9) and return base64 JPEG."""
    if not PIL_AVAILABLE:
        return ""

    W, H = 400, 225
    cat_colours = {
        "recipe":   (120, 53, 15),
        "training": (15, 80, 120),
        "quality":  (15, 120, 60),
        "vendor":   (80, 15, 120),
    }
    bg = cat_colours.get(category, (80, 80, 80))
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Gradient-like overlay
    for y in range(H):
        alpha = int(80 * (1 - y / H))
        draw.line([(0, y), (W, y)], fill=tuple(min(c + alpha, 255) for c in bg))

    # Play button
    cx, cy, r = W // 2, H // 2 - 10, 32
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(255, 255, 255, 180))
    draw.polygon([(cx - 10, cy - 16), (cx - 10, cy + 16), (cx + 18, cy)], fill=bg)

    # Title
    words = title.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:]) if len(words) > 4 else ""
    draw.text((W // 2, H - 48), line1, font=_font(14), fill=COLOURS["white"], anchor="mm")
    if line2:
        draw.text((W // 2, H - 28), line2, font=_font_reg(12), fill=COLOURS["accent"], anchor="mm")

    # Duration badge
    draw.rounded_rectangle([(W - 60, H - 22), (W - 4, H - 4)], radius=4, fill=(0, 0, 0))
    draw.text((W - 32, H - 13), duration, font=_font(10), fill=COLOURS["white"], anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


# ── Master recipe definitions ─────────────────────────────────────────────────
RECIPES = [
    {
        "name": "Classic Sourdough Loaf",
        "overhead_cost": 35.0,
        "yield_amount": 2,
        "sell_price": 180.0,
        "tags": ["Bread", "Sourdough", "Artisan"],
        "description": "Slow-fermented sourdough with 78% hydration, developed over 24 hours. Deep caramel crust, open crumb. A flagship product for premium bakery positioning.",
        "method": [
            "Mix Bread Flour and Chakki Atta with water, autolyse 45 min",
            "Add starter and salt, fold every 30 min × 4 during 4-hr bulk fermentation",
            "Pre-shape, bench rest 30 min, final shape into banneton",
            "Cold retard 12-14 hrs at 4°C. Score and bake 230°C, steam first 20 min",
        ],
        "ingredients": [
            {"name": "Bread Flour (High Gluten)", "qty": 0.400, "yield": 0.95},
            {"name": "Chakki Atta (Whole Wheat)", "qty": 0.100, "yield": 0.95},
            {"name": "Salt (Tata Iodised)", "qty": 0.010, "yield": 1.0},
            {"name": "Fresh Yeast (Instant)",   "qty": 0.005, "yield": 1.0},
            {"name": "Bread Packaging Bags (Small)", "qty": 2,    "yield": 1.0},
        ],
    },
    {
        "name": "Butter Croissant",
        "overhead_cost": 45.0,
        "yield_amount": 12,
        "sell_price": 85.0,
        "tags": ["Pastry", "Laminated", "French"],
        "description": "27-layer laminated pastry using high-grade unsalted butter. Flaky, shatteringly crisp exterior with honeycomb-soft interior. The gold standard for premium bakeries.",
        "method": [
            "Make détrempe: Maida, milk, sugar, salt, yeast, Amul Butter 60g. Mix to smooth dough",
            "Chill 1 hr. Laminate with 250g butter block — 3 double folds with 30 min rests",
            "Roll 4mm, cut triangles 8×20cm, shape and proof 2.5 hrs at 26°C / 75% RH",
            "Egg wash twice. Bake 190°C fan for 18–20 min until deep golden",
        ],
        "ingredients": [
            {"name": "Maida (Refined Flour)",      "qty": 0.500, "yield": 0.92},
            {"name": "Amul Butter (Unsalted)",     "qty": 0.310, "yield": 1.0},
            {"name": "Refined Sugar",              "qty": 0.060, "yield": 1.0},
            {"name": "Salt (Tata Iodised)",        "qty": 0.010, "yield": 1.0},
            {"name": "Fresh Yeast (Instant)",      "qty": 0.015, "yield": 1.0},
            {"name": "Full Cream Milk (Amul)",     "qty": 0.280, "yield": 1.0},
            {"name": "Pastry Boxes (Assorted)",    "qty": 2,     "yield": 1.0},
        ],
    },
    {
        "name": "Eggless Chocolate Cake",
        "overhead_cost": 60.0,
        "yield_amount": 1,
        "sell_price": 650.0,
        "tags": ["Cake", "Eggless", "Chocolate", "Celebration"],
        "description": "Rich, moist eggless chocolate sponge with whipped chocolate ganache frosting. Uses curd as egg replacer. Best-seller for occasions and celebrations.",
        "method": [
            "Sift Maida, Cocoa Powder, Baking Soda, Baking Powder. Combine dry ingredients",
            "Whisk vegetable oil, condensed milk, curd, Vanilla Extract. Fold into dry",
            "Bake 175°C for 30 min. Cool completely before frosting",
            "Melt Dark Chocolate Chips with Fresh Cream for ganache. Frost and decorate with Almond Flakes",
        ],
        "ingredients": [
            {"name": "Maida (Refined Flour)",      "qty": 0.200, "yield": 0.95},
            {"name": "Cocoa Powder (Morde)",       "qty": 0.050, "yield": 1.0},
            {"name": "Dark Chocolate Chips",       "qty": 0.150, "yield": 1.0},
            {"name": "Refined Sugar",              "qty": 0.180, "yield": 1.0},
            {"name": "Baking Soda",                "qty": 0.005, "yield": 1.0},
            {"name": "Baking Powder (Weikfield)",  "qty": 0.008, "yield": 1.0},
            {"name": "Fresh Cream (Amul)",         "qty": 0.200, "yield": 1.0},
            {"name": "Vanilla Extract",            "qty": 0.010, "yield": 1.0},
            {"name": "Almond Flakes",              "qty": 0.030, "yield": 1.0},
            {"name": "Sunflower Oil",              "qty": 0.080, "yield": 1.0},
            {"name": "Cake Boxes (6-inch)",        "qty": 1,     "yield": 1.0},
        ],
    },
    {
        "name": "Whole Wheat Multigrain Bread",
        "overhead_cost": 22.0,
        "yield_amount": 2,
        "sell_price": 120.0,
        "tags": ["Bread", "Healthy", "Multigrain"],
        "description": "Nutritious sandwich loaf made with 60% whole wheat and seeds. Soft crumb, nutty flavour. High-demand with health-conscious customers and corporate tiffin services.",
        "method": [
            "Mix Chakki Atta, Bread Flour, Semolina, Sesame Seeds, Poppy Seeds",
            "Add salt, yeast, sunflower oil, warm water. Knead 10 min",
            "Bulk ferment 90 min, shape into loaf tins, proof 45 min",
            "Bake 200°C for 28 min. Cool on wire rack min 1 hr before slicing",
        ],
        "ingredients": [
            {"name": "Chakki Atta (Whole Wheat)", "qty": 0.360, "yield": 0.95},
            {"name": "Bread Flour (High Gluten)", "qty": 0.140, "yield": 0.95},
            {"name": "Semolina (Sooji)",          "qty": 0.050, "yield": 1.0},
            {"name": "Sesame Seeds",              "qty": 0.020, "yield": 1.0},
            {"name": "Poppy Seeds",               "qty": 0.015, "yield": 1.0},
            {"name": "Salt (Tata Iodised)",       "qty": 0.010, "yield": 1.0},
            {"name": "Dry Active Yeast",          "qty": 0.008, "yield": 1.0},
            {"name": "Sunflower Oil",             "qty": 0.020, "yield": 1.0},
            {"name": "Bread Packaging Bags (Small)", "qty": 2,  "yield": 1.0},
        ],
    },
    {
        "name": "Butter Cookies (Nan Khatai)",
        "overhead_cost": 18.0,
        "yield_amount": 24,
        "sell_price": 12.0,
        "tags": ["Cookie", "Indian", "Festive"],
        "description": "Traditional Indian shortbread cookies with cardamom and ghee aroma. Crumbly melt-in-mouth texture. Popular for festivals and as gift box items throughout the year.",
        "method": [
            "Cream Vegetable Shortening and Powdered Icing Sugar until light and fluffy",
            "Add Cardamom Powder and Vanilla Extract. Fold in Maida + Semolina",
            "Roll walnut-sized balls, flatten slightly, indent with almond",
            "Bake 160°C for 18 min until lightly golden. Cool completely before packaging",
        ],
        "ingredients": [
            {"name": "Maida (Refined Flour)",     "qty": 0.200, "yield": 0.95},
            {"name": "Semolina (Sooji)",          "qty": 0.050, "yield": 1.0},
            {"name": "Vegetable Shortening",      "qty": 0.120, "yield": 1.0},
            {"name": "Powdered Icing Sugar",      "qty": 0.080, "yield": 1.0},
            {"name": "Cardamom Powder",           "qty": 0.003, "yield": 1.0},
            {"name": "Vanilla Extract",           "qty": 0.005, "yield": 1.0},
            {"name": "Almond Flakes",             "qty": 0.020, "yield": 1.0},
        ],
    },
    {
        "name": "Danish Pastry (Fruit Swirl)",
        "overhead_cost": 50.0,
        "yield_amount": 10,
        "sell_price": 90.0,
        "tags": ["Pastry", "Laminated", "Danish"],
        "description": "Enriched laminated dough with raisin and chocolate filling, spiral-shaped. Four-stage lamination gives 16 distinct butter layers. Weekend flagship item at premium price point.",
        "method": [
            "Prepare enriched dough: Maida, butter, sugar, milk, yeast, eggs. Mix to windowpane",
            "Chill 1 hr. Laminate with 200g butter, 2 double folds with 30 min rests each",
            "Roll to 5mm, spread Vanilla Extract syrup, scatter Raisins and Dark Chocolate Chips",
            "Roll tight, slice 3cm discs, proof 2 hrs. Bake 185°C, 16 min. Glaze warm",
        ],
        "ingredients": [
            {"name": "Maida (Refined Flour)",     "qty": 0.450, "yield": 0.92},
            {"name": "Amul Butter (Unsalted)",    "qty": 0.250, "yield": 1.0},
            {"name": "Refined Sugar",             "qty": 0.070, "yield": 1.0},
            {"name": "Full Cream Milk (Amul)",    "qty": 0.150, "yield": 1.0},
            {"name": "Fresh Yeast (Instant)",     "qty": 0.012, "yield": 1.0},
            {"name": "Raisins (Golden)",          "qty": 0.080, "yield": 1.0},
            {"name": "Dark Chocolate Chips",      "qty": 0.060, "yield": 1.0},
            {"name": "Vanilla Extract",           "qty": 0.008, "yield": 1.0},
            {"name": "Pastry Boxes (Assorted)",   "qty": 2,     "yield": 1.0},
        ],
    },
    {
        "name": "Focaccia with Rosemary & Sea Salt",
        "overhead_cost": 28.0,
        "yield_amount": 3,
        "sell_price": 140.0,
        "tags": ["Bread", "Italian", "Olive Oil"],
        "description": "High-hydration (85%) open-crumb Italian flatbread with generous olive oil, rosemary, and flaked sea salt. Baked in sheet trays for consistent dimpling and golden crust.",
        "method": [
            "Mix Bread Flour, salt, yeast with water to shaggy dough. Stretch and fold 4×",
            "Bulk ferment 4 hrs, transfer to oiled tray. Dimple generously, drizzle Sunflower Oil",
            "Scatter Sesame Seeds and Salt on top. Proof 45 min",
            "Bake 220°C for 22 min until deep golden with crispy base. Slice when cooled 20 min",
        ],
        "ingredients": [
            {"name": "Bread Flour (High Gluten)", "qty": 0.500, "yield": 0.95},
            {"name": "Salt (Tata Iodised)",       "qty": 0.012, "yield": 1.0},
            {"name": "Dry Active Yeast",          "qty": 0.006, "yield": 1.0},
            {"name": "Sunflower Oil",             "qty": 0.060, "yield": 1.0},
            {"name": "Sesame Seeds",              "qty": 0.015, "yield": 1.0},
            {"name": "Bread Packaging Bags (Small)", "qty": 3, "yield": 1.0},
        ],
    },
    {
        "name": "Almond Financiers",
        "overhead_cost": 40.0,
        "yield_amount": 18,
        "sell_price": 55.0,
        "tags": ["Petit Four", "Almond", "French"],
        "description": "Classic French almond cakes made with beurre noisette (browned butter). Crisp caramelized exterior, moist almond-rich interior. High-margin petit four for café menus.",
        "method": [
            "Brown Amul Butter Salted in pan until nutty hazelnut aroma. Strain and cool",
            "Whisk egg whites (not stiff), Powdered Icing Sugar, Maida, Almond Flakes",
            "Fold in warm browned butter. Rest batter 1 hr refrigerated",
            "Fill greased financier moulds 3/4 full. Bake 200°C for 12 min until risen and golden",
        ],
        "ingredients": [
            {"name": "Amul Butter (Salted)",      "qty": 0.120, "yield": 1.0},
            {"name": "Maida (Refined Flour)",     "qty": 0.080, "yield": 0.95},
            {"name": "Powdered Icing Sugar",      "qty": 0.160, "yield": 1.0},
            {"name": "Almond Flakes",             "qty": 0.100, "yield": 1.0},
            {"name": "Vanilla Extract",           "qty": 0.005, "yield": 1.0},
        ],
    },
    {
        "name": "Semolina Cake (Basbousa)",
        "overhead_cost": 20.0,
        "yield_amount": 16,
        "sell_price": 40.0,
        "tags": ["Cake", "Middle Eastern", "Semolina"],
        "description": "Dense, syrup-soaked semolina cake with coconut and rose water. Very low ingredient cost, extremely high margin. Increasingly popular in North Indian bakeries and sweet shops.",
        "method": [
            "Mix Semolina, Refined Sugar, Milk Powder, Baking Powder, Sunflower Oil",
            "Add Full Cream Milk to bind. Pour into greased tray, level and top with Almond Flakes",
            "Bake 180°C for 25 min until golden. Score into diamonds while warm",
            "Pour hot sugar syrup with Cardamom Powder over. Cool 30 min before serving",
        ],
        "ingredients": [
            {"name": "Semolina (Sooji)",          "qty": 0.300, "yield": 1.0},
            {"name": "Refined Sugar",             "qty": 0.150, "yield": 1.0},
            {"name": "Milk Powder",               "qty": 0.050, "yield": 1.0},
            {"name": "Baking Powder (Weikfield)", "qty": 0.008, "yield": 1.0},
            {"name": "Sunflower Oil",             "qty": 0.060, "yield": 1.0},
            {"name": "Full Cream Milk (Amul)",    "qty": 0.120, "yield": 1.0},
            {"name": "Almond Flakes",             "qty": 0.040, "yield": 1.0},
            {"name": "Cardamom Powder",           "qty": 0.003, "yield": 1.0},
            {"name": "Pastry Boxes (Assorted)",   "qty": 1,     "yield": 1.0},
        ],
    },
    {
        "name": "Rye & Sesame Crackers",
        "overhead_cost": 15.0,
        "yield_amount": 40,
        "sell_price": 8.0,
        "tags": ["Cracker", "Artisan", "Snack"],
        "description": "Crisp artisan crackers with Chakki Atta and sesame. Very long shelf life — ideal for hampers, gifting, and café companion for cheese boards. Zero-waste trim goes to breadcrumbs.",
        "method": [
            "Mix Chakki Atta, Maida, Sesame Seeds, Salt, Baking Soda with Sunflower Oil and water",
            "Knead briefly to smooth dough. Rest 20 min covered",
            "Roll paper-thin (2mm), cut into rectangles, prick with fork",
            "Bake 170°C for 14–16 min until crisp and golden. Cool completely before packing",
        ],
        "ingredients": [
            {"name": "Chakki Atta (Whole Wheat)", "qty": 0.200, "yield": 0.95},
            {"name": "Maida (Refined Flour)",     "qty": 0.100, "yield": 0.95},
            {"name": "Sesame Seeds",              "qty": 0.040, "yield": 1.0},
            {"name": "Salt (Tata Iodised)",       "qty": 0.008, "yield": 1.0},
            {"name": "Baking Soda",               "qty": 0.003, "yield": 1.0},
            {"name": "Sunflower Oil",             "qty": 0.030, "yield": 1.0},
        ],
    },
    {
        "name": "Dark Chocolate Brownies",
        "overhead_cost": 30.0,
        "yield_amount": 16,
        "sell_price": 60.0,
        "tags": ["Brownie", "Chocolate", "Fudgy"],
        "description": "Dense, fudgy brownies with 65% cocoa dark chocolate and cocoa powder. Shiny crinkle top from dissolved sugar. High-demand all-day café item with excellent repeat purchase rate.",
        "method": [
            "Melt Dark Chocolate Chips with Amul Butter Salted 100g over bain-marie",
            "Whisk Refined Sugar and Brown Sugar into melted chocolate. Add Vanilla Extract",
            "Fold in Cocoa Powder, then Maida. Do not overmix. Pour into 20×20cm pan",
            "Bake 165°C for 22 min. Centre should wobble slightly. Cool 1 hr before cutting",
        ],
        "ingredients": [
            {"name": "Dark Chocolate Chips",      "qty": 0.200, "yield": 1.0},
            {"name": "Amul Butter (Salted)",      "qty": 0.100, "yield": 1.0},
            {"name": "Refined Sugar",             "qty": 0.140, "yield": 1.0},
            {"name": "Brown Sugar",               "qty": 0.060, "yield": 1.0},
            {"name": "Cocoa Powder (Morde)",      "qty": 0.030, "yield": 1.0},
            {"name": "Maida (Refined Flour)",     "qty": 0.060, "yield": 0.95},
            {"name": "Vanilla Extract",           "qty": 0.008, "yield": 1.0},
            {"name": "Cake Boxes (6-inch)",       "qty": 1,     "yield": 1.0},
        ],
    },
    {
        "name": "Cinnamon Raisin Loaf",
        "overhead_cost": 25.0,
        "yield_amount": 2,
        "sell_price": 160.0,
        "tags": ["Bread", "Enriched", "Breakfast"],
        "description": "Soft enriched bread swirled with cinnamon sugar and golden raisins. Milk-and-butter enriched dough gives pillowy crumb. Top-seller for weekend brunches and gift hampers.",
        "method": [
            "Make enriched dough: Bread Flour, Milk Powder, Refined Sugar, Butter, Yeast, milk. Knead 12 min",
            "Bulk ferment 2 hrs. Roll out to rectangle, brush with Brown Sugar and cinnamon mixture",
            "Scatter Raisins evenly. Roll tight, place seam-down in loaf tin",
            "Proof 1.5 hrs. Bake 185°C for 30 min. Brush with butter while warm",
        ],
        "ingredients": [
            {"name": "Bread Flour (High Gluten)", "qty": 0.450, "yield": 0.95},
            {"name": "Milk Powder",               "qty": 0.030, "yield": 1.0},
            {"name": "Refined Sugar",             "qty": 0.040, "yield": 1.0},
            {"name": "Brown Sugar",               "qty": 0.060, "yield": 1.0},
            {"name": "Amul Butter (Unsalted)",    "qty": 0.050, "yield": 1.0},
            {"name": "Fresh Yeast (Instant)",     "qty": 0.010, "yield": 1.0},
            {"name": "Raisins (Golden)",          "qty": 0.100, "yield": 1.0},
            {"name": "Salt (Tata Iodised)",       "qty": 0.009, "yield": 1.0},
            {"name": "Full Cream Milk (Amul)",    "qty": 0.250, "yield": 1.0},
            {"name": "Bread Packaging Bags (Small)", "qty": 2, "yield": 1.0},
        ],
    },
    {
        "name": "Pav (Dinner Rolls)",
        "overhead_cost": 12.0,
        "yield_amount": 12,
        "sell_price": 12.0,
        "tags": ["Bread", "Indian", "Street Food", "High Volume"],
        "description": "Soft, butter-glazed Indian dinner rolls — essential product for any Indian bakery. High volume, low food cost, reliable daily seller. Pairs with vada pav, bhaji, and egg burji.",
        "method": [
            "Mix Maida, Refined Sugar, Salt, Fresh Yeast. Add milk and Butter, knead 8 min",
            "Bulk ferment 1.5 hrs. Divide into 60g balls, roll tight without tearing surface",
            "Arrange in greased tray touching each other. Proof 45 min",
            "Brush with milk. Bake 190°C, 16 min. Brush immediately with Amul Butter while hot",
        ],
        "ingredients": [
            {"name": "Maida (Refined Flour)",     "qty": 0.500, "yield": 0.95},
            {"name": "Amul Butter (Salted)",      "qty": 0.040, "yield": 1.0},
            {"name": "Refined Sugar",             "qty": 0.025, "yield": 1.0},
            {"name": "Salt (Tata Iodised)",       "qty": 0.008, "yield": 1.0},
            {"name": "Fresh Yeast (Instant)",     "qty": 0.015, "yield": 1.0},
            {"name": "Full Cream Milk (Amul)",    "qty": 0.280, "yield": 1.0},
        ],
    },
]


# ── Video / training media library ───────────────────────────────────────────
VIDEO_ASSETS = [
    {
        "title": "Lamination Technique: Croissant Dough",
        "category": "recipe",
        "description": "Step-by-step 3-fold butter lamination for croissants. Shows correct butter temperature, lock-in technique, and how to detect over-worked gluten.",
        "duration_seconds": 420,
        "file_size_kb": 38400,
        "tags": "croissant,lamination,technique,pastry",
        "recipe_name": "Butter Croissant",
    },
    {
        "title": "Sourdough Scoring Patterns",
        "category": "recipe",
        "description": "Demonstrates 6 scoring patterns for sourdough loaves — ear angle, depth, and pressure. Explains how scoring controls oven spring and crust aesthetics.",
        "duration_seconds": 310,
        "file_size_kb": 28200,
        "tags": "sourdough,scoring,technique,artisan",
        "recipe_name": "Classic Sourdough Loaf",
    },
    {
        "title": "Proofing Chamber Setup & Calibration",
        "category": "training",
        "description": "How to calibrate the proofing chamber — setting temperature 26–28°C and humidity 70–78%. Includes CO2 sensor placement and anomaly alert threshold configuration.",
        "duration_seconds": 540,
        "file_size_kb": 49000,
        "tags": "proofing,calibration,training,equipment",
        "recipe_name": None,
    },
    {
        "title": "Oven Temperature Mapping — Deck Oven",
        "category": "training",
        "description": "Thermal mapping exercise using 12-point temperature logger in a 3-deck oven. Identifies hot zones and rotation schedule to ensure even baking across all products.",
        "duration_seconds": 780,
        "file_size_kb": 71000,
        "tags": "oven,calibration,training,equipment",
        "recipe_name": None,
    },
    {
        "title": "Browning Score: Visual Quality Guide",
        "category": "quality",
        "description": "Shows the 0–100 browning calibration scale used by BakeManage Quality Control. Demonstrates reject vs. accept examples for bread, pastry, cookies, and cakes.",
        "duration_seconds": 290,
        "file_size_kb": 26500,
        "tags": "quality,browning,training,colour",
        "recipe_name": None,
    },
    {
        "title": "Chocolate Brownie Fudginess Test",
        "category": "quality",
        "description": "How to perform the skewer + press test to ensure correct moisture retention in brownies. Explains the difference between underbaked, perfect, and overbaked texture signatures.",
        "duration_seconds": 180,
        "file_size_kb": 16400,
        "tags": "quality,brownie,texture,testing",
        "recipe_name": "Dark Chocolate Brownies",
    },
    {
        "title": "Vendor Invoice Data Entry — Live Demo",
        "category": "vendor",
        "description": "Live walkthrough of uploading a vendor invoice image through BakeManage Injection. Shows OCR extraction, context classification, and automatic stock update flow.",
        "duration_seconds": 360,
        "file_size_kb": 33000,
        "tags": "injection,invoice,vendor,workflow",
        "recipe_name": None,
    },
    {
        "title": "Bulk Ordering Strategy — Flour & Sugar",
        "category": "vendor",
        "description": "Negotiation and ordering strategy for the two highest-cost staples. Shows volume threshold analysis, seasonal pricing patterns, and how to use vendor comparison data in BakeManage.",
        "duration_seconds": 490,
        "file_size_kb": 44800,
        "tags": "vendor,cost,flour,strategy",
        "recipe_name": None,
    },
    {
        "title": "Pav Shaping — High Speed Production",
        "category": "recipe",
        "description": "High-speed shaping technique for 12-pav batches. Shows how to maintain consistent 60g weight, tight surface tension, and tray spacing for uniform proofing.",
        "duration_seconds": 240,
        "file_size_kb": 22000,
        "tags": "pav,shaping,production,speed",
        "recipe_name": "Pav (Dinner Rolls)",
    },
    {
        "title": "Daily Bakery Opening Checklist — Operations",
        "category": "training",
        "description": "Complete 7-point opening checklist: oven preheat, proofing chamber check, stock count, expiry review, dough prep schedule, quality log start, and system health check.",
        "duration_seconds": 620,
        "file_size_kb": 56800,
        "tags": "operations,checklist,training,daily",
        "recipe_name": None,
    },
]


# ── DB seeding ────────────────────────────────────────────────────────────────
def get_inventory_price_map(session: Session) -> dict[str, float]:
    """Build a {name: unit_price} map from inventory. Uses highest-quality price."""
    rows = session.execute(
        text("SELECT name, MIN(unit_price) as unit_price FROM inventory_items GROUP BY name")
    ).fetchall()
    return {r[0]: float(r[1]) for r in rows}


def seed_recipes(session: Session) -> dict[int, dict]:
    """Insert all recipes + ingredients. Returns {recipe_id: recipe_data}."""
    price_map = get_inventory_price_map(session)
    recipe_id_map: dict[int, dict] = {}

    for r_def in RECIPES:
        # Skip if already exists
        existing = session.execute(
            text("SELECT id FROM recipes WHERE name = :name"),
            {"name": r_def["name"]}
        ).fetchone()
        if existing:
            print(f"  SKIP (exists): {r_def['name']}")
            recipe_id_map[existing[0]] = r_def
            continue

        # Compute costs from inventory price map
        total_ingredient_cost = 0.0
        ingredients_with_cost = []
        for ing in r_def["ingredients"]:
            base_price = price_map.get(ing["name"], 50.0)  # fallback ₹50/unit
            cost = round(base_price * ing["qty"] / ing["yield"], 2)
            total_ingredient_cost += cost
            ingredients_with_cost.append({
                "ingredient_name": ing["name"],
                "required_quantity": ing["qty"],
                "cost": cost,
                "yield_amount": ing["yield"],
            })

        total_cost = round(total_ingredient_cost + r_def["overhead_cost"], 2)

        recipe = Recipe(
            name=r_def["name"],
            overhead_cost=r_def["overhead_cost"],
            yield_amount=r_def["yield_amount"],
        )
        session.add(recipe)
        session.flush()

        for ing in ingredients_with_cost:
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_name=ing["ingredient_name"],
                required_quantity=ing["required_quantity"],
                cost=ing["cost"],
                yield_amount=ing["yield_amount"],
            )
            session.add(ri)

        session.commit()

        r_def["_id"] = recipe.id
        r_def["total_cost"] = total_cost
        recipe_id_map[recipe.id] = r_def
        print(f"  ✓ Recipe: {r_def['name']} (id={recipe.id}, cost=Rs.{total_cost:.0f}, yield={r_def['yield_amount']})")

    return recipe_id_map


def seed_media(session: Session, recipe_id_map: dict[int, dict]) -> None:
    """Generate recipe PDF cards + video metadata and insert MediaAsset records."""
    # Build name-to-id map
    name_to_id = {}
    for rid, r in recipe_id_map.items():
        name_to_id[r["name"]] = rid

    total_assets = 0

    # ── Recipe PDF cards ─────────────────────────────────────────────────────
    for rid, r_def in recipe_id_map.items():
        # Check if asset exists
        existing = session.execute(
            text("SELECT id FROM media_assets WHERE title = :t"),
            {"t": f"Recipe Card: {r_def['name']}"}
        ).fetchone()
        if existing:
            print(f"  SKIP media (exists): Recipe Card: {r_def['name']}")
            continue

        r_def.setdefault("total_cost", 0)
        r_def.setdefault("sell_price", r_def.get("sell_price", r_def["total_cost"] * 1.5))
        r_def.setdefault("margin_pct", round(
            (r_def["sell_price"] - r_def["total_cost"]) / r_def["sell_price"] * 100
            if r_def["sell_price"] > 0 else 0, 1
        ))

        # Rebuild ingredients list for card rendering
        price_map = get_inventory_price_map(session)
        r_def_render = dict(r_def)
        r_def_render["ingredients"] = []
        for ing in r_def.get("ingredients", []):
            base_price = price_map.get(ing["name"], 50.0)
            cost = round(base_price * ing["qty"] / ing["yield"], 2)
            r_def_render["ingredients"].append({
                "ingredient_name": ing["name"],
                "required_quantity": ing["qty"],
                "cost": cost,
                "yield_amount": ing["yield"],
            })

        thumb = generate_recipe_card(r_def_render)
        tags_list = r_def.get("tags", [])
        fsize = len(thumb) * 3 // 4 // 1024 if thumb else 0  # rough base64 → bytes estimate

        asset = MediaAsset(
            title=f"Recipe Card: {r_def['name']}",
            asset_type="pdf",
            category="recipe",
            description=r_def.get("description", ""),
            file_size_kb=max(fsize, 180),
            tags=",".join(tags_list),
            recipe_id=rid,
            thumbnail_data=thumb,
            pdf_data=thumb,  # using JPEG card as PDF proxy for sandbox
        )
        session.add(asset)
        session.commit()
        total_assets += 1
        print(f"  ✓ PDF card: {r_def['name']}")

    # ── Video assets ─────────────────────────────────────────────────────────
    for v in VIDEO_ASSETS:
        existing = session.execute(
            text("SELECT id FROM media_assets WHERE title = :t"),
            {"t": v["title"]}
        ).fetchone()
        if existing:
            print(f"  SKIP video (exists): {v['title'][:40]}")
            continue

        rid = name_to_id.get(v["recipe_name"]) if v["recipe_name"] else None
        thumb = generate_video_thumbnail(v["title"], v["category"], _fmt_duration(v["duration_seconds"]))

        asset = MediaAsset(
            title=v["title"],
            asset_type="video",
            category=v["category"],
            description=v["description"],
            duration_seconds=v["duration_seconds"],
            file_size_kb=v["file_size_kb"],
            tags=v["tags"],
            recipe_id=rid,
            thumbnail_data=thumb,
        )
        session.add(asset)
        session.commit()
        total_assets += 1
        print(f"  ✓ Video: {v['title'][:45]}")

    print(f"\n  Total media assets created: {total_assets}")


def _fmt_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    with Session(engine) as session:
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║   BakeManage — Recipe & Media Library Seeder        ║")
        print("╚══════════════════════════════════════════════════════╝\n")

        print("► Seeding recipes...")
        recipe_id_map = seed_recipes(session)

        print("\n► Generating media library (PDFs + video metadata)...")
        seed_media(session, recipe_id_map)

        # ── Final count ───────────────────────────────────────────────────────
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║   FINAL STATE                                        ║")
        print("╚══════════════════════════════════════════════════════╝")
        for table in ["recipes", "recipe_ingredients", "media_assets"]:
            n = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:<25}: {n:>4}")
        print()


if __name__ == "__main__":
    main()
