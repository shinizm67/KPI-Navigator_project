      /* INSIGHT-TAB-CROSS-LINKS */
      function goInsightTabSection(tab, targetId) {
        setInsightTab(tab);
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            var target = document.getElementById(targetId);
            if (target) scrollInsightToTarget(target);
          });
        });
      }
      root.addEventListener('click', function (ev) {
        var analyzeLink = ev.target && ev.target.closest ? ev.target.closest('.insight-graph-analyze-link') : null;
        if (analyzeLink && root.contains(analyzeLink)) {
          var analyzeHref = analyzeLink.getAttribute('href');
          if (!analyzeHref || analyzeHref.charAt(0) !== '#') return;
          var analyzeTargetId = analyzeHref.slice(1);
          if (analyzeTargetId.indexOf('insight-jump-analyze-') !== 0) return;
          ev.preventDefault();
          goInsightTabSection('analyze', analyzeTargetId);
          return;
        }
        var graphLink =
          ev.target && ev.target.closest ? ev.target.closest('.insight-daily-summary-graph-link') : null;
        if (!graphLink || !root.contains(graphLink)) return;
        var graphHref = graphLink.getAttribute('href');
        if (!graphHref || graphHref.charAt(0) !== '#') return;
        var graphTargetId = graphHref.slice(1);
        if (graphTargetId.indexOf('insight-jump-graph-') !== 0) return;
        ev.preventDefault();
        goInsightTabSection('graph', graphTargetId);
      });
