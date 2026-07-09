      /* SDM-WEEKDAY-QUALITY (Phase 11-7) */
      (function () {
        var root = document.getElementById('sdm-weekday-quality');
        if (!root) return;

        var badgeEl = document.getElementById('sdm-weekday-quality-badge');
        var msgEl = document.getElementById('sdm-weekday-quality-msg');
        var recalcUntil = 0;
        var RECALC_MS = 12000;

        function storeReady() {
          return !!(
            window.KpiYearStore &&
            typeof KpiYearStore.assessWeekdayTargetQuality === 'function' &&
            typeof KpiYearStore.getOperatingYear === 'function'
          );
        }

        function isJa() {
          return (
            String(document.documentElement.getAttribute('lang') || '')
              .toLowerCase()
              .indexOf('ja') === 0
          );
        }

        function t(ja, en) {
          return isJa() ? ja : en;
        }

        function monthLabel(m0) {
          if (isJa()) return m0 + 1 + '月';
          var names = [
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
          ];
          return names[m0] || String(m0 + 1);
        }

        function formatMonthList(months) {
          if (!months || !months.length) return '';
          return months
            .map(function (m) {
              return monthLabel(Number(m));
            })
            .join(isJa() ? '、' : ', ');
        }

        function setTone(tone) {
          root.classList.remove(
            'sdm-weekday-quality--info',
            'sdm-weekday-quality--ok'
          );
          if (tone === 'ok') root.classList.add('sdm-weekday-quality--ok');
          else if (tone === 'info') root.classList.add('sdm-weekday-quality--info');
        }

        function show(badge, message, tone) {
          if (badgeEl) badgeEl.textContent = badge;
          if (msgEl) msgEl.textContent = message;
          setTone(tone || 'warn');
          root.removeAttribute('hidden');
        }

        function hide() {
          root.setAttribute('hidden', '');
          if (msgEl) msgEl.textContent = '';
        }

        function markRecalculated() {
          recalcUntil = Date.now() + RECALC_MS;
        }

        function buildQualityMessage(quality) {
          if (!quality) return null;
          if (quality.mode === 'monthly-flat') {
            return {
              badge: t('設定', 'Setting'),
              msg: t(
                'いまは「月内均等」です。毎日の目標売上は同じ金額になります。',
                'Daily targets use flat mode: the same amount every business day.'
              ),
              tone: 'info',
            };
          }
          if (quality.usingFlatFallback) {
            return {
              badge: t('注意', 'Notice'),
              msg: t(
                '「曜日加重」を選んでいますが、過去の売上データが足りません。いまは月内均等（毎日同じ目標）で計算しています。Past Sales に過去の売上を保存すると、曜日ごとの目標に切り替わります。',
                'Weekday weighting is selected, but past sales data is insufficient. Targets are calculated as flat (equal each day) for now. Save past years in Past Sales to enable weekday-based targets.'
              ),
              tone: 'warn',
            };
          }
          if (quality.fallbackMonths && quality.fallbackMonths.length) {
            var monthText = formatMonthList(quality.fallbackMonths);
            return {
              badge: t('注意', 'Notice'),
              msg: t(
                monthText +
                  'は過去データが薄いため、その月だけ均等配分（曜日差なし）で目標を出しています。Past Sales のデータを増やすと精度が上がります。',
                'For ' +
                  monthText +
                  ', past data is thin so targets use even split (no weekday pattern). Add more Past Sales data to improve accuracy.'
              ),
              tone: 'warn',
            };
          }
          return {
            badge: t('OK', 'OK'),
            msg: t(
              '過去の売上データに基づき、曜日ごとの日次目標を計算しています。',
              'Daily targets are calculated from your past sales by weekday.'
            ),
            tone: 'ok',
          };
        }

        function render() {
          if (!storeReady()) {
            hide();
            return;
          }
          if (Date.now() < recalcUntil) {
            show(
              t('更新', 'Updated'),
              t(
                '過去売上を保存しました。表の日次目標（Target Sales）を再計算しました。',
                'Past sales saved. Daily targets (Target Sales) have been recalculated.'
              ),
              'info'
            );
            return;
          }
          var oy = KpiYearStore.getOperatingYear();
          var quality = KpiYearStore.assessWeekdayTargetQuality(oy);
          if (!quality || quality.mode === 'monthly-flat') {
            hide();
            return;
          }
          if (!quality.usingFlatFallback && !(quality.fallbackMonths && quality.fallbackMonths.length)) {
            hide();
            return;
          }
          var built = buildQualityMessage(quality);
          if (!built || built.tone === 'ok') {
            hide();
            return;
          }
          show(built.badge, built.msg, built.tone);
        }

        document.addEventListener('kpi:dailyTargetModeChanged', render);
        document.addEventListener('kpi:weekdayBaselineChanged', render);
        document.addEventListener('annual:pastSalesSaved', function () {
          markRecalculated();
          render();
        });

        window.__SDM_WEEKDAY_QUALITY = { render: render, markRecalculated: markRecalculated };
        render();
      })();
