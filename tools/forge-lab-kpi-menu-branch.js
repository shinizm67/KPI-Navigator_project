/**
 * Forge Lab Global Menu — Key Performance Navigator リンク分岐（ローカル準備用）
 *
 * 使い方（本番アップロードは LP 動画完了後でOK）:
 * 1. このファイルを Forge Lab サイト側にコピーするか、同等の IIFE を共通 JS に貼る
 * 2. メニューの KPI リンクに class="nav--kpi" が付いていること（既存）
 * 3. メニュー表示ラベルは Forge Lab 本体 HTML で「Key Performance Navigator」（この JS は href のみ）
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
