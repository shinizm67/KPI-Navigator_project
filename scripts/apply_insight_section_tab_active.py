#!/usr/bin/env python3
"""Highlight Insight Daily/Monthly/Annual jump tabs for the in-view section."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "app/monthly/index.html",
    ROOT / "app/annual/index.html",
    ROOT / "en/app/monthly/index.html",
    ROOT / "en/app/annual/index.html",
]

CSS_OLD = """    .insight-overlay__tab--main.is-active {
      width: 131px;
      height: 30px;
      font-size: 20px;
      background: rgba(88, 225, 243, 0.7);
    }
    .insight-overlay__tab--jump {
      width: 100px;
      height: 28px;
      font-size: 16px;
      background: rgba(88, 225, 243, 0.33);
    }
"""

CSS_NEW = """    .insight-overlay__tab--main.is-active {
      width: 131px;
      height: 30px;
      font-size: 20px;
      background: rgba(88, 225, 243, 0.7);
      box-shadow:
        0 0 12px rgba(88, 225, 243, 0.75),
        0 0 20px rgba(88, 225, 243, 0.3),
        inset 0 0 8px rgba(88, 225, 243, 0.25);
    }
    .insight-overlay__tab--jump {
      width: 100px;
      height: 28px;
      font-size: 16px;
      background: rgba(88, 225, 243, 0.33);
      transition: background 0.15s ease, box-shadow 0.15s ease, color 0.15s ease,
        border-color 0.15s ease;
    }
    .insight-overlay__tab--jump.is-active {
      background: rgba(88, 225, 243, 0.72);
      border-color: #9af0ff;
      color: #d7fbff;
      font-weight: 700;
      box-shadow:
        0 0 12px rgba(88, 225, 243, 0.85),
        0 0 22px rgba(88, 225, 243, 0.35),
        inset 0 0 10px rgba(88, 225, 243, 0.28);
    }
    .office-mode .insight-overlay__tab--jump {
      background: #f0f0f0;
      border-color: #999;
      color: #111;
      box-shadow: none;
      font-weight: 400;
    }
    .office-mode .insight-overlay__tab--jump.is-active {
      background: #e2e2e2;
      border-color: #666;
      color: #111;
      box-shadow: none;
      font-weight: 700;
    }
    .office-mode .insight-overlay__tab--main.is-active {
      background: #e2e2e2;
      border-color: #666;
      color: #111;
      box-shadow: none;
    }
"""

JS_OLD = """      function updateInsightJumpHrefs() {
        var pane = 'summary';
        if (paneAnalyze && !paneAnalyze.hidden) pane = 'analyze';
        else if (paneGraph && !paneGraph.hidden) pane = 'graph';
        var p = 'insight-jump-' + pane + '-';
        if (jumpDaily) jumpDaily.setAttribute('href', '#' + p + 'daily');
        if (jumpMonthly) jumpMonthly.setAttribute('href', '#' + p + 'monthly');
        if (jumpAnnual) jumpAnnual.setAttribute('href', '#' + p + 'annual');
      }
"""

JS_NEW = """      function updateInsightJumpHrefs() {
        var pane = 'summary';
        if (paneAnalyze && !paneAnalyze.hidden) pane = 'analyze';
        else if (paneGraph && !paneGraph.hidden) pane = 'graph';
        var p = 'insight-jump-' + pane + '-';
        if (jumpDaily) jumpDaily.setAttribute('href', '#' + p + 'daily');
        if (jumpMonthly) jumpMonthly.setAttribute('href', '#' + p + 'monthly');
        if (jumpAnnual) jumpAnnual.setAttribute('href', '#' + p + 'annual');
      }
      function syncInsightJumpActive(which) {
        which = which || 'daily';
        if (jumpDaily) {
          jumpDaily.classList.toggle('is-active', which === 'daily');
          if (which === 'daily') jumpDaily.setAttribute('aria-current', 'true');
          else jumpDaily.removeAttribute('aria-current');
        }
        if (jumpMonthly) {
          jumpMonthly.classList.toggle('is-active', which === 'monthly');
          if (which === 'monthly') jumpMonthly.setAttribute('aria-current', 'true');
          else jumpMonthly.removeAttribute('aria-current');
        }
        if (jumpAnnual) {
          jumpAnnual.classList.toggle('is-active', which === 'annual');
          if (which === 'annual') jumpAnnual.setAttribute('aria-current', 'true');
          else jumpAnnual.removeAttribute('aria-current');
        }
      }
      function updateInsightJumpFromScroll() {
        if (!insightScroll) return;
        var pane = 'summary';
        if (paneAnalyze && !paneAnalyze.hidden) pane = 'analyze';
        else if (paneGraph && !paneGraph.hidden) pane = 'graph';
        var keys = ['daily', 'monthly', 'annual'];
        var pick = 'daily';
        for (var i = 0; i < keys.length; i++) {
          var el = document.getElementById('insight-jump-' + pane + '-' + keys[i]);
          if (!el) continue;
          var top =
            el.getBoundingClientRect().top - insightScroll.getBoundingClientRect().top;
          if (top <= 40) pick = keys[i];
        }
        syncInsightJumpActive(pick);
      }
"""

BIND_OLD = """      function bindInsightJumpLink(link) {
        if (!link) return;
        link.addEventListener('click', function (ev) {
          var href = link.getAttribute('href');
          if (!href || href.charAt(0) !== '#') return;
          var target = document.getElementById(href.slice(1));
          if (!target || !root.contains(target)) return;
          ev.preventDefault();
          scrollInsightToTarget(target);
        });
      }
"""

BIND_NEW = """      function bindInsightJumpLink(link) {
        if (!link) return;
        link.addEventListener('click', function (ev) {
          var href = link.getAttribute('href');
          if (!href || href.charAt(0) !== '#') return;
          var target = document.getElementById(href.slice(1));
          if (!target || !root.contains(target)) return;
          ev.preventDefault();
          var which = 'daily';
          if (href.indexOf('monthly') >= 0) which = 'monthly';
          else if (href.indexOf('annual') >= 0) which = 'annual';
          syncInsightJumpActive(which);
          scrollInsightToTarget(target);
        });
      }
"""

WIRE_OLD = """      updateInsightJumpHrefs();
      bindInsightJumpLink(jumpDaily);
      bindInsightJumpLink(jumpMonthly);
      bindInsightJumpLink(jumpAnnual);
"""

WIRE_NEW = """      updateInsightJumpHrefs();
      bindInsightJumpLink(jumpDaily);
      bindInsightJumpLink(jumpMonthly);
      bindInsightJumpLink(jumpAnnual);
      syncInsightJumpActive('daily');
      if (insightScroll) {
        var insightJumpScrollT = null;
        insightScroll.addEventListener(
          'scroll',
          function () {
            if (insightJumpScrollT) return;
            insightJumpScrollT = requestAnimationFrame(function () {
              insightJumpScrollT = null;
              updateInsightJumpFromScroll();
            });
          },
          { passive: true }
        );
      }
"""

SET_TAB_SNIPPET_OLD = """        if (insightScroll) insightScroll.scrollTop = 0;
        updateInsightJumpHrefs();
"""

SET_TAB_SNIPPET_NEW = """        if (insightScroll) insightScroll.scrollTop = 0;
        updateInsightJumpHrefs();
        syncInsightJumpActive('daily');
"""


def patch(text: str) -> str:
    if "syncInsightJumpActive" in text and ".insight-overlay__tab--jump.is-active" in text:
        return text
    if CSS_OLD not in text:
        raise SystemExit("insight tab CSS anchor miss")
    text = text.replace(CSS_OLD, CSS_NEW, 1)
    if JS_OLD not in text:
        raise SystemExit("updateInsightJumpHrefs miss")
    text = text.replace(JS_OLD, JS_NEW, 1)
    if BIND_OLD not in text:
        raise SystemExit("bindInsightJumpLink miss")
    text = text.replace(BIND_OLD, BIND_NEW, 1)
    if WIRE_OLD not in text:
        raise SystemExit("jump link wire miss")
    text = text.replace(WIRE_OLD, WIRE_NEW, 1)
    if SET_TAB_SNIPPET_OLD not in text:
        raise SystemExit("setInsightTab jump sync miss")
    text = text.replace(SET_TAB_SNIPPET_OLD, SET_TAB_SNIPPET_NEW, 1)
    return text


def main() -> None:
    for page in PAGES:
        raw = page.read_text(encoding="utf-8")
        page.write_text(patch(raw), encoding="utf-8")
        print("patched", page.relative_to(ROOT))


if __name__ == "__main__":
    main()
