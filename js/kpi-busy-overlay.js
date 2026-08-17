/**
 * Phase 0 / Stage 5 busy overlay — CSV import / bulk save / year-chunk rebuild.
 * Schema unchanged. Docs: docs/snapshot-store-phased-plan.md
 * Marker: KPI-BUSY-YEAR-CHUNK-AK
 */
(function (global) {
  'use strict';

  if (global.__KPI_BUSY && global.__KPI_BUSY.__ready) return;

  var ROOT_ID = 'kpi-busy-overlay';
  var busy = false;
  var inRun = false;
  var lastKind = 'save';
  var lastExtra = {};

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
    if (kind === 'rebuild') {
      var y = Number(extra.year);
      var i = Number(extra.index);
      var t = Number(extra.total);
      if (Number.isFinite(y) && Number.isFinite(i) && Number.isFinite(t) && t > 0) {
        if (L === 'ja') {
          return 'サーバで年次の解を計算中（' + y + '年・' + i + '/' + t + '）。画面が止まるように見えても処理中です。';
        }
        if (L === 'zh') {
          return '伺服器正在計算年度解（' + y + '・' + i + '/' + t + '）。畫面可能暫時無回應，請稍候。';
        }
        return 'Rebuilding year facts on the server (' + y + ', ' + i + '/' + t + '). The page may look frozen — please wait.';
      }
      if (L === 'ja') return 'サーバで年次の解を計算中です。画面が止まるように見えても処理中です。';
      if (L === 'zh') return '伺服器正在計算年度解。畫面可能暫時無回應，請稍候。';
      return 'Rebuilding year facts on the server. The page may look frozen — please wait.';
    }
    if (kind === 'import') {
      var years = Number(extra.yearCount);
      if (Number.isFinite(years) && years > 0) {
        if (L === 'ja') {
          return '取り込み後、サーバで年次計算します（' + years + '年分）。画面が止まるように見えても処理中です。';
        }
        if (L === 'zh') {
          return '匯入後由伺服器計算年度解（共 ' + years + ' 年）。畫面可能暫時無回應，請稍候。';
        }
        return 'Importing, then rebuilding ' + years + ' year(s) on the server. The page may look frozen — please wait.';
      }
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
    if (kind === 'rebuild') {
      if (L === 'ja') return '年次計算中';
      if (L === 'zh') return '年度計算中';
      return 'Rebuilding';
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
    lastKind = kind || 'save';
    lastExtra = extra || {};
    var el = ensureDom();
    var title = document.getElementById('kpi-busy-overlay-title');
    var msg = document.getElementById('kpi-busy-overlay-msg');
    if (title) title.textContent = titleFor(lastKind);
    if (msg) msg.textContent = copy(lastKind, lastExtra);
    el.removeAttribute('hidden');
    el.classList.add('is-on');
    document.body.classList.add('kpi-busy-lock');
    busy = true;
  }

  function update(kind, extra) {
    if (!busy) {
      show(kind, extra);
      return;
    }
    if (kind) lastKind = kind;
    if (extra && typeof extra === 'object') {
      lastExtra = Object.assign({}, lastExtra, extra);
    }
    var title = document.getElementById('kpi-busy-overlay-title');
    var msg = document.getElementById('kpi-busy-overlay-msg');
    if (title) title.textContent = titleFor(lastKind);
    if (msg) msg.textContent = copy(lastKind, lastExtra);
  }

  function hide() {
    var el = document.getElementById(ROOT_ID);
    if (el) {
      el.setAttribute('hidden', '');
      el.classList.remove('is-on');
    }
    document.body.classList.remove('kpi-busy-lock');
    busy = false;
    lastExtra = {};
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
    if (typeof kind === 'function') {
      extra = fn;
      fn = kind;
      kind = (extra && extra.kind) || 'save';
    }
    if (typeof fn !== 'function') {
      return Promise.resolve();
    }
    if (inRun) {
      return Promise.resolve(fn());
    }
    if (busy) {
      return Promise.resolve(fn());
    }
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
    update: update,
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
