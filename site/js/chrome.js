// Shared header and footer. Text is filled in by hydrate() in data.js through data-copy.
const page = document.body.dataset.page || 'home';
const minimal = ['checkout', 'thanks'].includes(page);

const logo = `<svg class="logo" viewBox="0 0 28 28" aria-hidden="true">
  <rect x="7" y="2" width="14" height="14" rx="3.5" fill="#d9d0c6" stroke="#a89c8f"/>
  <circle cx="10.6" cy="5.6" r="1.7" fill="#2a2a2e"/><circle cx="14.4" cy="5.6" r="1.7" fill="#2a2a2e"/>
  <rect x="4" y="9" width="20" height="17" rx="5" fill="#e3d8c9" stroke="#b5a690" stroke-width="1.5"/>
</svg>`;

const links = [
  ['index.html#shop', 'nav.shop'],
  ['index.html#how', 'nav.how'],
  ['index.html#faq', 'nav.faq'],
];

const navLinks = links.map(([href, key]) => `<a href="${href}" data-copy="${key}"></a>`).join('');

const header = document.createElement('header');
header.className = 'site';
header.innerHTML = minimal
  ? `<div class="wrap bar">
       <a class="brand" href="index.html">${logo}<span data-copy="brand.name">Safeguard</span></a>
       <a class="back" href="index.html" data-copy="nav.back"></a>
     </div>`
  : `<div class="wrap bar">
       <a class="brand" href="index.html">${logo}<span data-copy="brand.name">Safeguard</span></a>
       <nav aria-label="Main">${navLinks}</nav>
       <a class="button small" href="product.html" data-copy="nav.preorder"></a>
     </div>`;

const footer = document.createElement('footer');
footer.className = 'site';
footer.innerHTML = `<div class="wrap foot">
  <a class="brand" href="index.html">${logo}<span data-copy="brand.name">Safeguard</span></a>
  <nav aria-label="Footer">${navLinks}</nav>
  <p class="muted" data-copy="footer.disclaimer"></p>
</div>`;

const announce = document.createElement('div');
announce.className = 'announce';
announce.innerHTML = `<div class="wrap"><span data-copy="nav.announce"></span>${
  minimal ? '' : ' <a class="more" href="product.html" data-copy="nav.announceCta"></a>'
}</div>`;

document.body.prepend(header);
header.after(announce);
document.body.append(footer);
