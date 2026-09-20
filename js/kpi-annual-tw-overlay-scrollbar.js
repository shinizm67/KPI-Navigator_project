/**
 * KPN Annual TW Overlay Scrollbar — in-place thumbs (no host wrap).
 *
 * Why separate from js/kpi-overlay-scrollbar.js SELECTORS:
 * wrapping .annual-daily-focus-scroll inside absolute .annual-daily-focus-scroll-clip
 * breaks height:100% → content-sized pin → canY false / clipped content.
 *
 * This module:
 * - never wraps / never mutates height|max-height|min-height|flex|overflow
 * - appends thumbs as siblings inside the clip
 * - hides native rails only when nativeScrollbarWidth > 0 (or force flag)
 * - leaves Mac native overlay alone
 */
(function (global) {
  'use strict';

  if (global.KpiAnnualTwOverlayScrollbar && global.KpiAnnualTwOverlayScrollbar.__ready) {
    return;
  }

  var HIDE_MS = 700;
  var THUMB_MIN = 28;
  var STYLE_ID = 'kpn-annual-tw-overlay-style';
  var ENABLED_HTML = 'kpn-annual-tw-overlay';
  var TARGET_CLASS = 'kpn-atw-osb-target';
  var THUMB_CLASS = 'kpn-atw-osb-thumb';
  var PRIMARY_SEL = '.annual-daily-focus-scroll';
  var CLIP_SEL = '.annual-daily-focus-scroll-clip';

  var instances = [];
  var reducedMotion = false;
  var moRefreshQueued = false;

  function sharedApi() {
    return global.KpiOverlayScrollbar || null;
  }

  function needsOverlay() {
    if (global.__KPN_FORCE_OVERLAY_SCROLL === true) return true;
    if (global.__KPN_FORCE_OVERLAY_SCROLL === false) return false;
    var api = sharedApi();
    if (api && typeof api.needsOverlay === 'function') return api.needsOverlay();
    if (api && typeof api.getNativeScrollbarWidth === 'function') {
      return api.getNativeScrollbarWidth() > 0;
    }
    /* Fallback measure if shared module absent */
    var outer = document.createElement('div');
    outer.style.cssText =
      'position:absolute;top:-9999px;left:-9999px;width:120px;height:120px;overflow:scroll;visibility:hidden;';
    var inner = document.createElement('div');
    inner.style.cssText = 'width:100%;height:200px;';
    outer.appendChild(inner);
    document.documentElement.appendChild(outer);
    var w = outer.offsetWidth - outer.clientWidth;
    if (!w) w = outer.offsetHeight - outer.clientHeight;
    outer.parentNode.removeChild(outer);
    return w > 0;
  }

  function injectCss() {
    if (document.getElementById(STYLE_ID)) return;
    var css =
      'html.' +
      ENABLED_HTML +
      ' .' +
      TARGET_CLASS +
      '{' +
      'scrollbar-width:none!important;' +
      '-ms-overflow-style:none!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .' +
      TARGET_CLASS +
      '::-webkit-scrollbar{' +
      'width:0!important;height:0!important;display:none!important;background:transparent!important;' +
      '}' +
      '.' +
      THUMB_CLASS +
      '{' +
      'position:absolute;z-index:40;opacity:0;pointer-events:none;' +
      'border-radius:999px;' +
      'background:var(--kpn-scroll-thumb,rgba(88,225,243,.75));' +
      'box-shadow:0 0 6px rgba(88,225,243,.25);' +
      'transition:opacity .18s ease;' +
      'touch-action:none;' +
      '}' +
      '.' +
      THUMB_CLASS +
      '.is-visible{opacity:1;pointer-events:auto;}' +
      '.' +
      THUMB_CLASS +
      '.is-dragging{' +
      'opacity:1;pointer-events:auto;' +
      'background:var(--kpn-scroll-thumb-hover,rgba(110,235,250,.95));' +
      '}' +
      '.' +
      THUMB_CLASS +
      ':hover{' +
      'background:var(--kpn-scroll-thumb-hover,rgba(110,235,250,.95));' +
      '}' +
      '.' +
      THUMB_CLASS +
      '--y{top:0;right:2px;width:6px;min-height:' +
      THUMB_MIN +
      'px;}' +
      '.' +
      THUMB_CLASS +
      '--x{left:0;bottom:2px;height:6px;min-width:' +
      THUMB_MIN +
      'px;}' +
      'body.office-mode{' +
      '--kpn-scroll-thumb:rgba(80,80,80,.55);' +
      '--kpn-scroll-thumb-hover:rgba(60,60,60,.8);' +
      '}' +
      '@media (prefers-reduced-motion:reduce){.' +
      THUMB_CLASS +
      '{transition:none;}}';
    var style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }

  function isUnmeasurable(el) {
    if (!el || !el.isConnected) return true;
    if (el.closest('[hidden]')) return true;
    var node = el;
    while (node && node.nodeType === 1) {
      if (getComputedStyle(node).display === 'none') return true;
      node = node.parentElement;
    }
    return el.clientWidth < 2 || el.clientHeight < 2;
  }

  function findClip(el) {
    return el.closest(CLIP_SEL) || el.parentElement;
  }

  function enhance(el) {
    if (!el || el.nodeType !== 1) return null;
    if (el.dataset.kpnAtwOsb === '1') return el._kpnAtwOsb || null;
    if (!needsOverlay()) return null;
    if (isUnmeasurable(el)) {
      el.dataset.kpnAtwOsbPending = '1';
      watchPending(el);
      return null;
    }

    var clip = findClip(el);
    if (!clip) return null;

    injectCss();
    document.documentElement.classList.add(ENABLED_HTML);
    delete el.dataset.kpnAtwOsbPending;

    /* Never wrap. Never rewrite layout props on el. */
    el.classList.add(TARGET_CLASS);
    el.dataset.kpnAtwOsb = '1';

    var thumbY = document.createElement('div');
    thumbY.className = THUMB_CLASS + ' ' + THUMB_CLASS + '--y';
    thumbY.setAttribute('aria-hidden', 'true');
    var thumbX = document.createElement('div');
    thumbX.className = THUMB_CLASS + ' ' + THUMB_CLASS + '--x';
    thumbX.setAttribute('aria-hidden', 'true');
    clip.appendChild(thumbY);
    clip.appendChild(thumbX);

    var hideTimer = null;
    var dragging = null;

    function canY() {
      return el.scrollHeight > el.clientHeight + 1;
    }
    function canX() {
      return el.scrollWidth > el.clientWidth + 1;
    }

    function show() {
      if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
      }
      if (canY()) thumbY.classList.add('is-visible');
      else thumbY.classList.remove('is-visible');
      if (canX()) thumbX.classList.add('is-visible');
      else thumbX.classList.remove('is-visible');
    }

    function scheduleHide() {
      if (dragging) return;
      if (hideTimer) clearTimeout(hideTimer);
      var ms = reducedMotion ? 120 : HIDE_MS;
      hideTimer = setTimeout(function () {
        if (dragging) return;
        thumbY.classList.remove('is-visible');
        thumbX.classList.remove('is-visible');
      }, ms);
    }

    function sync() {
      var ch = el.clientHeight;
      var cw = el.clientWidth;
      var sh = el.scrollHeight;
      var sw = el.scrollWidth;

      if (canY()) {
        var trackH = Math.max(ch - 4, THUMB_MIN);
        var th = Math.max(THUMB_MIN, Math.round(trackH * (ch / sh)));
        var maxTop = Math.max(trackH - th, 0);
        var top = sh <= ch ? 0 : Math.round((el.scrollTop / (sh - ch)) * maxTop);
        thumbY.style.height = th + 'px';
        thumbY.style.transform = 'translateY(' + top + 'px)';
        thumbY.style.display = '';
      } else {
        thumbY.style.display = 'none';
        thumbY.classList.remove('is-visible');
      }

      if (canX()) {
        var trackW = Math.max(cw - 4, THUMB_MIN);
        var tw = Math.max(THUMB_MIN, Math.round(trackW * (cw / sw)));
        var maxLeft = Math.max(trackW - tw, 0);
        var left = sw <= cw ? 0 : Math.round((el.scrollLeft / (sw - cw)) * maxLeft);
        thumbX.style.width = tw + 'px';
        thumbX.style.transform = 'translateX(' + left + 'px)';
        thumbX.style.display = '';
      } else {
        thumbX.style.display = 'none';
        thumbX.classList.remove('is-visible');
      }
    }

    function onScroll() {
      sync();
      show();
      scheduleHide();
    }

    el.addEventListener('scroll', onScroll, { passive: true });
    clip.addEventListener('pointerenter', function () {
      sync();
      show();
    });
    clip.addEventListener('pointerleave', function () {
      if (!dragging) scheduleHide();
    });
    el.addEventListener(
      'wheel',
      function () {
        sync();
        show();
        scheduleHide();
      },
      { passive: true }
    );

    function bindDrag(thumb, axis) {
      thumb.addEventListener('pointerdown', function (ev) {
        if (ev.button != null && ev.button !== 0) return;
        ev.preventDefault();
        ev.stopPropagation();
        thumb.setPointerCapture(ev.pointerId);
        dragging = axis;
        thumb.classList.add('is-dragging');
        show();
        var startClient = axis === 'y' ? ev.clientY : ev.clientX;
        var startScroll = axis === 'y' ? el.scrollTop : el.scrollLeft;
        var scrollRange =
          axis === 'y'
            ? el.scrollHeight - el.clientHeight
            : el.scrollWidth - el.clientWidth;
        var track =
          axis === 'y'
            ? Math.max(el.clientHeight - 4 - thumb.offsetHeight, 1)
            : Math.max(el.clientWidth - 4 - thumb.offsetWidth, 1);

        function onMove(e) {
          var delta = (axis === 'y' ? e.clientY : e.clientX) - startClient;
          var next = startScroll + (delta / track) * scrollRange;
          if (axis === 'y') el.scrollTop = next;
          else el.scrollLeft = next;
          sync();
        }
        function onUp(e) {
          dragging = null;
          thumb.classList.remove('is-dragging');
          try {
            thumb.releasePointerCapture(e.pointerId);
          } catch (err) {}
          thumb.removeEventListener('pointermove', onMove);
          thumb.removeEventListener('pointerup', onUp);
          thumb.removeEventListener('pointercancel', onUp);
          scheduleHide();
        }
        thumb.addEventListener('pointermove', onMove);
        thumb.addEventListener('pointerup', onUp);
        thumb.addEventListener('pointercancel', onUp);
      });
    }
    bindDrag(thumbY, 'y');
    bindDrag(thumbX, 'x');

    var ro =
      typeof ResizeObserver !== 'undefined'
        ? new ResizeObserver(function () {
            sync();
          })
        : null;
    if (ro) {
      ro.observe(el);
      ro.observe(clip);
    }

    var api = {
      el: el,
      clip: clip,
      sync: sync,
      show: show,
      scheduleHide: scheduleHide,
      remeasure: function () {
        if (isUnmeasurable(el)) return;
        sync();
      },
      destroy: function () {
        if (ro) ro.disconnect();
        el.removeEventListener('scroll', onScroll);
        if (hideTimer) clearTimeout(hideTimer);
        if (thumbY.parentNode) thumbY.parentNode.removeChild(thumbY);
        if (thumbX.parentNode) thumbX.parentNode.removeChild(thumbX);
        el.classList.remove(TARGET_CLASS);
        delete el.dataset.kpnAtwOsb;
        delete el.dataset.kpnAtwOsbPending;
        delete el._kpnAtwOsb;
        instances = instances.filter(function (x) {
          return x !== api;
        });
        if (!instances.length) {
          document.documentElement.classList.remove(ENABLED_HTML);
        }
      }
    };
    el._kpnAtwOsb = api;
    instances.push(api);
    sync();
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          if (api && typeof api.remeasure === 'function') api.remeasure();
        });
      });
    }
    return api;
  }

  function watchPending(el) {
    if (!el || el._kpnAtwOsbWatch) return;
    el._kpnAtwOsbWatch = true;
    var finished = false;
    var ro = null;
    function cleanup() {
      if (finished) return;
      finished = true;
      try {
        if (ro) ro.disconnect();
      } catch (e) {}
      delete el._kpnAtwOsbWatch;
    }
    function tryFlush() {
      if (finished) return;
      if (el.dataset.kpnAtwOsb === '1') {
        cleanup();
        return;
      }
      if (isUnmeasurable(el)) return;
      cleanup();
      delete el.dataset.kpnAtwOsbPending;
      enhance(el);
    }
    ro =
      typeof ResizeObserver !== 'undefined'
        ? new ResizeObserver(function () {
            tryFlush();
          })
        : null;
    if (ro) ro.observe(el);
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(function () {
        requestAnimationFrame(tryFlush);
      });
    } else {
      tryFlush();
    }
  }

  function enhanceAll(root) {
    if (!needsOverlay()) {
      document.documentElement.classList.remove(ENABLED_HTML);
      return [];
    }
    root = root || document;
    var out = [];
    var nodes = root.querySelectorAll ? root.querySelectorAll(PRIMARY_SEL) : [];
    for (var i = 0; i < nodes.length; i++) {
      var api = enhance(nodes[i]);
      if (api) out.push(api);
    }
    flushPending(root);
    return out;
  }

  function flushPending(root) {
    root = root || document;
    var pending = root.querySelectorAll
      ? root.querySelectorAll('[data-kpn-atw-osb-pending="1"]')
      : [];
    var out = [];
    for (var i = 0; i < pending.length; i++) {
      var el = pending[i];
      if (isUnmeasurable(el)) continue;
      delete el.dataset.kpnAtwOsbPending;
      var api = enhance(el);
      if (api) out.push(api);
    }
    return out;
  }

  function refreshAll(root) {
    if (!needsOverlay()) return [];
    enhanceAll(root || document);
    for (var i = 0; i < instances.length; i++) {
      if (instances[i] && typeof instances[i].remeasure === 'function') {
        instances[i].remeasure();
      }
    }
    return instances.slice();
  }

  function queueRefreshAll() {
    if (moRefreshQueued) return;
    moRefreshQueued = true;
    function run() {
      moRefreshQueued = false;
      refreshAll(document);
    }
    if (typeof requestAnimationFrame === 'function') {
      requestAnimationFrame(function () {
        requestAnimationFrame(run);
      });
    } else {
      run();
    }
  }

  function boot() {
    try {
      reducedMotion = !!(
        global.matchMedia &&
        global.matchMedia('(prefers-reduced-motion: reduce)').matches
      );
    } catch (e) {
      reducedMotion = false;
    }
    /* Drop any legacy wraps from the shared module if still present. */
    var shared = sharedApi();
    if (shared && typeof shared.destroyAnnualTwWrappers === 'function') {
      shared.destroyAnnualTwWrappers();
    }
    if (!needsOverlay()) return;
    enhanceAll(document);
    if (typeof MutationObserver !== 'undefined') {
      var mo = new MutationObserver(function (muts) {
        var needRefresh = false;
        for (var i = 0; i < muts.length; i++) {
          var m = muts[i];
          if (m.type === 'attributes') {
            needRefresh = true;
            continue;
          }
          for (var j = 0; j < m.addedNodes.length; j++) {
            var n = m.addedNodes[j];
            if (n.nodeType !== 1) continue;
            enhanceAll(n);
          }
        }
        if (needRefresh) queueRefreshAll();
      });
      mo.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['hidden', 'class', 'aria-hidden']
      });
    }
  }

  var api = {
    __ready: true,
    PRIMARY_SEL: PRIMARY_SEL,
    needsOverlay: needsOverlay,
    enhance: enhance,
    enhanceAll: enhanceAll,
    refresh: refreshAll,
    refreshAll: refreshAll,
    remeasure: refreshAll,
    getInstances: function () {
      return instances.slice();
    },
    boot: boot
  };
  global.KpiAnnualTwOverlayScrollbar = api;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})(typeof window !== 'undefined' ? window : this);
