// Remembers whether the visitor arrived from the card packed with an Amazon single.
const KEY = 'safeguard.source';

export function captureSource() {
  try {
    const params = new URLSearchParams(location.search);
    if (params.get('utm_source') === 'amazon' && params.get('utm_medium') === 'package-card') {
      sessionStorage.setItem(KEY, 'amazon-card');
    }
  } catch {
    // Storage can be blocked. The order then falls back to "direct".
  }
}

export function getSource() {
  try {
    return sessionStorage.getItem(KEY) || 'direct';
  } catch {
    return 'direct';
  }
}
