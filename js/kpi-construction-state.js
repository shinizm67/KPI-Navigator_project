/**
 * KPN Construction State — scramble hero for unfinished pages.
 * Sci-Fi: decode-style scramble then readable English hold.
 * Office: freeze on COMING SOON (no scramble).
 */
(function (global) {
  'use strict';

  var PHRASES = ['COMING SOON', 'UNDER CONSTRUCTION', 'WORK IN PROGRESS'];
  var IDLE = 'COMING SOON';
  var CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?<>[]{}+-_=*';
  var SCRAMBLE_MS = 1000;
  var HOLD_MS = 8000;
  var TICK_MS = 40;
  var REVEAL_START_MS = 400;

  function randomText(len) {
    var out = '';
    var i;
    for (i = 0; i < len; i++) out += CHARS.charAt(Math.floor(Math.random() * CHARS.length));
    return out;
  }

  function isOffice(bodyEl) {
    return !!(bodyEl && bodyEl.classList && bodyEl.classList.contains('office-mode'));
  }

  function bind(opts) {
    opts = opts || {};
    var textEl = opts.textEl || document.getElementById('coming-soon-text');
    var bodyEl = opts.bodyEl || document.getElementById('body-el') || document.body;
    if (!textEl || !bodyEl) return null;

    var phrases = opts.phrases || PHRASES;
    var idleLabel = opts.idleLabel || IDLE;
    var index = 0;
    var running = false;
    var timer = 0;

    function clearTimer() {
      if (timer) {
        clearTimeout(timer);
        timer = 0;
      }
    }

    function freeze() {
      clearTimer();
      running = false;
      textEl.textContent = idleLabel;
    }

    function animatePhrase(target, done) {
      var started = Date.now();
      function tick() {
        if (isOffice(bodyEl)) {
          freeze();
          return;
        }
        var elapsed = Date.now() - started;
        if (elapsed < REVEAL_START_MS) {
          textEl.textContent = randomText(target.length);
          timer = setTimeout(tick, TICK_MS);
          return;
        }
        if (elapsed < SCRAMBLE_MS) {
          var p = (elapsed - REVEAL_START_MS) / (SCRAMBLE_MS - REVEAL_START_MS);
          var revealed = Math.min(target.length, Math.floor(p * target.length));
          textEl.textContent = target.slice(0, revealed) + randomText(Math.max(target.length - revealed, 0));
          timer = setTimeout(tick, TICK_MS);
          return;
        }
        textEl.textContent = target;
        timer = setTimeout(done, HOLD_MS);
      }
      tick();
    }

    function loop() {
      if (running) return;
      if (isOffice(bodyEl)) {
        freeze();
        return;
      }
      running = true;
      animatePhrase(phrases[index], function () {
        index = (index + 1) % phrases.length;
        running = false;
        loop();
      });
    }

    var observer = new MutationObserver(function () {
      running = false;
      clearTimer();
      loop();
    });
    observer.observe(bodyEl, { attributes: true, attributeFilter: ['class'] });
    loop();
    return { freeze: freeze, loop: loop };
  }

  function autoBind() {
    if (document.getElementById('coming-soon-text')) bind({});
  }

  global.KpiConstructionState = {
    bind: bind,
    phrases: PHRASES,
    idleLabel: IDLE,
    scrambleMs: SCRAMBLE_MS,
    holdMs: HOLD_MS
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoBind);
  } else {
    autoBind();
  }
})(typeof window !== 'undefined' ? window : this);
