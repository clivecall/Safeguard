# Manual run-through

Start the server from the project folder: `python3 -m http.server 8000`, then open http://localhost:8000/site/

Automatic first:

- [ ] `python3 -I tests/validate_data.py` prints OK
- [ ] `python3 -I tests/check_claims.py` prints OK

Then by hand, in a browser:

- [ ] **4-pack path.** On `/site/`, open the 4-pack card, press Pre-order now, fill the form, submit. The quantity chosen on the product page carries into checkout. The confirmation shows a `MOCK-` id and $39.99. In dev tools, `localStorage["safeguard.preorders"]` holds the row with `source: "direct"`.
- [ ] **Quantity.** Set 2 packs: total shows $79.98.
- [ ] **No Amazon.** No page mentions Amazon, links to it, or offers a single. Checkout quantity is in 4-packs.
- [ ] **Doors.** `/site/doors.html` marks every finish untested. Smooth finishes say "Expected to hold", the rest say "Not recommended".
- [ ] **Google Sheet (only once `preorderEndpoint` is set).** Place a pre-order. The confirmation shows a `PO-` id, a new row appears in the sheet with the right total and source, and the checkout shows the privacy note. With the network off, submitting shows an error and stays on the form.
- [ ] **Test banner.** While `preorderEndpoint` is empty, every page shows the prototype banner. Once it is set, no page shows it.
- [ ] **Phone width.** In the device toolbar at 375px, no page scrolls sideways and the buy button is reachable. Check light and dark.
- [ ] **No payment data.** Checkout asks only for name, email and quantity, and says it is a pre-order.
