/**
 * KPN Overlay Scrollbar — Windows Mac-like overlay thumbs.
 * Contract: docs/kpn-scrollbar-ux-contract.md
 *
 * Runtime detects native scrollbar layout width (not UA).
 * nativeWidth === 0 → preserve native overlay (Mac Chrome).
 * nativeWidth > 0  → hide native rails, show auto-hiding overlay thumbs.
 */
(function (global) {
  'use strict';

  if (global.KpiOverlayScrollbar && global.KpiOverlayScrollbar.__ready) return;

  var HIDE_MS = 700;
  var THUMB_MIN = 28;
  var STYLE_ID = 'kpn-overlay-scrollbar-style';
  var HOST_CLASS = 'kpn-osb-host';
  var TARGET_CLASS = 'kpn-osb-target';
  var ENABLED_HTML = 'kpn-overlay-scroll';

  /** Known KPN scroll containers (Phase 1–3).
   *  Annual Timeline Window (.annual-daily-focus-*) intentionally excluded:
   *  wrapping breaks height:100% inside absolute clip → host pins to content
   *  height, canY becomes false, content appears clipped with no vertical scroll.
   */
  var SELECTORS = [
    /* Daily FW */
    '.daily-overlay__scroll',
    '.annual-edit-modal__scroll',
    /* Insight */
    '.insight-overlay__scroll',
    '.insight-analyze-weekly__table-scroll',
    /* Past Sales / Sales Data */
    '.past-sales-modal__scroll',
    '.past-sales-modal__analyze-scroll',
    '.sales-data-modal__scroll',
    '.sales-data-modal__analyze-scroll',
    /* Monthly TW data band */
    '.monthly-scroll-data',
    /* MEP — primary grid scroller only.
       labels / date-rail are slave ports (wheel routed here); rails hidden via CSS. */
    '.monthly-edit-float__scroll',
    '.memo-float-modal__body-scroll',
    '.memo-float-modal__date-scroll',
    /* PL table */
    '.pl-table-scroll-y',
    '.pl-data-pane',
    /* PL Insight (= pl-graph-overlay scrollport) */
    '.pl-graph-overlay__scroll',
    /* Generic opt-in */
    '[data-kpn-overlay-scroll]'
  ];

  /** Legacy Annual TW selectors — destroy if previously wrapped (hotfixed out). */
  var ANNUAL_TW_SELECTORS = [
    '.annual-daily-focus-scroll',
    '.annual-daily-focus-global-scroll',
    '.annual-daily-focus-bar-upper-scroll',
    '.annual-daily-focus-bar-lower-scroll'
  ];

  var nativeWidthCache = null;
  var instances = [];
  var reducedMotion = false;

  function measureNativeScrollbarWidth() {
    if (nativeWidthCache !== null) return nativeWidthCache;
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
    nativeWidthCache = w > 0 ? w : 0;
    return nativeWidthCache;
  }

  function needsOverlay() {
    if (global.__KPN_FORCE_OVERLAY_SCROLL === true) return true;
    if (global.__KPN_FORCE_OVERLAY_SCROLL === false) return false;
    return measureNativeScrollbarWidth() > 0;
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
      HOST_CLASS +
      '{' +
      'position:relative;' +
      'min-width:0;min-height:0;' +
      '}' +
      '.' +
      HOST_CLASS +
      ' > .' +
      TARGET_CLASS +
      '{' +
      'width:100%;' +
      'height:100%;' +
      'box-sizing:border-box;' +
      '}' +
      '.kpn-osb-thumb{' +
      'position:absolute;z-index:40;opacity:0;pointer-events:none;' +
      'border-radius:999px;' +
      'background:var(--kpn-scroll-thumb,rgba(88,225,243,.75));' +
      'box-shadow:0 0 6px rgba(88,225,243,.25);' +
      'transition:opacity .18s ease;' +
      'touch-action:none;' +
      '}' +
      '.kpn-osb-thumb.is-visible{' +
      'opacity:1;pointer-events:auto;' +
      '}' +
      '.kpn-osb-thumb.is-dragging{' +
      'opacity:1;pointer-events:auto;' +
      'background:var(--kpn-scroll-thumb-hover,rgba(110,235,250,.95));' +
      '}' +
      '.kpn-osb-thumb:hover{' +
      'background:var(--kpn-scroll-thumb-hover,rgba(110,235,250,.95));' +
      '}' +
      '.kpn-osb-thumb-y{top:0;right:2px;width:6px;min-height:' +
      THUMB_MIN +
      'px;}' +
      '.kpn-osb-thumb-x{left:0;bottom:2px;height:6px;min-width:' +
      THUMB_MIN +
      'px;}' +
      'body.office-mode{' +
      '--kpn-scroll-thumb:rgba(80,80,80,.55);' +
      '--kpn-scroll-thumb-hover:rgba(60,60,60,.8);' +
      '}' +
      'html.' +
      ENABLED_HTML +
      '{' +
      '--monthly-hscroll-scrollbar-gutter:0px;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-window{' +
      '--pl-scrollbar-w:0!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-scroll-y{' +
      'scrollbar-gutter:auto!important;' +
      'overflow-y:auto!important;' +
      'scrollbar-width:none!important;' +
      'scrollbar-color:transparent transparent!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-frozen{' +
      'padding-right:0!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .pl-data-pane{' +
      'scrollbar-width:none!important;' +
      'scrollbar-color:transparent transparent!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .pl-data-pane::-webkit-scrollbar,' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-scroll-y::-webkit-scrollbar,' +
      'html.' +
      ENABLED_HTML +
      ' .pl-data-pane::-webkit-scrollbar-track,' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-scroll-y::-webkit-scrollbar-track,' +
      'html.' +
      ENABLED_HTML +
      ' .pl-data-pane::-webkit-scrollbar-thumb,' +
      'html.' +
      ENABLED_HTML +
      ' .pl-table-scroll-y::-webkit-scrollbar-thumb{' +
      'width:0!important;height:0!important;display:none!important;' +
      'background:transparent!important;border:0!important;' +
      '}' +
      /* MEP slave ports: keep overflow for sync, hide duplicated native rails */
      'html.' +
      ENABLED_HTML +
      ' .monthly-edit-float__labels,' +
      'html.' +
      ENABLED_HTML +
      ' .monthly-edit-float__date-rail-scroll{' +
      'scrollbar-width:none!important;' +
      '-ms-overflow-style:none!important;' +
      'scrollbar-color:transparent transparent!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .monthly-edit-float__labels::-webkit-scrollbar,' +
      'html.' +
      ENABLED_HTML +
      ' .monthly-edit-float__date-rail-scroll::-webkit-scrollbar{' +
      'width:0!important;height:0!important;display:none!important;' +
      'background:transparent!important;' +
      '}' +
      'html.' +
      ENABLED_HTML +
      ' .monthly-scroll-data{' +
      'scrollbar-color:transparent transparent!important;' +
      '}' +
      '@media (prefers-reduced-motion:reduce){' +
      '.kpn-osb-thumb{transition:none;}' +
      '}';
    var style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }

  function isFlexScrollChild(el, cs) {
    if (!cs) cs = getComputedStyle(el);
    if (cs.flexGrow && cs.flexGrow !== '0') return true;
    return (
      el.classList.contains('pl-data-pane') ||
      el.classList.contains('pl-table-scroll-y') ||
      el.classList.contains('monthly-edit-float__scroll') ||
      el.classList.contains('pl-graph-overlay__scroll') ||
      el.classList.contains('daily-overlay__scroll') ||
      el.classList.contains('insight-overlay__scroll') ||
      el.classList.contains('annual-edit-modal__scroll') ||
      el.classList.contains('past-sales-modal__scroll') ||
      el.classList.contains('sales-data-modal__scroll') ||
      el.classList.contains('past-sales-modal__analyze-scroll') ||
      el.classList.contains('sales-data-modal__analyze-scroll') ||
      el.classList.contains('memo-float-modal__body-scroll')
    );
  }

  function applyFlexFillHost(el, host, cs) {
    /* Host becomes the flex item; target fills host. Prefer flex grow over
       height:100% so nested % height does not collapse the flex chain to 0. */
    host.style.minHeight = '0';
    host.style.minWidth = '0';
    host.style.flex =
      cs.flex && cs.flex !== '0 1 auto' ? cs.flex : '1 1 0%';
    host.style.flexGrow = cs.flexGrow && cs.flexGrow !== '0' ? cs.flexGrow : '1';
    host.style.flexShrink = cs.flexShrink || '1';
    host.style.alignSelf = cs.alignSelf && cs.alignSelf !== 'auto' ? cs.alignSelf : 'stretch';
    host.style.width = '100%';
    host.style.height = 'auto';
    el.style.width = '100%';
    el.style.height = '100%';
    el.style.minHeight = '0';
    el.style.minWidth = '0';
  }

  function copyLayoutToHost(el, host) {
    var cs = getComputedStyle(el);
    var pos = cs.position;
    var portH = el.offsetHeight;
    var portW = el.offsetWidth;
    var isScrollPort =
      cs.overflow === 'auto' ||
      cs.overflow === 'scroll' ||
      cs.overflowY === 'auto' ||
      cs.overflowY === 'scroll' ||
      cs.overflowX === 'auto' ||
      cs.overflowX === 'scroll';
    var heightIsPct =
      (cs.height && String(cs.height).indexOf('%') !== -1) ||
      el.style.height === '100%' ||
      (el.style.height && el.style.height.indexOf('%') !== -1);
    /* Never pin host to content-sized height (kills overflow / canY). */
    var contentSized =
      isScrollPort && portH > 0 && el.scrollHeight <= portH + 1;
    var flexFill = isFlexScrollChild(el, cs);

    if (pos === 'absolute' || pos === 'fixed') {
      /* Absolute ports come in two authoring patterns:
         A) Insight-style insets: left+right / top+bottom (no definite box size)
         B) Box-style: left+top+width+height (Monthly TW .monthly-scroll-data)
         getComputedStyle always resolves the residual inset (right/bottom) even for
         pattern B — copying that residual makes the host larger than the TW and
         content paints past the window with canX/thumb still on an oversized port. */
      host.style.position = pos;
      host.style.zIndex = el.style.zIndex || cs.zIndex;
      host.style.margin = el.style.margin || cs.margin;

      var insetPort =
        el.classList.contains('insight-overlay__scroll') ||
        el.classList.contains('pl-graph-overlay__scroll');

      if (insetPort) {
        host.style.left = el.style.left || (cs.left !== 'auto' ? cs.left : '');
        host.style.right = el.style.right || (cs.right !== 'auto' ? cs.right : '');
        host.style.top = el.style.top || (cs.top !== 'auto' ? cs.top : '');
        host.style.bottom = el.style.bottom || (cs.bottom !== 'auto' ? cs.bottom : '');
        host.style.width = el.style.width || '';
        host.style.height = el.style.height || '';
      } else {
        /* Box-style absolute (Monthly TW etc.): never copy residual right/bottom. */
        host.style.left = el.style.left || (cs.left !== 'auto' ? cs.left : '');
        host.style.top = el.style.top || (cs.top !== 'auto' ? cs.top : '');
        host.style.right = el.style.right || '';
        host.style.bottom = el.style.bottom || '';
        host.style.width = el.style.width || portW + 'px';
        host.style.height = el.style.height || portH + 'px';
        host.setAttribute('data-kpn-osb-box-w', String(portW));
        host.setAttribute('data-kpn-osb-box-h', String(portH));
      }

      el.style.position = 'relative';
      el.style.left = '0';
      el.style.right = 'auto';
      el.style.top = '0';
      el.style.bottom = 'auto';
      el.style.width = '100%';
      el.style.height = '100%';
      el.style.margin = '0';
      el.style.zIndex = '0';
    } else if (pos === 'relative') {
      host.style.position = 'relative';
      if (flexFill || heightIsPct || contentSized) {
        applyFlexFillHost(el, host, cs);
      } else if (isScrollPort && portH > 0 && el.scrollHeight > portH + 1) {
        host.style.width = el.style.width || '';
        host.style.flex = cs.flex || '';
        host.style.minHeight = '0';
        host.style.height = portH + 'px';
      } else {
        host.style.width = el.style.width || '';
        host.style.flex = cs.flex || '';
        host.style.minHeight = cs.minHeight !== 'auto' ? cs.minHeight : '';
        host.style.flexGrow = cs.flexGrow;
        host.style.flexShrink = cs.flexShrink;
        host.style.alignSelf = cs.alignSelf;
        host.style.height = el.style.height || '';
      }
    } else {
      /* static / sticky: host fills as block wrapper */
      host.style.display =
        cs.display === 'flex' || cs.display === 'grid' ? 'block' : cs.display;
      if (flexFill || heightIsPct || contentSized) {
        applyFlexFillHost(el, host, cs);
      } else if (isScrollPort && portH > 0 && el.scrollHeight > portH + 1) {
        host.style.height = portH + 'px';
        if (el.style.width) host.style.width = el.style.width;
        else if (isScrollPort && portW > 0 && cs.width && cs.width.indexOf('px') !== -1) {
          host.style.width = portW + 'px';
        }
      } else if (cs.height && cs.height !== 'auto' && el.style.height) {
        host.style.height = el.style.height;
        if (el.style.width) host.style.width = el.style.width;
      } else {
        if (el.style.width) {
          host.style.width = el.style.width;
        } else if (isScrollPort && portW > 0 && cs.width && cs.width.indexOf('px') !== -1) {
          host.style.width = portW + 'px';
        }
      }
    }
  }

  function isUnmeasurable(el) {
    if (!el || !el.isConnected) return true;
    if (el.closest('[hidden]')) return true;
    var node = el;
    while (node && node.nodeType === 1) {
      var cs = getComputedStyle(node);
      if (cs.display === 'none') return true;
      node = node.parentElement;
    }
    /* Either axis still 0 => layout not settled (flex open race). */
    return el.clientWidth < 2 || el.clientHeight < 2;
  }

  function watchPending(el) {
    if (!el || el._kpnOsbWatch) return;
    el._kpnOsbWatch = true;
    var finished = false;
    var ro = null;
    function cleanup() {
      if (finished) return;
      finished = true;
      try {
        if (ro) ro.disconnect();
      } catch (e) {}
      delete el._kpnOsbWatch;
    }
    function tryFlush() {
      if (finished) return;
      if (el.dataset.kpnOsb === '1') {
        cleanup();
        return;
      }
      if (isUnmeasurable(el)) return;
      cleanup();
      delete el.dataset.kpnOsbPending;
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

  function enhance(el) {
    if (!el || el.nodeType !== 1) return null;
    if (el.dataset.kpnOsb === '1') return el._kpnOsb || null;
    if (!needsOverlay()) return null;
    if (isUnmeasurable(el)) {
      el.dataset.kpnOsbPending = '1';
      watchPending(el);
      return null;
    }

    injectCss();
    document.documentElement.classList.add(ENABLED_HTML);

    var parent = el.parentNode;
    if (!parent) return null;

    delete el.dataset.kpnOsbPending;

    var host = document.createElement('div');
    host.className = HOST_CLASS;
    parent.insertBefore(host, el);
    host.appendChild(el);
    copyLayoutToHost(el, host);

    el.classList.add(TARGET_CLASS);
    el.dataset.kpnOsb = '1';

    var thumbY = document.createElement('div');
    thumbY.className = 'kpn-osb-thumb kpn-osb-thumb-y';
    thumbY.setAttribute('aria-hidden', 'true');
    var thumbX = document.createElement('div');
    thumbX.className = 'kpn-osb-thumb kpn-osb-thumb-x';
    thumbX.setAttribute('aria-hidden', 'true');
    host.appendChild(thumbY);
    host.appendChild(thumbX);

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
        var ratio = ch / sh;
        var th = Math.max(THUMB_MIN, Math.round(trackH * ratio));
        var maxTop = Math.max(trackH - th, 0);
        var top =
          sh <= ch ? 0 : Math.round((el.scrollTop / (sh - ch)) * maxTop);
        thumbY.style.height = th + 'px';
        thumbY.style.transform = 'translateY(' + top + 'px)';
        thumbY.style.display = '';
      } else {
        thumbY.style.display = 'none';
        thumbY.classList.remove('is-visible');
      }

      if (canX()) {
        var trackW = Math.max(cw - 4, THUMB_MIN);
        var ratioX = cw / sw;
        var tw = Math.max(THUMB_MIN, Math.round(trackW * ratioX));
        var maxLeft = Math.max(trackW - tw, 0);
        var left =
          sw <= cw ? 0 : Math.round((el.scrollLeft / (sw - cw)) * maxLeft);
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
    host.addEventListener('pointerenter', function () {
      sync();
      show();
    });
    host.addEventListener('pointerleave', function () {
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
      ro.observe(host);
    }

    var api = {
      el: el,
      host: host,
      sync: sync,
      show: show,
      scheduleHide: scheduleHide,
      remeasure: function () {
        if (isUnmeasurable(el)) return;
        var hcs = getComputedStyle(host);
        /* Absolute inset hosts must not keep a frozen px height (Insight blank band). */
        if (
          (hcs.position === 'absolute' || hcs.position === 'fixed') &&
          host.style.top &&
          host.style.bottom &&
          host.style.height &&
          String(host.style.height).indexOf('px') !== -1
        ) {
          host.style.height = '';
        }
        /* Monthly TW box-style absolute: drop residual right/bottom from older enhance. */
        if (
          el.classList.contains('monthly-scroll-data') &&
          (hcs.position === 'absolute' || hcs.position === 'fixed')
        ) {
          host.style.right = '';
          host.style.bottom = '';
          var boxW = parseFloat(host.getAttribute('data-kpn-osb-box-w') || '');
          var boxH = parseFloat(host.getAttribute('data-kpn-osb-box-h') || '');
          var parent = host.parentElement;
          var leftPx = parseFloat(host.style.left);
          if (parent && Number.isFinite(leftPx) && parent.clientWidth > 0) {
            host.style.width = Math.max(0, parent.clientWidth - leftPx) + 'px';
          } else if (Number.isFinite(boxW) && boxW > 0) {
            host.style.width = boxW + 'px';
          }
          if (Number.isFinite(boxH) && boxH > 0) {
            host.style.height = boxH + 'px';
          }
        }
        /* Drop content-sized pins; restore percentage fill. */
        if (host.style.height && el.scrollHeight > 0) {
          var pinned = parseFloat(host.style.height);
          if (
            Number.isFinite(pinned) &&
            pinned > 0 &&
            Math.abs(pinned - el.scrollHeight) <= 2
          ) {
            host.style.height = '100%';
            host.style.minHeight = '0';
          }
        }
        if (el.clientHeight < 2 && host.style.height && host.style.height.indexOf('px') !== -1) {
          host.style.height = '100%';
          host.style.minHeight = '0';
        }
        sync();
      },
      destroy: function () {
        if (ro) ro.disconnect();
        el.removeEventListener('scroll', onScroll);
        if (hideTimer) clearTimeout(hideTimer);
        if (thumbY.parentNode) thumbY.parentNode.removeChild(thumbY);
        if (thumbX.parentNode) thumbX.parentNode.removeChild(thumbX);
        if (host.parentNode) {
          host.parentNode.insertBefore(el, host);
          host.parentNode.removeChild(host);
        }
        el.classList.remove(TARGET_CLASS);
        el.style.width = '';
        el.style.height = '';
        el.style.minHeight = '';
        el.style.minWidth = '';
        el.style.position = '';
        el.style.left = '';
        el.style.top = '';
        el.style.right = '';
        el.style.bottom = '';
        el.style.margin = '';
        el.style.zIndex = '';
        delete el.dataset.kpnOsb;
        delete el.dataset.kpnOsbPending;
        delete el._kpnOsb;
        instances = instances.filter(function (x) {
          return x !== api;
        });
      }
    };
    el._kpnOsb = api;
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

  function flushPending(root) {
    root = root || document;
    var pending = root.querySelectorAll
      ? root.querySelectorAll('[data-kpn-osb-pending="1"]')
      : [];
    var out = [];
    for (var i = 0; i < pending.length; i++) {
      var el = pending[i];
      if (isUnmeasurable(el)) continue;
      delete el.dataset.kpnOsbPending;
      var api = enhance(el);
      if (api) out.push(api);
    }
    return out;
  }

  function refreshAll(root) {
    if (!needsOverlay()) return [];
    enhanceAll(root || document);
    flushPending(root || document);
    for (var i = 0; i < instances.length; i++) {
      if (instances[i] && typeof instances[i].remeasure === 'function') {
        instances[i].remeasure();
      }
    }
    return instances.slice();
  }

  function destroyAnnualTwWrappers() {
    for (var i = 0; i < ANNUAL_TW_SELECTORS.length; i++) {
      var nodes = document.querySelectorAll(ANNUAL_TW_SELECTORS[i]);
      for (var j = 0; j < nodes.length; j++) {
        var el = nodes[j];
        if (el._kpnOsb && typeof el._kpnOsb.destroy === 'function') {
          el._kpnOsb.destroy();
        }
      }
    }
  }

  function enhanceAll(root) {
    if (!needsOverlay()) {
      document.documentElement.classList.remove(ENABLED_HTML);
      return [];
    }
    injectCss();
    document.documentElement.classList.add(ENABLED_HTML);
    root = root || document;
    var out = [];
    for (var i = 0; i < SELECTORS.length; i++) {
      var nodes = root.querySelectorAll
        ? root.querySelectorAll(SELECTORS[i])
        : [];
      for (var j = 0; j < nodes.length; j++) {
        var api = enhance(nodes[j]);
        if (api) out.push(api);
      }
    }
    flushPending(root);
    return out;
  }

  function boot() {
    try {
      reducedMotion =
        !!(
          global.matchMedia &&
          global.matchMedia('(prefers-reduced-motion: reduce)').matches
        );
    } catch (e) {
      reducedMotion = false;
    }
    measureNativeScrollbarWidth();
    destroyAnnualTwWrappers();
    if (!needsOverlay()) return;
    enhanceAll(document);
    if (typeof MutationObserver !== 'undefined') {
      var moRefreshQueued = false;
      function queueRefreshAll() {
        if (moRefreshQueued) return;
        moRefreshQueued = true;
        function run() {
          moRefreshQueued = false;
          refreshAll(document);
        }
        if (typeof requestAnimationFrame === 'function') {
          /* Overlay open/close toggles [hidden] — enhance after layout settles.
             Do NOT watch style attrs: PL Insight chart style thrash was blocking scroll ~10s. */
          requestAnimationFrame(function () {
            requestAnimationFrame(run);
          });
        } else {
          run();
        }
      }
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
    SELECTORS: SELECTORS,
    measureNativeScrollbarWidth: measureNativeScrollbarWidth,
    needsOverlay: needsOverlay,
    enhance: enhance,
    enhanceAll: enhanceAll,
    refresh: refreshAll,
    refreshAll: refreshAll,
    remeasure: refreshAll,
    destroyAnnualTwWrappers: destroyAnnualTwWrappers,
    boot: boot,
    getNativeScrollbarWidth: function () {
      return measureNativeScrollbarWidth();
    },
    getInstances: function () {
      return instances.slice();
    }
  };
  global.KpiOverlayScrollbar = api;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})(typeof window !== 'undefined' ? window : this);
