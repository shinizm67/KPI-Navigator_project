"""MEP Phase 4 — hydrate / flush dailyExpenses + dailyMeta via KpiYearStore."""

from __future__ import annotations

KPI_MEP_STORE_MARKER = "/* KPI-MEP-STORE */"


def mep_store_client_js() -> str:
    return f"""      {KPI_MEP_STORE_MARKER}
      function mepStoreReady() {{
        return !!(
          window.KpiYearStore &&
          typeof KpiYearStore.loadMepYearPayload === 'function' &&
          typeof KpiYearStore.bulkPersistMepYear === 'function'
        );
      }}
      function mepIsoYear(iso) {{
        if (!iso || iso.length < 4) return NaN;
        var y = Number(iso.slice(0, 4));
        return Number.isFinite(y) ? y : NaN;
      }}
      function mepFilterIsoMap(byIso, year) {{
        var out = {{}};
        var y = Number(year);
        Object.keys(byIso || {{}}).forEach(function (iso) {{
          if (mepIsoYear(iso) === y) out[iso] = byIso[iso];
        }});
        return out;
      }}
      function restoreMemoRowsFromSnapshot(rows) {{
        if (!rows || !rows.length) return;
        state.memoItems = rows.map(function (s) {{
          return {{
            id: s.id,
            kind: 'memo',
            labelJa: s.labelJa,
            labelEn: s.labelEn,
            editableLabel: !!s.editableLabel,
            deletable: !!s.deletable,
            weeklyFixed: !!s.weeklyFixed,
            sub: !!s.sub,
          }};
        }});
        var maxId = nextRowId;
        state.memoItems.forEach(function (r) {{
          var m = String(r.id).match(/^r(\\d+)$/);
          if (m) maxId = Math.max(maxId, Number(m[1]) + 1);
        }});
        nextRowId = maxId;
      }}
      function mergeMepYearPayload(payload) {{
        if (!payload) return;
        Object.keys(payload.dailyExpenses || {{}}).forEach(function (rowId) {{
          if (!rowValueById[rowId]) rowValueById[rowId] = {{}};
          Object.assign(rowValueById[rowId], payload.dailyExpenses[rowId]);
        }});
        var meta = payload.dailyMeta || {{}};
        /* KPI-MEP-MEMO-MERGE: do not wipe non-empty local memo with empty store string
           (CreateYear seed / partial payload used to erase typed Daily Notes). */
        Object.keys(meta.memos || {{}}).forEach(function (rowId) {{
          if (!memoValueById[rowId]) memoValueById[rowId] = {{}};
          var dest = memoValueById[rowId];
          var src = meta.memos[rowId] || {{}};
          Object.keys(src).forEach(function (iso) {{
            var incoming = String(src[iso] == null ? '' : src[iso]);
            var current = dest[iso];
            if (String(current || '').trim() && !String(incoming || '').trim()) return;
            dest[iso] = incoming;
          }});
        }});
        Object.assign(weatherByIso, meta.weather || {{}});
        if (payload.mepMemoRows && payload.mepMemoRows.length) {{
          restoreMemoRowsFromSnapshot(payload.mepMemoRows);
        }}
        syncWeeklyMemoItems();
      }}
      function loadMepFromYearStore(year) {{
        if (!mepStoreReady()) return;
        /* Capture open Daily Notes DOM before Store merge can race with re-render. */
        if (typeof flushPendingMemoFloatTextareasFromDom === 'function') {{
          flushPendingMemoFloatTextareasFromDom();
        }}
        mergeMepYearPayload(KpiYearStore.loadMepYearPayload(year));
      }}
      function flushPendingMemoInputsFromDom() {{
        if (!root) return;
        root.querySelectorAll('[data-action="memo-input"]').forEach(function (inp) {{
          var rowId = inp.getAttribute('data-row-id');
          var iso = inp.getAttribute('data-iso');
          if (!rowId || !iso) return;
          writeMemo(rowId, iso, inp.value);
        }});
      }}
      function flushPendingMemoFloatTextareasFromDom() {{
        if (typeof memoFloatRoot === 'undefined' || !memoFloatRoot || memoFloatRoot.hasAttribute('hidden')) {{
          return;
        }}
        memoFloatRoot.querySelectorAll('.memo-float-modal__textarea[data-row-id]').forEach(function (ta) {{
          var rowId = ta.getAttribute('data-row-id');
          var iso = ta.getAttribute('data-iso');
          if (!rowId || !iso) return;
          writeMemo(rowId, iso, ta.value);
        }});
      }}
      function flushPendingMemoEditsFromDom() {{
        flushPendingMemoFloatTextareasFromDom();
        flushPendingMemoInputsFromDom();
      }}
      function buildMepPersistPayload(year) {{
        var y = Number(year);
        var dailyExpenses = {{}};
        Object.keys(rowValueById || {{}}).forEach(function (rowId) {{
          var filtered = mepFilterIsoMap(rowValueById[rowId], y);
          if (Object.keys(filtered).length) dailyExpenses[rowId] = filtered;
        }});
        var memos = {{}};
        Object.keys(memoValueById || {{}}).forEach(function (rowId) {{
          var filtered = mepFilterIsoMap(memoValueById[rowId], y);
          if (Object.keys(filtered).length) memos[rowId] = filtered;
        }});
        var weather = mepFilterIsoMap(weatherByIso, y);
        var flags = {{}};
        Object.keys(memos).forEach(function (rowId) {{
          Object.keys(memos[rowId]).forEach(function (iso) {{
            if (String(memos[rowId][iso] || '').trim()) flags[iso] = true;
            else flags[iso] = false;
          }});
        }});
        return {{
          dailyExpenses: dailyExpenses,
          dailyMeta: {{ memos: memos, weather: weather, flags: flags }},
          mepMemoRows: rowSnapshot(state.memoItems),
        }};
      }}
      function persistMepToYearStore(year) {{
        if (!mepStoreReady()) return false;
        flushPendingMemoEditsFromDom();
        if (!KpiYearStore.canWriteMepYear(year)) return false;
        return KpiYearStore.bulkPersistMepYear(year, buildMepPersistPayload(year), {{
          source: 'monthly-edit-float',
        }});
      }}
      function onMepYearContextChanged(year) {{
        createInitialRowsIfNeeded();
        loadMepFromYearStore(year);
        if (typeof syncMonthlySalesFromAnnualStoreForMonth === 'function') {{
          syncMonthlySalesFromAnnualStoreForMonth();
        }}
        if (typeof syncBizDayFromAnnualStoreForMonth === 'function') {{
          syncBizDayFromAnnualStoreForMonth();
        }}
      }}
      document.addEventListener('kpi:mepDataChanged', function (ev) {{
        if (root.hidden) return;
        var src = ev && ev.detail && ev.detail.source;
        if (src === 'monthly-edit-float') return;
        var y = ev && ev.detail && Number(ev.detail.year);
        if (!Number.isFinite(y) || y !== mefYear) return;
        loadMepFromYearStore(y);
        buildGrid();
      }});
"""
