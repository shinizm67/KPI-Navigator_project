/* HOME-VISUAL-01. Font, Office gap/radius, and zh-tw Home language route. */
'use strict';

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const fails = [];
function fail(msg) { fails.push(msg); }

const css = fs.readFileSync(path.join(root, 'app/home/home-shell.css'), 'utf8');
if (!css.includes("font-family: 'Orbitron', sans-serif;")) fail('EN sci-fi Orbitron missing');
if (!css.includes('html[lang="ja"] .home-window')) fail('JP font override missing');
if (!css.includes('html[lang="zh-TW"] .home-window')) fail('zh-TW font override missing');
if (!css.includes("font-family: 'BIZ UDPGothic', 'BIZ UDP Gothic', sans-serif;")) fail('BIZ font missing');
const office = css.split('body.office-mode .home-window {')[1] || '';
if (!office.includes('border-radius: 12px')) fail('office radius is not 12px');
if (!css.includes('body.office-mode.home-page .home-windows') || !css.includes('background: transparent;')) {
  fail('office gap background not transparent');
}
if (/body\.office-mode \.home-windows[\s\S]{0,80}background:\s*#000/.test(css)) fail('office gap still black');

function resolve(page, href) {
  let parts = path.posix.dirname(page).split('/');
  for (const seg of href.split('/')) {
    if (seg === '..') parts.pop();
    else if (seg && seg !== '.') parts.push(seg);
  }
  return parts.join('/');
}

const cases = [
  ['en/app/home/index.html', 'data-url-zh-tw="../../../zh-tw/app/home/index.html"', 'zh-tw/app/home/index.html'],
  ['en/app/home/index.html', 'data-url-ja="../../../app/home/index.html"', 'app/home/index.html'],
  ['zh-tw/app/home/index.html', 'data-url-en="../../../en/app/home/index.html"', 'en/app/home/index.html'],
  ['zh-tw/app/home/index.html', 'data-url-ja="../../../app/home/index.html"', 'app/home/index.html'],
  ['app/home/index.html', 'data-url-zh-tw="../../zh-tw/app/home/index.html"', 'zh-tw/app/home/index.html'],
];
for (const [page, attr, expected] of cases) {
  const html = fs.readFileSync(path.join(root, page), 'utf8');
  if (!html.includes('home-shell.css?v=20261008-hv02')) fail(page + ' css cache');
  if (!html.includes(attr)) fail(page + ' missing ' + attr);
  const href = attr.split('"')[1];
  const got = resolve(page, href);
  if (got !== expected) fail(page + ' resolves ' + got);
  else console.log('PASS', page, '->', got);
}

if (fails.length) {
  console.log('FAIL');
  fails.forEach((m) => console.log(' -', m));
  process.exit(1);
}
console.log('HOME-VISUAL-01 CHECK PASS');
