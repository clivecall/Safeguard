// Loads the mock data and fills pages from it. Pages never hardcode prices or copy.
const DATA_DIR = new URL('../../data/', import.meta.url);
const COPY_URL = new URL('../copy.json', import.meta.url);

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Could not load ${url} (${res.status})`);
  return res.json();
}

export async function loadAll() {
  const [products, settings, copy] = await Promise.all([
    getJSON(new URL('products.json', DATA_DIR)),
    getJSON(new URL('settings.json', DATA_DIR)),
    getJSON(COPY_URL),
  ]);
  return { products, settings, copy };
}

export function money(cents) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100);
}

export function getCopy(copy, key) {
  return key.split('.').reduce((obj, part) => (obj == null ? obj : obj[part]), copy);
}

// data-copy="hero.headline"            -> text from copy.json
// data-product="safeguard-4pack" data-field="packPriceCents" -> formatted price
export function hydrate(root, { products, copy }) {
  root.querySelectorAll('[data-copy]').forEach((el) => {
    const text = getCopy(copy, el.dataset.copy);
    if (typeof text === 'string') el.textContent = text;
  });
  root.querySelectorAll('[data-product]').forEach((el) => {
    const product = products.find((p) => p.id === el.dataset.product);
    if (!product) return;
    const value = product[el.dataset.field];
    el.textContent = el.dataset.field.endsWith('Cents') ? money(value) : String(value);
  });
}

// Shown until pre-orders are recorded, so a tester never mistakes this for a real order.
function showTestBanner(copy) {
  const banner = document.createElement('p');
  banner.className = 'mock-banner';
  banner.textContent = copy.preorder.testBanner;
  document.body.prepend(banner);
}

// Loads everything and hydrates the page. Shows a plain message if the data can't load.
export async function boot() {
  try {
    const data = await loadAll();
    hydrate(document, data);
    if (!data.settings.preorderEndpoint) showTestBanner(data.copy);
    return data;
  } catch (err) {
    const banner = document.createElement('p');
    banner.className = 'load-error';
    banner.textContent =
      'This page could not load its data. Start a local server from the project folder (python3 -m http.server 8000) and open http://localhost:8000/site/.';
    document.body.prepend(banner);
    throw err;
  }
}
