/**
 * KPN Editable Grid Keyboard Keys
 * Keyboard navigation only — no save / OCC / lease / persistence / calc.
 *
 * Contract:
 * - Enter: commit + next vertical (wrap to next column top / first column top)
 * - Shift+Enter: commit + previous vertical (wrap)
 * - Tab: next horizontal (wrap to next row left / first row left)
 * - Shift+Tab: previous horizontal (wrap)
 * - Space on checkbox: native toggle (do not reimplement)
 */
(function (global) {
  'use strict';

  function selectAll(el) {
    if (!el) return;
    try {
      if (typeof el.select === 'function') {
        el.select();
        return;
      }
      if (el.isContentEditable) {
        var range = document.createRange();
        range.selectNodeContents(el);
        var sel = global.getSelection && global.getSelection();
        if (!sel) return;
        sel.removeAllRanges();
        sel.addRange(range);
      }
    } catch (_e) {}
  }

  function focusControl(el) {
    if (!el) return;
    try {
      el.focus({ preventScroll: false });
    } catch (_e) {
      try {
        el.focus();
      } catch (_e2) {}
    }
  }

  function focusAndSelect(el) {
    if (!el) return;
    focusControl(el);
    global.setTimeout(function () {
      selectAll(el);
    }, 0);
  }

  function defaultCommit(el) {
    if (!el) return;
    try {
      if (typeof el.blur === 'function') el.blur();
    } catch (_e) {}
  }

  function isCheckbox(el) {
    return !!(el && String(el.type || '').toLowerCase() === 'checkbox');
  }

  function colCount(matrix) {
    var max = 0;
    if (!matrix) return 0;
    for (var r = 0; r < matrix.length; r++) {
      var row = matrix[r];
      if (row && row.length > max) max = row.length;
    }
    return max;
  }

  function cellAt(matrix, r, c) {
    if (!matrix || r < 0 || c < 0) return null;
    var row = matrix[r];
    if (!row || c >= row.length) return null;
    return row[c] || null;
  }

  function findCoord(matrix, el) {
    if (!matrix || !el) return null;
    for (var r = 0; r < matrix.length; r++) {
      var row = matrix[r] || [];
      for (var c = 0; c < row.length; c++) {
        if (row[c] === el) return { r: r, c: c };
      }
    }
    return null;
  }

  /** Enter: same column down → next column top → wrap to first column top */
  function nextVerticalWrap(matrix, el) {
    var pos = findCoord(matrix, el);
    if (!pos) return null;
    var rows = matrix.length;
    var cols = colCount(matrix);
    if (!cols) return null;
    var r;
    var hit;
    for (r = pos.r + 1; r < rows; r++) {
      hit = cellAt(matrix, r, pos.c);
      if (hit) return hit;
    }
    var step;
    var c;
    var r2;
    for (step = 1; step <= cols; step++) {
      c = (pos.c + step) % cols;
      for (r2 = 0; r2 < rows; r2++) {
        hit = cellAt(matrix, r2, c);
        if (hit) return hit;
      }
    }
    return null;
  }

  /** Shift+Enter: same column up → previous column bottom → wrap */
  function prevVerticalWrap(matrix, el) {
    var pos = findCoord(matrix, el);
    if (!pos) return null;
    var rows = matrix.length;
    var cols = colCount(matrix);
    if (!cols) return null;
    var r;
    var hit;
    for (r = pos.r - 1; r >= 0; r--) {
      hit = cellAt(matrix, r, pos.c);
      if (hit) return hit;
    }
    var step;
    var c;
    var r2;
    for (step = 1; step <= cols; step++) {
      c = (pos.c - step + cols * 32) % cols;
      for (r2 = rows - 1; r2 >= 0; r2--) {
        hit = cellAt(matrix, r2, c);
        if (hit) return hit;
      }
    }
    return null;
  }

  /** Tab: same row right → next row left → wrap to first row left */
  function nextHorizontalWrap(matrix, el) {
    var pos = findCoord(matrix, el);
    if (!pos) return null;
    var rows = matrix.length;
    var cols = colCount(matrix);
    if (!cols) return null;
    var c;
    var hit;
    for (c = pos.c + 1; c < cols; c++) {
      hit = cellAt(matrix, pos.r, c);
      if (hit) return hit;
    }
    var step;
    var r;
    var c2;
    for (step = 1; step <= rows; step++) {
      r = (pos.r + step) % rows;
      for (c2 = 0; c2 < cols; c2++) {
        hit = cellAt(matrix, r, c2);
        if (hit) return hit;
      }
    }
    return null;
  }

  /** Shift+Tab: same row left → previous row right → wrap */
  function prevHorizontalWrap(matrix, el) {
    var pos = findCoord(matrix, el);
    if (!pos) return null;
    var rows = matrix.length;
    var cols = colCount(matrix);
    if (!cols) return null;
    var c;
    var hit;
    for (c = pos.c - 1; c >= 0; c--) {
      hit = cellAt(matrix, pos.r, c);
      if (hit) return hit;
    }
    var step;
    var r;
    var c2;
    for (step = 1; step <= rows; step++) {
      r = (pos.r - step + rows * 32) % rows;
      for (c2 = cols - 1; c2 >= 0; c2--) {
        hit = cellAt(matrix, r, c2);
        if (hit) return hit;
      }
    }
    return null;
  }

  function resolveMatrix(opts) {
    if (!opts) return null;
    if (typeof opts.getMatrix === 'function') {
      try {
        return opts.getMatrix() || null;
      } catch (_e) {
        return null;
      }
    }
    return opts.matrix || null;
  }

  function focusNavTarget(opts, next) {
    if (!next) return;
    if (typeof opts.afterFocus === 'function') {
      opts.afterFocus(next);
      return;
    }
    if (isCheckbox(next)) {
      focusControl(next);
    } else {
      focusAndSelect(next);
    }
  }

  /**
   * Full grid navigation: Enter / Shift+Enter / Tab / Shift+Tab with wraparound.
   * @param {object} opts
   * @param {Element} opts.el
   * @param {function(): Element[][]|null|undefined} [opts.getMatrix]
   * @param {Element[][]} [opts.matrix]
   * @param {function(Element)=} opts.commit  (Enter / Shift+Enter only)
   * @param {function(Element)=} opts.afterFocus
   */
  function bindGridKeys(opts) {
    var el = opts && opts.el;
    if (!el || el.getAttribute('data-kpi-grid-nav') === '1') return;
    el.setAttribute('data-kpi-grid-nav', '1');
    el.setAttribute('data-kpi-grid-enter', '1');
    el.addEventListener('keydown', function (e) {
      if (e.isComposing) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      var isEnter = e.key === 'Enter';
      var isTab = e.key === 'Tab';
      if (!isEnter && !isTab) return;
      if (el.disabled) return;
      if (el.readOnly && !isCheckbox(el)) return;
      var matrix = resolveMatrix(opts);
      if (!matrix || !matrix.length) return;
      if (!findCoord(matrix, el)) return;
      var next = null;
      if (isEnter && !e.shiftKey) next = nextVerticalWrap(matrix, el);
      else if (isEnter && e.shiftKey) next = prevVerticalWrap(matrix, el);
      else if (isTab && !e.shiftKey) next = nextHorizontalWrap(matrix, el);
      else if (isTab && e.shiftKey) next = prevHorizontalWrap(matrix, el);
      if (!next) return;
      e.preventDefault();
      if (isEnter) {
        var commit = opts.commit || defaultCommit;
        commit(el);
      }
      global.setTimeout(function () {
        focusNavTarget(opts, next);
      }, 0);
    });
  }

  /**
   * Legacy Enter-only binder (no wrap unless findNext wraps). Prefer bindGridKeys.
   */
  function bindEnterVertical(opts) {
    var el = opts && opts.el;
    if (!el || el.getAttribute('data-kpi-grid-enter') === '1') return;
    if (typeof opts.findNext !== 'function') return;
    el.setAttribute('data-kpi-grid-enter', '1');
    el.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      if (e.isComposing) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      if (el.disabled) return;
      if (el.readOnly && !isCheckbox(el)) return;
      if (opts.shouldHandle && !opts.shouldHandle(el, e)) return;
      var reverse = !!e.shiftKey;
      e.preventDefault();
      var commit = opts.commit || defaultCommit;
      commit(el);
      var next = null;
      if (reverse && typeof opts.findPrev === 'function') next = opts.findPrev(el);
      else if (!reverse) next = opts.findNext(el);
      if (!next) return;
      global.setTimeout(function () {
        focusNavTarget(opts, next);
      }, 0);
    });
  }

  function listEditable(root, selector, extraFilter) {
    if (!root || !selector) return [];
    var nodes = root.querySelectorAll(selector);
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (node.disabled) continue;
      if (node.readOnly && !isCheckbox(node)) continue;
      if (extraFilter && !extraFilter(node)) continue;
      out.push(node);
    }
    return out;
  }

  function nextInList(list, current) {
    if (!list || !list.length || !current) return null;
    var idx = list.indexOf(current);
    if (idx < 0) return null;
    return list[idx + 1] || null;
  }

  function prevInList(list, current) {
    if (!list || !list.length || !current) return null;
    var idx = list.indexOf(current);
    if (idx < 0) return null;
    return idx > 0 ? list[idx - 1] : null;
  }

  /** Wrap within a flat list (single-column / single-row helpers). */
  function nextInListWrap(list, current) {
    if (!list || !list.length || !current) return null;
    var idx = list.indexOf(current);
    if (idx < 0) return null;
    return list[(idx + 1) % list.length];
  }

  function prevInListWrap(list, current) {
    if (!list || !list.length || !current) return null;
    var idx = list.indexOf(current);
    if (idx < 0) return null;
    return list[(idx - 1 + list.length) % list.length];
  }

  global.KpiEditableGridKeys = {
    selectAll: selectAll,
    focusControl: focusControl,
    focusAndSelect: focusAndSelect,
    defaultCommit: defaultCommit,
    bindGridKeys: bindGridKeys,
    bindEnterVertical: bindEnterVertical,
    listEditable: listEditable,
    nextInList: nextInList,
    prevInList: prevInList,
    nextInListWrap: nextInListWrap,
    prevInListWrap: prevInListWrap,
    nextVerticalWrap: nextVerticalWrap,
    prevVerticalWrap: prevVerticalWrap,
    nextHorizontalWrap: nextHorizontalWrap,
    prevHorizontalWrap: prevHorizontalWrap,
    findCoord: findCoord,
    isCheckbox: isCheckbox,
  };
})(typeof window !== 'undefined' ? window : this);
