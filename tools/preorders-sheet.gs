// Google Apps Script that records website pre-orders in a Google Sheet.
//
// Setup:
// 1. Open https://sheets.new and name the sheet "Safeguard pre-orders".
// 2. Choose Extensions > Apps Script, replace the code there with this file, and save.
// 3. Choose Deploy > New deployment, then the gear icon > Web app.
//    Execute as: Me. Who has access: Anyone. Press Deploy and approve the access request.
// 4. Copy the Web app URL (it ends in /exec) into preorderEndpoint in data/settings.json.
//
// After editing this script, publish it with Deploy > Manage deployments > Edit > New version.

const PACK_PRICE_CENTS = 3999; // tests/validate_data.py checks this against data/products.json
const PRODUCT_ID = 'safeguard-4pack';
const MAX_PACKS = 10;
const SOURCES = ['direct', 'amazon-card', 'survey'];
const HEADERS = ['id', 'createdAt', 'source', 'productId', 'quantity', 'total', 'name', 'email', 'status'];
const TOTAL_COLUMN = HEADERS.indexOf('total') + 1;
const TOTAL_FORMAT = '$#,##0.00';

function reply(ok) {
  return ContentService.createTextOutput(JSON.stringify({ ok })).setMimeType(ContentService.MimeType.JSON);
}

// A leading = + - or @ would make the sheet run the text as a formula.
function plainText(value) {
  return /^[=+\-@]/.test(value) ? `'${value}` : value;
}

// Returns the sheet row, or null if the order is not valid.
function toRow(order) {
  const name = String(order.name || '').trim();
  const email = String(order.email || '').trim();
  const valid =
    /^PO-[A-Z0-9]{6,24}$/.test(order.id) &&
    SOURCES.includes(order.source) &&
    order.productId === PRODUCT_ID &&
    Number.isInteger(order.quantity) &&
    order.quantity >= 1 &&
    order.quantity <= MAX_PACKS &&
    name.length >= 1 &&
    name.length <= 100 &&
    email.length <= 254 &&
    /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  if (!valid) return null;
  return [
    order.id,
    new Date().toISOString(),
    order.source,
    PRODUCT_ID,
    order.quantity,
    (order.quantity * PACK_PRICE_CENTS) / 100, // The sheet is for people to read, so it shows dollars.
    plainText(name),
    plainText(email),
    'preorder',
  ];
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const order = JSON.parse(e.postData.contents);
    if (order.website) return reply(true); // Hidden form field: only bots fill it in.
    const row = toRow(order);
    if (!row) return reply(false);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);
    // A retry after a lost response sends the same id, so it must not add a second row.
    const seen = sheet.createTextFinder(order.id).matchEntireCell(true).findNext();
    if (!seen) {
      sheet.appendRow(row);
      sheet.getRange(sheet.getLastRow(), TOTAL_COLUMN).setNumberFormat(TOTAL_FORMAT);
    }
    return reply(true);
  } catch (err) {
    console.error(err);
    return reply(false);
  } finally {
    lock.releaseLock();
  }
}

// Opening the URL in a browser shows {"ok":true} when the deployment is reachable.
function doGet() {
  return reply(true);
}
