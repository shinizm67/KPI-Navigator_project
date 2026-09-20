/**
 * KPN Editable Grid Keyboard Keys
 * Keyboard navigation only — no save / OCC / lease / persistence / calc.
 *
 * Contract:
 * - Enter: commit current (blur/change via page) + move to next vertical editable
 * - Tab / Shift+Tab: leave to native order (do not reimplement)
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

  /**
   * @param {object} opts
   * @param {Element} opts.el
   * @param {function(Element): (Element|null|undefined)} opts.findNext
   * @param {function(Element)=} opts.commit
   * @param {function(Element, KeyboardEvent): boolean=} opts.shouldHandle
   * @param {function(Element)=} opts.afterFocus
   */
  function bindEnterVertical(opts) {
    var el = opts && opts.el;
    if (!el || el.getAttribute('data-kpi-grid-enter') === '1') return;
    if (typeof opts.findNext !== 'function') return;
    el.setAttribute('data-kpi-grid-enter', '1');
    el.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      if (e.isComposing) return;
      if (e.shiftKey || e.altKey || e.ctrlKey || e.metaKey) return;
      if (el.disabled) return;
      if (el.readOnly && !isCheckbox(el)) return;
      if (opts.shouldHandle && !opts.shouldHandle(el, e)) return;
      e.preventDefault();
      var commit = opts.commit || defaultCommit;
      commit(el);
      var next = opts.findNext(el);
      if (!next) return;
      global.setTimeout(function () {
        if (typeof opts.afterFocus === 'function') {
          opts.afterFocus(next);
          return;
        }
        if (isCheckbox(next)) {
          focusControl(next);
        } else {
          focusAndSelect(next);
        }
      }, 0);
    });
  }

  /**
   * Collect controls matching selector under root, in DOM order, editable only.
   * @param {ParentNode} root
   * @param {string} selector
   * @param {function(Element): boolean=} extraFilter
   */
  function listEditable(root, selector, extraFilter) {
    if (!root || !selector) return [];
    var nodes = root.querySelectorAll(selector);
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.disabled) continue;
      if (el.readOnly && !isCheckbox(el)) continue;
      if (extraFilter && !extraFilter(el)) continue;
      out.push(el);
    }
    return out;
  }

  function nextInList(list, current) {
    if (!list || !list.length || !current) return null;
    var idx = list.indexOf(current);
    if (idx < 0) return null;
    return list[idx + 1] || null;
  }

  global.KpiEditableGridKeys = {
    selectAll: selectAll,
    focusControl: focusControl,
    focusAndSelect: focusAndSelect,
    defaultCommit: defaultCommit,
    bindEnterVertical: bindEnterVertical,
    listEditable: listEditable,
    nextInList: nextInList,
    isCheckbox: isCheckbox,
  };
})(typeof window !== 'undefined' ? window : this);
