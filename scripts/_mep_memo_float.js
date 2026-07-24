
      /* MEMO-FLOAT-MODAL */
      var memoFloatRoot = document.getElementById('memo-float-modal');
      var memoFloatBackdrop = document.getElementById('memo-float-backdrop');
      var memoFloatClose = document.getElementById('memo-float-close');
      var memoFloatUndo = document.getElementById('memo-float-undo');
      var memoFloatSave = document.getElementById('memo-float-save');
      var memoFloatMonthLabel = document.getElementById('memo-float-month-label');
      var memoFloatPrevMonth = document.getElementById('memo-float-prev-month');
      var memoFloatNextMonth = document.getElementById('memo-float-next-month');
      var memoFloatToday = document.getElementById('memo-float-today');
      var memoFloatDateRail = document.getElementById('memo-float-date-rail');
      var memoFloatDayPanel = document.getElementById('memo-float-day-panel');
      var memoFloatCloseChooser = document.getElementById('memo-float-close-chooser');
      var memoFloatCloseChooserScrim = document.getElementById('memo-float-close-chooser-scrim');
      var memoFloatCloseSave = document.getElementById('memo-float-close-save');
      var memoFloatCloseDiscard = document.getElementById('memo-float-close-discard');
      var memoFloatCloseCancel = document.getElementById('memo-float-close-cancel');
      var memoFloatState = {
        year: mefYear,
        month0: mefMonth0,
        focusIso: null,
        focusRowId: null,
        dirty: false,
        sessionSaved: true
      };
      var memoFloatUndoStack = [];
      var memoFloatOpenSnapshot = '';
      var memoFloatCloseResolve = null;
      var memoFloatCloseReturnFocus = null;

      function memoCharLimits() {
        return useJa
          ? { hard: 300, tiers: [200, 300] }
          : { hard: 500, tiers: [200, 300, 500] };
      }
      function memoCharTierClass(tier) {
        return 'memo-float-modal__char-count--' + tier;
      }

      function memoFloatBizDay(iso) {
        if (!iso) return false;
        if (Object.prototype.hasOwnProperty.call(bizDayByIso, iso)) {
          return bizDayByIso[iso] !== false;
        }
        var daily = ensureAnnualDailyStore();
        if (daily) {
          var bmap = daily.businessDayByDate || {};
          var tmap = daily.targetSalesByDate || {};
          if (Object.prototype.hasOwnProperty.call(bmap, iso)) return !!bmap[iso];
          if (Object.prototype.hasOwnProperty.call(tmap, iso)) {
            var n = Number(tmap[iso]);
            return Number.isFinite(n) ? n !== 0 : true;
          }
        }
        return true;
      }
      function syncBizDayForMemoFloatMonth(year, month0) {
        var daily = ensureAnnualDailyStore();
        var bmap = (daily && daily.businessDayByDate) || {};
        var tmap = (daily && daily.targetSalesByDate) || {};
        monthIsoList(year, month0).forEach(function (iso) {
          if (Object.prototype.hasOwnProperty.call(bmap, iso)) {
            bizDayByIso[iso] = !!bmap[iso];
            return;
          }
          if (Object.prototype.hasOwnProperty.call(tmap, iso)) {
            var n = Number(tmap[iso]);
            bizDayByIso[iso] = Number.isFinite(n) ? n !== 0 : true;
            return;
          }
          if (bizDayByIso[iso] == null) bizDayByIso[iso] = true;
        });
      }
      function ensureMemoFloatYearData(year, month0) {
        if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {
          flushPendingMemoFloatTextareasFromDom();
        }
        if (mepStoreReady()) loadMepFromYearStore(year);
        syncBizDayForMemoFloatMonth(year, month0);
      }

      function memoFloatLabels() {
        return useJa
          ? {
              windowTitle: '日次メモ',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo（自由記述）',
              addFreeMemo: '自由メモを追加',
              today: 'Today',
              prevMonth: '先月',
              nextMonth: '翌月'
            }
          : {
              windowTitle: 'Daily Notes',
              todaySales: "Today's Sales",
              targetSales: "Today's Target Sales",
              diff: 'Difference',
              achievement: 'Achievement',
              weather: 'Weather',
              freeMemoSection: 'Memo',
              addFreeMemo: 'Add free memo',
              today: 'Today',
              prevMonth: 'Prev',
              nextMonth: 'Next'
            };
      }
      function snapshotMemoFloatState() {
        return JSON.stringify({
          memoValueById: sortedNestedMap(memoValueById),
          memoItems: rowSnapshot(state.memoItems)
        });
      }
      function restoreMemoFloatState(json) {
        var snap = JSON.parse(json);
        memoValueById = snap.memoValueById || memoValueById;
        state.memoItems = snap.memoItems || state.memoItems;
        syncWeeklyMemoItems();
      }
      function pushMemoFloatUndo() {
        memoFloatUndoStack.push(snapshotMemoFloatState());
        if (memoFloatUndoStack.length > 30) memoFloatUndoStack.shift();
        if (memoFloatUndo) memoFloatUndo.disabled = memoFloatUndoStack.length === 0;
      }
      function popMemoFloatUndo() {
        if (!memoFloatUndoStack.length) return false;
        restoreMemoFloatState(memoFloatUndoStack.pop());
        if (memoFloatUndo) memoFloatUndo.disabled = memoFloatUndoStack.length === 0;
        memoFloatState.dirty = true;
        memoFloatState.sessionSaved = false;
        markDirty();
        renderMemoFloatDayPanel();
        return true;
      }
      function weatherLabelForIso(iso) {
        var code = readWeather(iso);
        for (var wi = 0; wi < MEF_WEATHER_PRESETS.length; wi++) {
          if (MEF_WEATHER_PRESETS[wi].code === code) {
            return useJa ? MEF_WEATHER_PRESETS[wi].ja : MEF_WEATHER_PRESETS[wi].en;
          }
        }
        return code || '—';
      }
      function memoDayKpi(iso) {
        var sales = memoFloatBizDay(iso) ? Math.round(aggregateValue('totalSales', iso)) : 0;
        var target = 0;
        var dt = isoToDate(iso);
        if (dt) {
          var res = sumTargetByDateRange(dt, dt);
          target = Math.round(res.total || 0);
        }
        var diff = sales - target;
        var rate = target > 0 ? (sales / target) * 100 : 0;
        return { sales: sales, target: target, diff: diff, rate: rate };
      }
      function ensureTwDiffExports() {
        if (typeof window.__twFmtDiff === 'function') return;
        var isJa = document.documentElement.getAttribute('lang') === 'ja';
        window.__twDiffLevels = [
          'tw-diff--win',
          'tw-diff--neutral',
          'tw-diff--sev-90',
          'tw-diff--sev-80',
          'tw-diff--sev-70',
          'tw-diff--sev-60',
          'tw-diff--sev-50',
          'tw-diff--sev-below',
        ];
        window.__twDiffSeverityClass = function (actual, target) {
          if (!Number.isFinite(actual) || !Number.isFinite(target) || target <= 0) {
            return 'tw-diff--neutral';
          }
          var diff = actual - target;
          if (diff > 0) return 'tw-diff--win';
          if (diff === 0) return 'tw-diff--neutral';
          var ach = (actual / target) * 100;
          if (ach >= 90) return 'tw-diff--sev-90';
          if (ach >= 80) return 'tw-diff--sev-80';
          if (ach >= 70) return 'tw-diff--sev-70';
          if (ach >= 60) return 'tw-diff--sev-60';
          if (ach >= 50) return 'tw-diff--sev-50';
          return 'tw-diff--sev-below';
        };
        window.__twFmtDiff = function (actual, target) {
          if (!Number.isFinite(actual) || !Number.isFinite(target)) return '—';
          var n = actual - target;
          if (n === 0) {
            if (typeof window.__twFmtMoney === 'function') return window.__twFmtMoney(0);
            return window.KpiCurrency ? KpiCurrency.zero() : ((document.documentElement.lang || '').indexOf('ja') === 0 ? '¥0' : '$0');
          }
          var r = Math.round(Math.abs(n));
          var body = isJa
            ? '¥' + r.toLocaleString('ja-JP')
            : '$' + r.toLocaleString('en-US');
          return (n > 0 ? '+' : '−') + body;
        };
      }
      function applyTwDiffSurfaceEl(el, actual, target) {
        if (!el) return;
        ensureTwDiffExports();
        var levels = window.__twDiffLevels || [];
        for (var i = 0; i < levels.length; i++) el.classList.remove(levels[i]);
        if (typeof window.__twDiffSeverityClass === 'function') {
          el.classList.add(window.__twDiffSeverityClass(actual, target));
        }
      }
      window.applyTwDiffSurfaceEl = applyTwDiffSurfaceEl;
      function updateMemoCharCount(ta, counter) {
        if (!ta || !counter) return;
        var limits = memoCharLimits();
        var tiers = limits.tiers;
        var hard = limits.hard;
        var len = String(ta.value || '').length;
        if (len > hard) {
          ta.value = ta.value.slice(0, hard);
          len = hard;
        }
        tiers.forEach(function (tier) {
          counter.classList.remove(memoCharTierClass(tier));
        });
        var activeTier = tiers[tiers.length - 1];
        for (var ti = 0; ti < tiers.length; ti++) {
          if (len <= tiers[ti]) {
            activeTier = tiers[ti];
            break;
          }
        }
        counter.classList.add(memoCharTierClass(activeTier));
        counter.textContent = len + '/' + activeTier;
      }
      function startMemoLabelEdit(host, row) {
        if (!host || !row || row.weeklyFixed) return;
        var old = rowLabel(row);
        host.innerHTML = '';
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'memo-float-modal__memo-head-label-input';
        input.value = old;
        input.setAttribute('aria-label', t('メモタイトルを編集', 'Edit memo title'));
        input.maxLength = 48;
        host.appendChild(input);
        input.focus();
        input.select();
        var commit = function (ok) {
          var val = String(input.value || '').trim();
          if (ok && val !== '' && val !== old) {
            pushMemoFloatUndo();
            if (useJa) row.labelJa = val;
            else row.labelEn = val;
            memoFloatState.dirty = true;
            memoFloatState.sessionSaved = false;
            markDirty();
          }
          renderMemoFloatDayPanel();
        };
        input.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter') {
            ev.preventDefault();
            commit(true);
          } else if (ev.key === 'Escape') {
            ev.preventDefault();
            commit(false);
          }
        });
        input.addEventListener('blur', function () {
          commit(true);
        });
      }
      function mountMemoHeadLabel(host, row) {
        if (!host || !row) return;
        host.innerHTML = '';
        if (row.editableLabel !== false && !row.weeklyFixed) {
          var labelBtn = document.createElement('button');
          labelBtn.type = 'button';
          labelBtn.className = 'memo-float-modal__memo-head-label is-editable';
          labelBtn.textContent = rowLabel(row);
          labelBtn.setAttribute('aria-label', t('メモタイトルを編集', 'Edit memo title'));
          labelBtn.addEventListener('click', function () {
            startMemoLabelEdit(host, row);
          });
          host.appendChild(labelBtn);
        } else {
          var headLbl = document.createElement('div');
          headLbl.className = 'memo-float-modal__memo-head-label';
          headLbl.textContent = rowLabel(row);
          host.appendChild(headLbl);
        }
      }
      function memoFloatAddRow(afterIdx) {
        pushMemoFloatUndo();
        addFreeMemoRow(afterIdx);
        memoFloatState.dirty = true;
        memoFloatState.sessionSaved = false;
        markDirty();
        renderMemoFloatDayPanel();
      }
      function memoFloatRemoveRow(removeIdx) {
        if (isWeeklyFixedMemoIndex(removeIdx)) return;
        pushMemoFloatUndo();
        if (!removeFreeMemoRowAt(removeIdx)) return;
        memoFloatState.dirty = true;
        memoFloatState.sessionSaved = false;
        markDirty();
        renderMemoFloatDayPanel();
      }
      function appendMemoFloatBlock(parent, row, idx, iso, withControls) {
        var block = document.createElement('div');
        block.className = 'memo-float-modal__memo-block';
        block.setAttribute('data-memo-row-id', row.id);
        if (row.weeklyFixed) block.classList.add('memo-float-modal__memo-block--fixed');
        var head = document.createElement('div');
        head.className = 'memo-float-modal__memo-head';
        var headLblWrap = document.createElement('div');
        headLblWrap.className = 'memo-float-modal__memo-head-label-wrap';
        mountMemoHeadLabel(headLblWrap, row);
        head.appendChild(headLblWrap);
        if (withControls) {
          var ctrls = document.createElement('div');
          ctrls.className = 'memo-float-modal__memo-controls';
          var plus = document.createElement('button');
          plus.type = 'button';
          plus.textContent = '+';
          plus.setAttribute('aria-label', t('この下に自由メモを追加', 'Add free memo below'));
          (function (i) {
            plus.addEventListener('click', function () {
              memoFloatAddRow(i);
            });
          })(idx);
          var minus = document.createElement('button');
          minus.type = 'button';
          minus.textContent = '−';
          minus.setAttribute('aria-label', t('この自由メモ行を削除', 'Remove this free memo row'));
          (function (i) {
            minus.addEventListener('click', function () {
              memoFloatRemoveRow(i);
            });
          })(idx);
          ctrls.appendChild(plus);
          ctrls.appendChild(minus);
          head.appendChild(ctrls);
        }
        block.appendChild(head);
        var taWrap = document.createElement('div');
        taWrap.className = 'memo-float-modal__textarea-wrap';
        var counter = document.createElement('div');
        counter.className = 'memo-float-modal__char-count';
        var ta = document.createElement('textarea');
        ta.className = 'memo-float-modal__textarea';
        ta.value = readMemo(row.id, iso);
        ta.setAttribute('data-row-id', row.id);
        ta.setAttribute('data-iso', iso);
        ta.setAttribute('aria-label', rowLabel(row));
        if (!memoFloatBizDay(iso)) ta.disabled = true;
        updateMemoCharCount(ta, counter);
        ta.addEventListener('input', function () {
          updateMemoCharCount(ta, counter);
          writeMemo(row.id, iso, ta.value);
          memoFloatState.dirty = true;
          memoFloatState.sessionSaved = false;
          markDirty();
        });
        ta.addEventListener('focus', function () {
          ta.dataset.memoPrev = readMemo(row.id, iso);
        });
        ta.addEventListener('change', function () {
          var prev = ta.dataset.memoPrev == null ? '' : String(ta.dataset.memoPrev);
          if (prev !== ta.value) pushMemoFloatUndo();
          writeMemo(row.id, iso, ta.value);
          memoFloatState.dirty = true;
          memoFloatState.sessionSaved = false;
          markDirty();
          ta.dataset.memoPrev = ta.value;
        });
        taWrap.appendChild(counter);
        taWrap.appendChild(ta);
        block.appendChild(taWrap);
        parent.appendChild(block);
      }
      function renderMemoFloatDateRail() {
        if (!memoFloatDateRail) return;
        ensureMemoFloatYearData(memoFloatState.year, memoFloatState.month0);
        var isoList = monthIsoList(memoFloatState.year, memoFloatState.month0);
        memoFloatDateRail.innerHTML = '';
        isoList.forEach(function (iso, idx) {
          var dt = new Date(memoFloatState.year, memoFloatState.month0, idx + 1);
          var wd = useJa ? WD_JA[dt.getDay()] : WD_EN[dt.getDay()];
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'memo-float-modal__date-btn';
          if (iso === memoFloatState.focusIso) btn.classList.add('is-active');
          btn.setAttribute('data-iso', iso);
          btn.textContent = memoFloatState.month0 + 1 + '/' + (idx + 1) + ' ' + wd;
          memoFloatDateRail.appendChild(btn);
        });
        if (memoFloatMonthLabel) {
          memoFloatMonthLabel.textContent = monthLabelText(memoFloatState.year, memoFloatState.month0);
        }
        requestAnimationFrame(function () {
          if (!memoFloatDateRail || !memoFloatState.focusIso) return;
          var active = memoFloatDateRail.querySelector('.memo-float-modal__date-btn.is-active');
          if (active && active.scrollIntoView) {
            active.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' });
          }
        });
      }
      function renderMemoFloatDayPanel() {
        if (!memoFloatDayPanel) return;
        var iso = memoFloatState.focusIso;
        var labels = memoFloatLabels();
        var kpi = memoDayKpi(iso);
        memoFloatDayPanel.innerHTML = '';
        function addReadRow(label, value) {
          var row = document.createElement('div');
          row.className = 'memo-float-modal__row';
          var lbl = document.createElement('div');
          lbl.className = 'memo-float-modal__row-label';
          lbl.textContent = label;
          var val = document.createElement('div');
          val.className = 'memo-float-modal__row-value';
          val.textContent = value;
          row.appendChild(lbl);
          row.appendChild(val);
          memoFloatDayPanel.appendChild(row);
        }
        addReadRow(labels.todaySales, fmtMoney(kpi.sales));
        addReadRow(labels.targetSales, fmtMoney(kpi.target));
        (function () {
          var row = document.createElement('div');
          row.className = 'memo-float-modal__row';
          var lbl = document.createElement('div');
          lbl.className = 'memo-float-modal__row-label';
          lbl.textContent = labels.diff;
          var val = document.createElement('div');
          val.className = 'memo-float-modal__row-value';
          ensureTwDiffExports();
          val.textContent =
            typeof window.__twFmtDiff === 'function'
              ? window.__twFmtDiff(kpi.sales, kpi.target)
              : fmtMoney(kpi.diff);
          applyTwDiffSurfaceEl(val, kpi.sales, kpi.target);
          row.appendChild(lbl);
          row.appendChild(val);
          memoFloatDayPanel.appendChild(row);
        })();
        addReadRow(labels.achievement, fmtPct(kpi.rate));
        addReadRow(labels.weather, weatherLabelForIso(iso));
        syncWeeklyMemoItems();
        var fi;
        for (fi = 0; fi < WEEKLY_MEMO_FIXED_COUNT; fi++) {
          appendMemoFloatBlock(memoFloatDayPanel, state.memoItems[fi], fi, iso, false);
        }
        var freeSection = document.createElement('div');
        freeSection.className = 'memo-float-modal__free-memo-section';
        var freeHead = document.createElement('div');
        freeHead.className = 'memo-float-modal__free-memo-head';
        var freeTitle = document.createElement('p');
        freeTitle.className = 'memo-float-modal__free-memo-title';
        freeTitle.textContent = labels.freeMemoSection;
        freeHead.appendChild(freeTitle);
        if (freeMemoCount() === 0) {
          var addOnly = document.createElement('button');
          addOnly.type = 'button';
          addOnly.className = 'memo-float-modal__free-memo-add';
          addOnly.textContent = '+';
          addOnly.setAttribute('aria-label', labels.addFreeMemo);
          addOnly.addEventListener('click', function () {
            memoFloatAddRow(WEEKLY_MEMO_FIXED_COUNT - 1);
          });
          freeHead.appendChild(addOnly);
        }
        freeSection.appendChild(freeHead);
        for (fi = WEEKLY_MEMO_FIXED_COUNT; fi < state.memoItems.length; fi++) {
          appendMemoFloatBlock(freeSection, state.memoItems[fi], fi, iso, true);
        }
        memoFloatDayPanel.appendChild(freeSection);
        if (memoFloatState.focusRowId) {
          var rowToFocus = memoFloatState.focusRowId;
          memoFloatState.focusRowId = null;
          requestAnimationFrame(function () {
            requestAnimationFrame(function () {
              focusMemoFloatMemoRow(rowToFocus);
            });
          });
        }
      }
      function focusMemoFloatMemoRow(rowId) {
        if (!rowId || !memoFloatDayPanel) return;
        var block = memoFloatDayPanel.querySelector('[data-memo-row-id="' + rowId + '"]');
        if (!block) return;
        block.classList.add('memo-float-modal__memo-block--jump-focus');
        if (block.scrollIntoView) {
          block.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
        var ta = block.querySelector('.memo-float-modal__textarea');
        if (ta && !ta.disabled && typeof ta.focus === 'function') {
          ta.focus({ preventScroll: true });
        }
        window.setTimeout(function () {
          block.classList.remove('memo-float-modal__memo-block--jump-focus');
        }, 2200);
      }
      function setMemoFloatFocusIso(iso) {
        if (!iso) return;
        if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {
          flushPendingMemoFloatTextareasFromDom();
        }
        memoFloatState.focusIso = iso;
        memoFloatState.focusRowId = null;
        renderMemoFloatDateRail();
        renderMemoFloatDayPanel();
      }
      function syncMepFromMemoFloatSave() {
        var y = memoFloatState.year;
        var m0 = memoFloatState.month0;
        var iso = memoFloatState.focusIso;
        var monthChanged = y !== mefYear || m0 !== mefMonth0;
        if (monthChanged) {
          var prevYear = mefYear;
          /* Flush current textareas before year/month context swap can reload Store. */
          if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {
            flushPendingMemoFloatTextareasFromDom();
          }
          if (prevYear !== y && Number.isFinite(prevYear)) {
            persistMepToYearStore(prevYear);
          }
          mefYear = y;
          mefMonth0 = m0;
          if (prevYear !== mefYear) onMepYearContextChanged(mefYear);
          persistMefMonth();
        }
        return persistMepToYearStore(mefYear);
      }
      function afterMemoFloatPersistUi(iso, monthChanged) {
        buildGrid();
        if (iso) {
          if (monthChanged) scrollToIsoColumn(iso);
          else {
            var ths = tbl && tbl.querySelectorAll('thead th');
            if (ths && ths.length) {
              var parts = iso.split('-');
              var d = Number(parts[2]) - 1;
              if (d >= 0 && d < ths.length) scroller.scrollLeft = ths[d].offsetLeft * currentScale;
            }
          }
        }
      }
      function saveMemoFloatModal() {
        flushPendingMemoEditsFromDom();
        var y = memoFloatState.year;
        var m0 = memoFloatState.month0;
        var iso = memoFloatState.focusIso;
        var monthChanged = y !== mefYear || m0 !== mefMonth0;
        var ok = syncMepFromMemoFloatSave();
        if (!ok) {
          var lockedMsg = useJa
            ? 'メモを保存できませんでした（年がロックされているか、ストアが未準備です）。'
            : 'Could not save memos (year may be locked, or store is not ready).';
          window.alert(lockedMsg);
          return false;
        }
        afterMemoFloatPersistUi(iso, monthChanged);
        memoFloatState.dirty = false;
        memoFloatState.sessionSaved = true;
        memoFloatUndoStack = [];
        if (memoFloatUndo) memoFloatUndo.disabled = true;
        editSessionCommitted = true;
        confirmedSnapshot = buildConfirmedSnapshot();
        clearDirty();
        return true;
      }
      function hideMemoFloatCloseChooser() {
        if (!memoFloatCloseChooser || memoFloatCloseChooser.hasAttribute('hidden')) return;
        memoFloatCloseChooser.setAttribute('hidden', '');
        var el = memoFloatCloseReturnFocus;
        memoFloatCloseReturnFocus = null;
        if (el && typeof el.focus === 'function') el.focus();
      }
      function finishMemoFloatClose(ok) {
        var fn = memoFloatCloseResolve;
        memoFloatCloseResolve = null;
        hideMemoFloatCloseChooser();
        if (fn) fn(!!ok);
      }
      function requestMemoFloatClose() {
        return new Promise(function (resolve) {
          if (memoFloatState.sessionSaved && !memoFloatState.dirty) {
            resolve(true);
            return;
          }
          if (memoFloatCloseChooser && !memoFloatCloseChooser.hasAttribute('hidden')) {
            resolve(false);
            return;
          }
          memoFloatCloseResolve = resolve;
          memoFloatCloseReturnFocus = document.activeElement;
          if (memoFloatCloseChooser) {
            memoFloatCloseChooser.removeAttribute('hidden');
            if (memoFloatCloseCancel) memoFloatCloseCancel.focus();
          } else resolve(window.confirm(t('未保存のメモがあります。閉じますか？', 'You have unsaved memos. Close anyway?')));
        });
      }
      function closeMemoFloatModal() {
        if (!memoFloatRoot) return;
        memoFloatRoot.setAttribute('hidden', '');
        document.body.style.overflow = '';
      }
      function openMemoModal(iso, rowId) {
        if (!memoFloatRoot) return;
        var parts = String(iso || '').split('-');
        if (parts.length >= 2) {
          memoFloatState.year = Number(parts[0]) || mefYear;
          memoFloatState.month0 = (Number(parts[1]) || 1) - 1;
        } else {
          memoFloatState.year = mefYear;
          memoFloatState.month0 = mefMonth0;
        }
        memoFloatState.focusIso = iso || mepIsoForMemoOpen();
        memoFloatState.focusRowId = rowId || null;
        memoFloatState.dirty = false;
        memoFloatState.sessionSaved = true;
        memoFloatUndoStack = [];
        memoFloatOpenSnapshot = snapshotMemoFloatState();
        if (memoFloatUndo) memoFloatUndo.disabled = true;
        syncWeeklyMemoItems();
        var floatLabels = memoFloatLabels();
        var titleEl = document.getElementById('memo-float-title');
        if (titleEl) titleEl.textContent = floatLabels.windowTitle;
        renderMemoFloatDateRail();
        renderMemoFloatDayPanel();
        memoFloatRoot.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';
        if (!rowId && memoFloatClose) memoFloatClose.focus();
      }
      function openMemoForIso(iso, allowNonBizDay, rowId) {
        if (!iso) return;
        if (!allowNonBizDay && !bizDayByIso[iso]) return;
        openMemoModal(iso, rowId);
      }
      if (memoFloatDateRail) {
        memoFloatDateRail.addEventListener('click', function (ev) {
          var btn = ev.target.closest('.memo-float-modal__date-btn');
          if (!btn) return;
          setMemoFloatFocusIso(btn.getAttribute('data-iso'));
        });
      }
      if (memoFloatPrevMonth) {
        memoFloatPrevMonth.addEventListener('click', function () {
          if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {
            flushPendingMemoFloatTextareasFromDom();
          }
          var d = memoFloatState.focusIso ? isoToDate(memoFloatState.focusIso) : null;
          var day = d ? d.getDate() : 1;
          if (memoFloatState.month0 <= 0) {
            memoFloatState.year -= 1;
            memoFloatState.month0 = 11;
          } else memoFloatState.month0 -= 1;
          var last = new Date(memoFloatState.year, memoFloatState.month0 + 1, 0).getDate();
          memoFloatState.focusIso =
            memoFloatState.year +
            '-' +
            String(memoFloatState.month0 + 1).padStart(2, '0') +
            '-' +
            String(Math.min(day, last)).padStart(2, '0');
          renderMemoFloatDateRail();
          renderMemoFloatDayPanel();
        });
      }
      if (memoFloatNextMonth) {
        memoFloatNextMonth.addEventListener('click', function () {
          if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {
            flushPendingMemoFloatTextareasFromDom();
          }
          var d = memoFloatState.focusIso ? isoToDate(memoFloatState.focusIso) : null;
          var day = d ? d.getDate() : 1;
          if (memoFloatState.month0 >= 11) {
            memoFloatState.year += 1;
            memoFloatState.month0 = 0;
          } else memoFloatState.month0 += 1;
          var last = new Date(memoFloatState.year, memoFloatState.month0 + 1, 0).getDate();
          memoFloatState.focusIso =
            memoFloatState.year +
            '-' +
            String(memoFloatState.month0 + 1).padStart(2, '0') +
            '-' +
            String(Math.min(day, last)).padStart(2, '0');
          renderMemoFloatDateRail();
          renderMemoFloatDayPanel();
        });
      }
      if (memoFloatToday) {
        memoFloatToday.addEventListener('click', function () {
          var now = new Date();
          memoFloatState.year = now.getFullYear();
          memoFloatState.month0 = now.getMonth();
          memoFloatState.focusIso =
            memoFloatState.year +
            '-' +
            String(memoFloatState.month0 + 1).padStart(2, '0') +
            '-' +
            String(now.getDate()).padStart(2, '0');
          renderMemoFloatDateRail();
          renderMemoFloatDayPanel();
        });
      }
      if (memoFloatUndo) {
        memoFloatUndo.addEventListener('click', function () {
          popMemoFloatUndo();
        });
      }
      if (memoFloatSave) {
        memoFloatSave.addEventListener('click', function () {
          saveMemoFloatModal();
        });
      }
      function requestCloseMemoFloatModal() {
        requestMemoFloatClose().then(function (ok) {
          if (!ok) return;
          closeMemoFloatModal();
        });
      }
      if (memoFloatClose) memoFloatClose.addEventListener('click', requestCloseMemoFloatModal);
      if (memoFloatBackdrop) memoFloatBackdrop.addEventListener('click', requestCloseMemoFloatModal);
      if (memoFloatCloseSave) {
        memoFloatCloseSave.addEventListener('click', function () {
          if (!saveMemoFloatModal()) return;
          finishMemoFloatClose(true);
          closeMemoFloatModal();
        });
      }
      if (memoFloatCloseDiscard) {
        memoFloatCloseDiscard.addEventListener('click', function () {
          if (memoFloatOpenSnapshot) restoreMemoFloatState(memoFloatOpenSnapshot);
          memoFloatState.dirty = false;
          memoFloatState.sessionSaved = true;
          memoFloatUndoStack = [];
          if (memoFloatUndo) memoFloatUndo.disabled = true;
          buildGrid();
          finishMemoFloatClose(true);
          closeMemoFloatModal();
        });
      }
      if (memoFloatCloseCancel) {
        memoFloatCloseCancel.addEventListener('click', function () {
          finishMemoFloatClose(false);
        });
      }
      if (memoFloatCloseChooserScrim) {
        memoFloatCloseChooserScrim.addEventListener('click', function () {
          finishMemoFloatClose(false);
        });
      }
      document.addEventListener('keydown', function (ev) {
        if (!memoFloatRoot || memoFloatRoot.hasAttribute('hidden')) return;
        if (ev.key === 'Escape') {
          ev.preventDefault();
          requestCloseMemoFloatModal();
        }
      });
      document.addEventListener('mep:memoOpenRequested', function (ev) {
        var d = ev && ev.detail;
        if (!d || !d.iso) return;
        openMemoModal(d.iso);
      });
