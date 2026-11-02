// Mock pre-order: saves to localStorage only. No payment data is collected.
import { boot, money } from './data.js';
import { getSource } from './source.js';

const STORAGE_KEY = 'safeguard.preorders';
const { products } = await boot();
const pack = products.find((p) => p.id === 'safeguard-4pack');

const form = document.getElementById('preorder-form');
const qty = document.getElementById('qty');
const total = document.getElementById('total');
const units = document.getElementById('units');

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

const startQty = Number.parseInt(new URLSearchParams(location.search).get('qty'), 10);
if (Number.isInteger(startQty) && startQty >= 1) qty.value = Math.min(startQty, 10);

qty.addEventListener('input', render);
render();

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const n = currentQty();
  const order = {
    id: `MOCK-${Date.now().toString(36).toUpperCase()}`,
    createdAt: new Date().toISOString(),
    source: getSource(),
    productId: pack.id,
    quantity: n,
    totalCents: n * pack.packPriceCents,
    name: form.elements.name.value.trim(),
    email: form.elements.email.value.trim(),
    status: 'mock-preorder',
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...readOrders(), order]));
  } catch {
    // Storage blocked: the confirmation page still opens, without the saved details.
  }
  location.href = `thanks.html?id=${encodeURIComponent(order.id)}`;
});
