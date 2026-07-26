      /* MEP-WEEKLY-MEMO-ROWS */
      var WEEKLY_MEMO_ROW_DEFS = [
        { labelJa: '店舗イベント', labelEn: 'Store Event' },
        { labelJa: 'エリアイベント', labelEn: 'Area Event' },
        { labelJa: 'SNS', labelEn: 'Social Media' },
        { labelJa: 'マーケ', labelEn: 'Marketing' },
        { labelJa: 'プロモ', labelEn: 'Promo Conversion' },
        { labelJa: '予約', labelEn: 'Reservation' }
      ];
      var WEEKLY_MEMO_FIXED_COUNT = WEEKLY_MEMO_ROW_DEFS.length;
      function isAutoMemoLabelJa(label) {
        return /^メモ\d*$/.test(String(label || '').trim());
      }
      function isAutoMemoLabelEn(label) {
        return /^Memo(\s\d+)?$/.test(String(label || '').trim());
      }
      function isWeeklyFixedMemoIndex(idx) {
        return idx < WEEKLY_MEMO_FIXED_COUNT;
      }
      function isWeeklyFixedMemoRow(row, idx) {
        if (row && row.weeklyFixed) return true;
        return typeof idx === 'number' && isWeeklyFixedMemoIndex(idx);
      }
      function applyWeeklyFixedRowMeta(row, def) {
        row.labelJa = def.labelJa;
        row.labelEn = def.labelEn;
        row.editableLabel = false;
        row.deletable = false;
        row.weeklyFixed = true;
        row.kind = 'memo';
      }
      function syncWeeklyMemoItems() {
        if (!state.memoItems) state.memoItems = [];
        for (var i = 0; i < WEEKLY_MEMO_FIXED_COUNT; i++) {
          var def = WEEKLY_MEMO_ROW_DEFS[i];
          if (!state.memoItems[i]) {
            state.memoItems.splice(
              i,
              0,
              makeRow('memo', def.labelJa, def.labelEn, {
                editableLabel: false,
                deletable: false,
                weeklyFixed: true
              })
            );
          } else {
            applyWeeklyFixedRowMeta(state.memoItems[i], def);
          }
        }
      }
      function freeMemoCount() {
        syncWeeklyMemoItems();
        return Math.max(0, state.memoItems.length - WEEKLY_MEMO_FIXED_COUNT);
      }
      function renumberFreeMemoItems() {
        for (var i = WEEKLY_MEMO_FIXED_COUNT; i < state.memoItems.length; i++) {
          var row = state.memoItems[i];
          var n = i - WEEKLY_MEMO_FIXED_COUNT + 1;
          if (isAutoMemoLabelJa(row.labelJa)) row.labelJa = n === 1 ? 'メモ' : 'メモ' + n;
          if (isAutoMemoLabelEn(row.labelEn)) row.labelEn = n === 1 ? 'Memo' : 'Memo ' + n;
        }
      }
      function addFreeMemoRow(afterAbsIdx) {
        syncWeeklyMemoItems();
        var insertAt =
          typeof afterAbsIdx === 'number' ? afterAbsIdx + 1 : state.memoItems.length;
        if (insertAt < WEEKLY_MEMO_FIXED_COUNT) insertAt = WEEKLY_MEMO_FIXED_COUNT;
        if (insertAt > state.memoItems.length) insertAt = state.memoItems.length;
        state.memoItems.splice(
          insertAt,
          0,
          makeRow('memo', 'メモ', 'Memo', { editableLabel: true, deletable: true })
        );
        renumberFreeMemoItems();
      }
      function removeFreeMemoRowAt(absIdx) {
        if (isWeeklyFixedMemoIndex(absIdx)) return false;
        if (absIdx < 0 || absIdx >= state.memoItems.length) return false;
        var removed = state.memoItems.splice(absIdx, 1)[0];
        if (removed && removed.id) delete memoValueById[removed.id];
        renumberFreeMemoItems();
        return true;
      }
