      /* MEP-STRATEGY-NOTE-MODAL */
      var strategyUserNotesByMonth = {};
      var strategyNoteModal = document.getElementById('strategy-note-modal');
      var strategyNoteInput = document.getElementById('monthly-edit-strategy-user-note');
      var strategyNoteCounter = document.getElementById('monthly-edit-strategy-char-count');
      var strategyNoteMonthLabel = document.getElementById('strategy-note-month-label');
      var strategyNoteOpenBtn = document.getElementById('monthly-edit-float-strategy-note');
      var STRATEGY_NOTE_HARD = 200;

      function strategyNoteTierClass(tier) {
        if (tier === 150) return 'strategy-note-modal__char-count--warn-150';
        if (tier === 120) return 'strategy-note-modal__char-count--warn-120';
        return '';
      }

      function syncStrategyCharCounter() {
        if (!strategyNoteInput || !strategyNoteCounter) return;
        var len = String(strategyNoteInput.value || '').length;
        var activeTier = 0;
        if (len > 150) activeTier = 150;
        else if (len > 120) activeTier = 120;
        strategyNoteCounter.textContent = len + ' / ' + STRATEGY_NOTE_HARD;
        strategyNoteCounter.classList.remove(
          strategyNoteTierClass(120),
          strategyNoteTierClass(150)
        );
        if (activeTier) strategyNoteCounter.classList.add(strategyNoteTierClass(activeTier));
      }

      function flushStrategyNoteToCache() {
        if (!strategyNoteInput) return;
        strategyUserNotesByMonth[String(mefMonth0)] = String(strategyNoteInput.value || '').slice(
          0,
          STRATEGY_NOTE_HARD
        );
      }

      function formatStrategyNoteMonthLabel() {
        var monthsJa = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
        var monthsEn = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var months = useJa ? monthsJa : monthsEn;
        return mefYear + ' / ' + (months[mefMonth0] || String(mefMonth0 + 1));
      }

      function loadStrategyNoteFromCache() {
        if (!strategyNoteInput) return;
        strategyNoteInput.value = String(strategyUserNotesByMonth[String(mefMonth0)] || '');
        syncStrategyCharCounter();
        if (strategyNoteMonthLabel) strategyNoteMonthLabel.textContent = formatStrategyNoteMonthLabel();
      }

      function mergeStrategyNotesFromPayload(payload) {
        strategyUserNotesByMonth = {};
        var src = payload && payload.monthlyStrategyUserNotes;
        if (!src || typeof src !== 'object') {
          loadStrategyNoteFromCache();
          return;
        }
        Object.keys(src).forEach(function (mKey) {
          strategyUserNotesByMonth[String(mKey)] = String(src[mKey] == null ? '' : src[mKey]).slice(
            0,
            STRATEGY_NOTE_HARD
          );
        });
        loadStrategyNoteFromCache();
      }

      function strategyNotesForPersist() {
        flushStrategyNoteToCache();
        var out = {};
        Object.keys(strategyUserNotesByMonth).forEach(function (mKey) {
          var text = String(strategyUserNotesByMonth[mKey] || '').trim();
          if (text) out[mKey] = text.slice(0, STRATEGY_NOTE_HARD);
        });
        return out;
      }

      function openStrategyNoteModal() {
        if (!strategyNoteModal) return;
        loadStrategyNoteFromCache();
        strategyNoteModal.removeAttribute('hidden');
      }

      function closeStrategyNoteModal() {
        if (!strategyNoteModal) return;
        flushStrategyNoteToCache();
        strategyNoteModal.setAttribute('hidden', '');
      }

      if (strategyNoteInput) {
        strategyNoteInput.addEventListener('input', function () {
          syncStrategyCharCounter();
          markDirty();
        });
      }
      if (strategyNoteOpenBtn) {
        strategyNoteOpenBtn.addEventListener('click', function () {
          openStrategyNoteModal();
        });
      }
      document.getElementById('strategy-note-close') &&
        document.getElementById('strategy-note-close').addEventListener('click', closeStrategyNoteModal);
      document.getElementById('strategy-note-backdrop') &&
        document.getElementById('strategy-note-backdrop').addEventListener('click', closeStrategyNoteModal);

      function maybeOpenStrategyNoteFromQuery() {
        try {
          var params = new URLSearchParams(window.location.search);
          var flag = String(params.get('openStrategyNote') || params.get('strategyNote') || '').toLowerCase();
          if (flag !== '1' && flag !== 'true' && flag !== 'yes') return;
          openStrategyNoteModal();
          if (history.replaceState) {
            params.delete('openStrategyNote');
            params.delete('strategyNote');
            var q = params.toString();
            history.replaceState(
              null,
              '',
              window.location.pathname + (q ? '?' + q : '') + window.location.hash
            );
          }
        } catch (_e) {}
      }
      /* initEditPage() runs later in the same IIFE; defer so year/month + notes are ready. */
      setTimeout(maybeOpenStrategyNoteFromQuery, 0);
