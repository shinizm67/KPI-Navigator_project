/**
 * Forge Lab Global Menu — Key Performance Navigator リンク分岐
 *
 * 本番反映: Forge Lab 本体の `script.js` / `en/script.js` 末尾に同等 IIFE を同梱済み（2026-08-11）。
 * このファイルは kpi-navigator リポ内の正本コピー（貼り付け・差分確認用）。
 *
 * 分岐:
 * - localStorage.kpiNavigator.registrationComplete === '1'
 *     → /kpi-navigator/login/ （EN ページなら /kpi-navigator/en/login/）
 * - それ以外 → 既存 href（LP: /kpi-navigator/ または /kpi-navigator/en/）を維持
 *
 * 注意: 本格セッション認証は Phase B。これは UX 用の仮フラグのみ。
 * ブランド表示名は Key Performance Navigator（docs/brand-key-performance-navigator.md）。
 * URL パスは当面 kpi-navigator。
 */
(function () {
  'use strict';

  var FLAG_KEY = 'kpiNavigator.registrationComplete';
  var registered = false;
  try {
    registered = localStorage.getItem(FLAG_KEY) === '1';
  } catch (e) {
    registered = false;
  }
  if (!registered) return;

  var path = (window.location.pathname || '').toLowerCase();
  var isEn = path.indexOf('/en/') !== -1 || path.indexOf('/en') === path.length - 3;
  var loginHref = isEn ? '/kpi-navigator/en/login/' : '/kpi-navigator/login/';

  var links = document.querySelectorAll('a.nav--kpi');
  for (var i = 0; i < links.length; i++) {
    links[i].setAttribute('href', loginHref);
  }
})();
