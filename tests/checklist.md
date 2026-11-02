# Manual run-through

Start the server from the project folder: `python3 -m http.server 8000`, then open http://localhost:8000/site/

Automatic first:

- [ ] `python3 -I tests/validate_data.py` prints OK
- [ ] `python3 -I tests/check_claims.py` prints OK

Then by hand, in a browser:

- [ ] **4-pack path.** On `/site/`, open the 4-pack card, press Pre-order now, fill the form, submit. The quantity chosen on the product page carries into checkout. The confirmation shows a `MOCK-` id and $34.88. In dev tools, `localStorage["safeguard.preorders"]` holds the row with `source: "direct"`.
- [ ] **Quantity.** Set 2 packs: total shows $69.76.
- [ ] **Amazon funnel.** Open `/site/amazon-preview.html`. It shows the mock banner, the single at $8.97, and the package card. Press the card button. You land on the home page with `utm_source=amazon&utm_medium=package-card` in the URL. Place a pre-order. The saved row has `source: "amazon-card"`.
- [ ] **No single on the site.** The home page, door guide and checkout never offer a single for sale. The home page links to the Amazon preview for singles.
- [ ] **Doors.** `/site/doors.html` marks every finish untested. Smooth finishes say "Expected to hold", the rest say "Not recommended".
- [ ] **Phone width.** In the device toolbar at 375px, no page scrolls sideways and the buy button is reachable. Check light and dark.
- [ ] **No payment data.** Checkout asks only for name, email and quantity, and says it is a pre-order.
