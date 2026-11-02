// Shared header and footer. Text is filled in by hydrate() in data.js through data-copy.
const page = document.body.dataset.page || 'home';
const minimal = ['checkout', 'thanks'].includes(page);

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
       <a class="brand" href="index.html"><span data-copy="brand.name">Safeguard</span></a>
       <a class="back" href="index.html" data-copy="nav.back"></a>
     </div>`
  : `<div class="wrap bar">
       <a class="brand" href="index.html"><span data-copy="brand.name">Safeguard</span></a>
       <nav aria-label="Main">${navLinks}</nav>
       <a class="button small" href="product.html" data-copy="nav.preorder"></a>
     </div>`;

const footer = document.createElement('footer');
footer.className = 'site';
footer.innerHTML = `<div class="wrap foot">
  <a class="brand" href="index.html"><span data-copy="brand.name">Safeguard</span></a>
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
