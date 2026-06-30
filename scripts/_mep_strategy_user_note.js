      /* MEP-STRATEGY-USER-NOTE */
      var strategyUserNotesByMonth = {};
      var strategyNoteInput = document.getElementById('monthly-edit-strategy-user-note');
      var strategyNoteCounter = document.getElementById('monthly-edit-strategy-char-count');
      var STRATEGY_NOTE_HARD = 200;

      function strategyNoteTierClass(tier) {
        if (tier === 150) return 'monthly-edit-float__strategy-char-count--warn-150';
        if (tier === 120) return 'monthly-edit-float__strategy-char-count--warn-120';
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
        strategyUserNotesByMonth[String(mefMonth0)] = String(strategyNoteInput.value || '').slice(0, STRATEGY_NOTE_HARD);
      }

      function loadStrategyNoteFromCache() {
        if (!strategyNoteInput) return;
        strategyNoteInput.value = String(strategyUserNotesByMonth[String(mefMonth0)] || '');
        syncStrategyCharCounter();
      }

      function mergeStrategyNotesFromPayload(payload) {
        strategyUserNotesByMonth = {};
        var src = payload && payload.monthlyStrategyUserNotes;
        if (!src || typeof src !== 'object') return;
        Object.keys(src).forEach(function (mKey) {
          strategyUserNotesByMonth[String(mKey)] = String(src[mKey] == null ? '' : src[mKey]).slice(0, STRATEGY_NOTE_HARD);
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

      function onMepStrategyMonthContextChanged() {
        loadStrategyNoteFromCache();
      }

      if (strategyNoteInput) {
        strategyNoteInput.addEventListener('input', function () {
          syncStrategyCharCounter();
          markDirty();
        });
      }
