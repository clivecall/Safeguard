// Pre-order form. Saves to localStorage, and also records the order in the Google Sheet
// when data/settings.json has an endpoint. No payment data is collected.
import { boot, money } from './data.js';
import { getSource } from './source.js';

const STORAGE_KEY = 'safeguard.preorders';
const SEND_TIMEOUT_MS = 20000;
const { products, settings, copy } = await boot();
const pack = products.find((p) => p.id === 'safeguard-4pack');
const live = Boolean(settings.preorderEndpoint);

const form = document.getElementById('preorder-form');
const qty = document.getElementById('qty');
const total = document.getElementById('total');
const units = document.getElementById('units');
const submit = form.querySelector('button[type="submit"]');
const sendError = document.getElementById('send-error');
const privacy = document.getElementById('privacy');

// Kept across retries, so a retry after a lost response cannot add a second row.
let orderId = null;

function currentQty() {
  const n = Number.parseInt(qty.value, 10);
  return Number.isInteger(n) && n >= 1 ? Math.min(n, 10) : 1;
}

function render() {
  const n = currentQty();
  total.textContent = money(n * pack.packPriceCents);
  units.textContent = `${n} × 4-pack (${n * pack.packSize} Safeguards)`;
}

function readOrders() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function newOrderId() {
  const stamp = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`.toUpperCase();
  return `${live ? 'PO' : 'MOCK'}-${stamp}`;
}

// Sent as text/plain because Apps Script cannot answer a CORS preflight.
async function sendOrder(order) {
  const res = await fetch(settings.preorderEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain;charset=utf-8' },
    body: JSON.stringify({ ...order, website: form.elements.website.value }),
    signal: AbortSignal.timeout(SEND_TIMEOUT_MS),
  });
  const reply = await res.json();
  if (!reply.ok) throw new Error('The pre-order was not recorded');
}

const startQty = Number.parseInt(new URLSearchParams(location.search).get('qty'), 10);
if (Number.isInteger(startQty) && startQty >= 1) qty.value = Math.min(startQty, 10);

if (live) {
  privacy.textContent = `${copy.preorder.privacy} ${settings.contactEmail}.`;
  privacy.hidden = false;
}

qty.addEventListener('input', render);
render();

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const n = currentQty();
  orderId ??= newOrderId();
  const order = {
    id: orderId,
    createdAt: new Date().toISOString(),
    source: getSource(),
    productId: pack.id,
    quantity: n,
    totalCents: n * pack.packPriceCents,
    name: form.elements.name.value.trim(),
    email: form.elements.email.value.trim(),
    status: live ? 'preorder' : 'mock-preorder',
  };
  const label = submit.textContent;
  sendError.hidden = true;
  submit.disabled = true;
  submit.textContent = copy.preorder.sending;
  try {
    if (live) await sendOrder(order);
  } catch {
    sendError.hidden = false;
    submit.disabled = false;
    submit.textContent = label;
    return;
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...readOrders(), order]));
  } catch {
    // Storage blocked: the confirmation page still opens, without the saved details.
  }
  // The back button can restore this page, and a new submit there is a new order.
  orderId = null;
  submit.disabled = false;
  submit.textContent = label;
  location.href = `thanks.html?id=${encodeURIComponent(order.id)}`;
});
