/**
 * Phase 0 busy overlay — CSV import / bulk save.
 * Schema unchanged. Docs: docs/snapshot-store-phased-plan.md
 */
(function (global) {
  'use strict';

  if (global.__KPI_BUSY && global.__KPI_BUSY.__ready) return;

  var ROOT_ID = 'kpi-busy-overlay';
  var busy = false;
  var inRun = false;

  function lang() {
    var raw = String((document.documentElement && document.documentElement.getAttribute('lang')) || '');
    var l = raw.toLowerCase();
    if (l.indexOf('zh') === 0) return 'zh';
    if (l.indexOf('ja') === 0) return 'ja';
    return 'en';
  }

  function copy(kind, extra) {
    var L = lang();
    extra = extra || {};
    if (kind === 'parse') {
      if (L === 'ja') return 'ファイルを読み込んでいます…';
      if (L === 'zh') return '正在讀取檔案…';
      return 'Reading file…';
    }
    if (kind === 'import') {
      var n = extra.count;
      if (L === 'ja') {
        return Number.isFinite(n)
          ? '取り込み中です（' + n + '件）。画面が止まるように見えても処理中です。'
          : '取り込み中です。画面が止まるように見えても処理中です。';
      }
      if (L === 'zh') {
        return Number.isFinite(n)
          ? '匯入中（' + n + ' 筆）。畫面可能暫時無回應，請稍候。'
          : '匯入中。畫面可能暫時無回應，請稍候。';
      }
      return Number.isFinite(n)
        ? 'Importing ' + n + ' rows. The page may look frozen — please wait.'
        : 'Importing. The page may look frozen — please wait.';
    }
    if (L === 'ja') return '保存しています。画面が止まるように見えても処理中です。';
    if (L === 'zh') return '正在儲存。畫面可能暫時無回應，請稍候。';
    return 'Saving. The page may look frozen — please wait.';
  }

  function titleFor(kind) {
    var L = lang();
    if (kind === 'parse') {
      if (L === 'ja') return '読み込み中';
      if (L === 'zh') return '讀取中';
      return 'Reading';
    }
    if (kind === 'import') {
      if (L === 'ja') return '取り込み中';
      if (L === 'zh') return '匯入中';
      return 'Importing';
    }
    if (L === 'ja') return '保存中';
    if (L === 'zh') return '儲存中';
    return 'Saving';
  }

  function ensureDom() {
    var el = document.getElementById(ROOT_ID);
    if (el) return el;
    el = document.createElement('div');
    el.id = ROOT_ID;
    el.className = 'kpi-busy-overlay';
    el.setAttribute('hidden', '');
    el.setAttribute('role', 'alertdialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-live', 'assertive');
    el.innerHTML =
      '<div class="kpi-busy-overlay__panel">' +
      '<p class="kpi-busy-overlay__title" id="kpi-busy-overlay-title"></p>' +
      '<p class="kpi-busy-overlay__msg" id="kpi-busy-overlay-msg"></p>' +
      '</div>';
    (document.body || document.documentElement).appendChild(el);
    return el;
  }

  function show(kind, extra) {
    var el = ensureDom();
    var title = document.getElementById('kpi-busy-overlay-title');
    var msg = document.getElementById('kpi-busy-overlay-msg');
    if (title) title.textContent = titleFor(kind);
    if (msg) msg.textContent = copy(kind, extra);
    el.removeAttribute('hidden');
    el.classList.add('is-on');
    document.body.classList.add('kpi-busy-lock');
    busy = true;
  }

  function hide() {
    var el = document.getElementById(ROOT_ID);
    if (el) {
      el.setAttribute('hidden', '');
      el.classList.remove('is-on');
    }
    document.body.classList.remove('kpi-busy-lock');
    busy = false;
  }

  function yieldPaint() {
    return new Promise(function (resolve) {
      if (typeof requestAnimationFrame !== 'function') {
        setTimeout(resolve, 32);
        return;
      }
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          resolve();
        });
      });
    });
  }

  function run(kind, fn, extra) {
    if (inRun) {
      return Promise.resolve(fn());
    }
    if (busy) return Promise.resolve();
    inRun = true;
    show(kind, extra);
    return yieldPaint()
      .then(function () {
        return fn();
      })
      .then(
        function (v) {
          inRun = false;
          hide();
          return v;
        },
        function (err) {
          inRun = false;
          hide();
          throw err;
        }
      );
  }

  global.__KPI_BUSY = {
    __ready: true,
    show: show,
    hide: hide,
    run: run,
    yieldPaint: yieldPaint,
    isBusy: function () {
      return busy;
    },
    get _inRun() {
      return inRun;
    },
  };
})(typeof window !== 'undefined' ? window : this);
