"""Checks the mock data against the contract in CLAUDE.md. Run: python3 -I tests/validate_data.py"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def err(message):
    errors.append(message)


def load(path):
    try:
        return json.loads((ROOT / path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        err(f"{path}: cannot read ({exc})")
        return None


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_keys(label, row, required):
    for key in required:
        if key not in row:
            err(f"{label}: missing '{key}'")
    return all(key in row for key in required)


products = load("data/products.json") or []
settings = load("data/settings.json") or {}
preorders = load("data/preorders.seed.json") or []
copy = load("site/copy.json") or {}

# products.json
product_keys = ["id", "name", "packSize", "packPriceCents", "currency", "channel",
                "shipping", "status", "shipWindow", "cupCount", "materials", "image"]
by_id = {}
for p in products:
    label = f"products.json[{p.get('id')}]"
    if not check_keys(label, p, product_keys):
        continue
    by_id[p["id"]] = p
    if p["id"] not in ("safeguard-4pack", "safeguard-single"):
        err(f"{label}: unknown id")
    if p["packSize"] not in (1, 4):
        err(f"{label}: packSize must be 1 or 4")
    if not is_int(p["packPriceCents"]):
        err(f"{label}: prices must be integer cents")
    if p["currency"] != "USD":
        err(f"{label}: currency must be USD")
    if p["status"] != "preorder":
        err(f"{label}: status must be preorder in the MVP")
    if p["cupCount"] != 6:
        err(f"{label}: cupCount must be 6")
    if p["materials"] != ["cream cotton canvas", "cream silicone"]:
        err(f"{label}: materials must be exactly cream cotton canvas and cream silicone")
    if not (ROOT / "site" / p["image"]).exists():
        err(f"{label}: image not found at site/{p['image']}")
    if p["id"] == "safeguard-4pack":
        if p["channel"] != "website" or p["packPriceCents"] != 3999:
            err(f"{label}: must be website at 3999 per pack")
        if p["shipping"].get("freeShipping") is not True:
            err(f"{label}: 4-pack must ship free")
if "safeguard-4pack" not in by_id:
    err("products.json: missing safeguard-4pack")
if "safeguard-single" in by_id:
    err("products.json: the single is parked with Amazon")
if (ROOT / "data" / "amazon-listings.json").exists() or (ROOT / "site" / "amazon-preview.html").exists():
    err("Amazon files are parked and must not be published")

# preorders.seed.json
four_pack = by_id.get("safeguard-4pack", {})
for row in preorders:
    label = f"preorders.seed.json[{row.get('id')}]"
    if not check_keys(label, row, ["id", "createdAt", "source", "productId", "quantity", "totalCents",
                                   "name", "email", "status"]):
        continue
    if not row["id"].startswith("MOCK-"):
        err(f"{label}: id must start with MOCK-")
    if row["source"] not in ("direct", "amazon-card", "survey"):
        err(f"{label}: bad source")
    if row["productId"] != "safeguard-4pack":
        err(f"{label}: the website sells only the 4-pack")
    if not (is_int(row["quantity"]) and row["quantity"] >= 1):
        err(f"{label}: quantity must be an integer of at least 1")
    elif four_pack and row["totalCents"] != row["quantity"] * four_pack["packPriceCents"]:
        err(f"{label}: totalCents must equal quantity x packPriceCents")
    if not re.fullmatch(r"[^@\s]+@example\.com", row["email"]):
        err(f"{label}: seed emails must use example.com")
    if row["status"] != "mock-preorder":
        err(f"{label}: status must be mock-preorder")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T[\d:]+Z", row["createdAt"]):
        err(f"{label}: createdAt must be ISO 8601 (UTC)")

# settings.json
if check_keys("settings.json", settings, ["preorderEndpoint", "contactEmail"]):
    endpoint = settings["preorderEndpoint"]
    if endpoint and not re.fullmatch(r"https://script\.google\.com/macros/s/[\w-]+/exec", endpoint):
        err("settings.json: preorderEndpoint must be empty or an Apps Script /exec URL")
    if endpoint and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", settings["contactEmail"]):
        err("settings.json: contactEmail is required once preorderEndpoint is set")

# tools/preorders-sheet.gs keeps its own price because it runs on Google, not on the site.
script = (ROOT / "tools" / "preorders-sheet.gs").read_text()
if f"const PACK_PRICE_CENTS = {four_pack.get('packPriceCents')};" not in script:
    err("tools/preorders-sheet.gs: PACK_PRICE_CENTS must equal the 4-pack packPriceCents")

# copy.json
def lookup(path):
    node = copy
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


for key in ["hero.headline", "hero.sub", "product.description", "product.materialsLine", "doors.note", "faq.q7",
            "preorder.notice", "preorder.privacy", "preorder.sendError", "preorder.sending",
            "preorder.thanksBodyLive", "preorder.testBanner", "footer.disclaimer"]:
    if not isinstance(lookup(key), str) or not lookup(key).strip():
        err(f"copy.json: missing or empty '{key}'")
if lookup("product.materialsLine") != "washable canvas with a soft-touch silicone back":
    err("copy.json: product.materialsLine must equal the marketing line from the PRD")

# The door limits have no page of their own, so these are the only places customers see them.
note = (lookup("doors.note") or "").lower()
for phrase in ("smooth, non-porous", "not recommended"):
    if phrase not in note:
        err(f"copy.json: doors.note must say '{phrase}'")
for page in ("product.html", "index.html"):
    if 'data-copy="doors.note"' not in (ROOT / "site" / page).read_text():
        err(f"site/{page}: must show doors.note")
if (ROOT / "data" / "doors.json").exists() or (ROOT / "site" / "doors.html").exists():
    err("The doors page is removed and must not be published")

if errors:
    print(f"FAIL: {len(errors)} problem(s)")
    for message in errors:
        print(f"  - {message}")
    sys.exit(1)
print("OK: data contract holds")
