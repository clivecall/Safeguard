"""Scans customer-facing text for banned claims. Run: python3 -I tests/check_claims.py"""
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BANNED = [
    (r"\bapp\b", "implies an app (version 1 has no tech)"),
    (r"\bsensors?\b", "implies a sensor (version 1 has no tech)"),
    (r"\bNFC\b|\bnotifications?\b|\bbluetooth\b", "implies tech (version 1 has no tech)"),
    (r"\bguarantee[sd]?\b", "no guarantees"),
    (r"\bproven\b|\bproves?\b|\bclinically\b", "no proof claims (pilot has not run, research is mixed)"),
    (r"reduc\w*\s+(arguments?|fights?|tension|conflict)", "no claim that it reduces arguments"),
    (r"\b(improv\w*|boosts?)\s+(grades|sleep|focus|attention|memory)", "no health or grade claims"),
    (r"never\s+falls?", "no 'never falls' claim"),
    (r"fits\s+(every|all|any)\b", "pocket size is still open"),
    (r"drill-free", "use the PRD wording: no drilling and no adhesive"),
    (r"\bincludes?\s+(a\s+|the\s+|your\s+)?(charger|cable)|charger\s+included", "no charger is included"),
    (r"[★☆]|\bstars?\b|\b\d[\d,]*\s+(reviews?|ratings?)\b|bought in past month|best.?seller",
     "no ratings, review counts or sales badges"),
    (r"\b(spy|spying|monitor\w*|catch\w*|police|policing|surveil\w*)\b", "positioning: family routine, not control of the teen"),
    (r"\$\s?\d", "prices must come from data, not be hardcoded in text"),
]

errors = []


def scan(label, text):
    for pattern, reason in BANNED:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            errors.append(f"{label}: '{match.group(0)}' ({reason})")


def strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from strings(item)
    elif isinstance(node, dict):
        for item in node.values():
            yield from strings(item)


# Text in JSON files. Skip URL fields, which are not customer-facing prose.
for rel in ["site/copy.json", "data/amazon-listings.json", "data/products.json"]:
    data = json.loads((ROOT / rel).read_text())
    for text in strings(data):
        if not text.startswith(("http", "index.html", "amazon-preview", "img/")):
            scan(rel, text)

# Text in HTML pages, with scripts, styles and tags removed.
for page in sorted((ROOT / "site").glob("*.html")):
    html = page.read_text()
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    scan(f"site/{page.name}", unescape(re.sub(r"<[^>]+>", " ", html)))

# The checkout must never ask for payment details.
checkout = (ROOT / "site" / "checkout.html").read_text().lower()
for needle in ["cc-number", "cc-exp", "cc-csc", "card number", "cvv", "cvc", "credit card", "billing address"]:
    if needle in checkout:
        errors.append(f"site/checkout.html: payment field or wording '{needle}'")

if errors:
    print(f"FAIL: {len(errors)} problem(s)")
    for message in errors:
        print(f"  - {message}")
    sys.exit(1)
print("OK: no banned claims, no payment fields")
