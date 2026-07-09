      /* MEP-MEMO-DRILLDOWN */
      function formatMemoCellPreview(text) {
        var s = String(text || '').trim();
        if (!s) return '—';
        var max = useJa ? 8 : 12;
        if (s.length <= max) return s;
        return s.slice(0, max) + '…';
      }
      function syncMemoPreviewTdFill(btn) {
        var td = btn && btn.closest ? btn.closest('td') : null;
        if (!td || !btn) return;
        var raw = btn.getAttribute('data-memo-full') || '';
        setKpiFill(td, String(raw).trim() === '' ? 'empty' : 'has');
      }
      function openMemoForRow(iso, rowId, allowNonBizDay) {
        if (!iso || !rowId) return;
        if (typeof openMemoForIso === 'function') {
          openMemoForIso(iso, !!allowNonBizDay, rowId);
        }
      }
