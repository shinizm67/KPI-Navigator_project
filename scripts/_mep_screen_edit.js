      function isMepDailySalesPathBlocked() {
        return !!(
          window.KpiYearStore &&
          typeof KpiYearStore.getDailySalesInputPath === 'function' &&
          KpiYearStore.getDailySalesInputPath() !== 'mep'
        );
      }
      function isMepDailySalesEditBlocked() {
        if (isMepDailySalesPathBlocked()) return true;
        return !!(
          window.KpiYearStore &&
          typeof KpiYearStore.holdsEditLease === 'function' &&
          !KpiYearStore.holdsEditLease('daily-sales')
        );
      }
      function isMepScreenEditBlocked() {
        return isMepDailySalesEditBlocked();
      }
      function mepPathSwitchHint() {
        return t(
          '閲覧モードです。編集するには「編集」を押してください。',
          'View mode. Press Edit to make changes.',
          '檢視模式。若要編輯，請按下「編輯」。'
        );
      }
      function syncMepScreenEditToolbar() {
        var blocked = isMepScreenEditBlocked();
        var hint = mepPathSwitchHint();
        if (typeof syncUndoButton === 'function') syncUndoButton();
        if (btnConfirm) {
          btnConfirm.disabled = blocked;
          if (blocked) btnConfirm.setAttribute('title', hint);
          else btnConfirm.removeAttribute('title');
        }
        if (btnExpenseCsvUpload) {
          if (!btnExpenseCsvUpload.getAttribute('data-kpi-edit-title-saved')) {
            btnExpenseCsvUpload.setAttribute(
              'data-kpi-edit-title-saved',
              btnExpenseCsvUpload.getAttribute('title') || ''
            );
            btnExpenseCsvUpload.setAttribute(
              'data-kpi-edit-tooltip-saved',
              btnExpenseCsvUpload.getAttribute('data-tooltip') || ''
            );
          }
          btnExpenseCsvUpload.disabled = blocked;
          if (blocked) {
            btnExpenseCsvUpload.setAttribute('title', hint);
            btnExpenseCsvUpload.setAttribute('data-tooltip', hint);
          } else {
            btnExpenseCsvUpload.setAttribute(
              'title',
              btnExpenseCsvUpload.getAttribute('data-kpi-edit-title-saved') || ''
            );
            btnExpenseCsvUpload.setAttribute(
              'data-tooltip',
              btnExpenseCsvUpload.getAttribute('data-kpi-edit-tooltip-saved') || ''
            );
          }
        }
        if (typeof syncCsvUploadTooltip === 'function') {
          syncCsvUploadTooltip();
        } else if (btnCsvUpload) {
          btnCsvUpload.disabled = blocked;
          if (blocked) {
            btnCsvUpload.setAttribute('title', hint);
            btnCsvUpload.setAttribute('data-tooltip', hint);
          }
        }
        if (strategyNoteInput) {
          strategyNoteInput.readOnly = blocked;
          strategyNoteInput.disabled = blocked;
        }
        var memoSave = document.getElementById('memo-float-save');
        if (memoSave) {
          memoSave.disabled = blocked;
          if (blocked) memoSave.setAttribute('title', hint);
          else memoSave.removeAttribute('title');
        }
        var memoUndo = document.getElementById('memo-float-undo');
        if (memoUndo && blocked) memoUndo.disabled = true;
        var memoCloseSave = document.getElementById('memo-float-close-save');
        if (memoCloseSave) memoCloseSave.disabled = blocked;
      }
