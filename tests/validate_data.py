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
listings = load("data/amazon-listings.json") or []
doors = load("data/doors.json") or []
preorders = load("data/preorders.seed.json") or []
copy = load("site/copy.json") or {}

# products.json
product_keys = ["id", "name", "packSize", "unitPriceCents", "packPriceCents", "currency", "channel",
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
    if not (is_int(p["unitPriceCents"]) and is_int(p["packPriceCents"])):
        err(f"{label}: prices must be integer cents")
    elif p["packPriceCents"] != p["unitPriceCents"] * p["packSize"]:
        err(f"{label}: packPriceCents {p['packPriceCents']} != unitPriceCents x packSize")
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
        if p["channel"] != "website" or p["unitPriceCents"] != 872 or p["packPriceCents"] != 3488:
            err(f"{label}: must be website, 872 per unit, 3488 per pack")
        if p["shipping"].get("freeShipping") is not True:
            err(f"{label}: 4-pack must ship free")
    if p["id"] == "safeguard-single":
        if p["channel"] != "amazon" or p["unitPriceCents"] != 897:
            err(f"{label}: must be amazon at 897")
for needed in ("safeguard-4pack", "safeguard-single"):
    if needed not in by_id:
        err(f"products.json: missing {needed}")

# amazon-listings.json
for row in listings:
    label = f"amazon-listings.json[{row.get('productId')}]"
    if not check_keys(label, row, ["productId", "asin", "title", "priceCents", "listingUrl", "bullets",
                                   "packageCard", "brandReferralBonus"]):
        continue
    product = by_id.get(row["productId"])
    if not product or product["channel"] != "amazon":
        err(f"{label}: productId must match a product with channel amazon")
    elif row["priceCents"] != product["unitPriceCents"]:
        err(f"{label}: priceCents must equal the product's unitPriceCents")
    if not row["asin"].startswith("MOCK-"):
        err(f"{label}: asin must start with MOCK-")
    if not (isinstance(row["bullets"], list) and 0 < len(row["bullets"]) <= 5):
        err(f"{label}: bullets must have 1 to 5 entries")
    if row["brandReferralBonus"] is not True:
        err(f"{label}: brandReferralBonus must be true")
    card = row["packageCard"]
    if check_keys(f"{label}.packageCard", card, ["headline", "body", "url"]):
        if "utm_source=amazon" not in card["url"] or "utm_medium=package-card" not in card["url"]:
            err(f"{label}.packageCard.url: must include utm_source=amazon and utm_medium=package-card")
        if not card["url"].startswith("index.html"):
            err(f"{label}.packageCard.url: must point at the website 4-pack page (index.html)")
        if "safeguard-single" in card["url"]:
            err(f"{label}.packageCard.url: must not link to a single")
if not listings:
    err("amazon-listings.json: needs at least one listing")

# doors.json
for door in doors:
    label = f"doors.json[{door.get('id')}]"
    if not check_keys(label, door, ["id", "label", "smoothNonPorous", "benchTestStatus", "benchTestWeeks"]):
        continue
    if door["benchTestStatus"] not in ("untested", "pass", "fail"):
        err(f"{label}: benchTestStatus must be untested, pass or fail")
    if not is_int(door["benchTestWeeks"]):
        err(f"{label}: benchTestWeeks must be an integer")
    elif door["benchTestStatus"] == "untested" and door["benchTestWeeks"] != 0:
        err(f"{label}: untested doors must have benchTestWeeks 0")
if not doors:
    err("doors.json: needs at least one door")

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

# copy.json
def lookup(path):
    node = copy
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


for key in ["hero.headline", "hero.sub", "product.description", "product.materialsLine", "doors.note",
            "preorder.notice", "amazon.singlesNote", "footer.disclaimer"]:
    if not isinstance(lookup(key), str) or not lookup(key).strip():
        err(f"copy.json: missing or empty '{key}'")
if lookup("product.materialsLine") != "washable canvas with a soft-touch silicone back":
    err("copy.json: product.materialsLine must equal the marketing line from the PRD")

if errors:
    print(f"FAIL: {len(errors)} problem(s)")
    for message in errors:
        print(f"  - {message}")
    sys.exit(1)
print("OK: data contract holds")
