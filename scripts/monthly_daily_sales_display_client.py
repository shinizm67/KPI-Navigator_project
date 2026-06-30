"""Monthly Table Window: show $0/¥0 when daily sales are unset (not demo placeholder)."""

MONTHLY_RESOLVE_DAILY_SALES_OLD = """      function resolveDailySalesText(iso) {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var tmap = daily && daily.targetSalesByDate;
        var n = tmap && Object.prototype.hasOwnProperty.call(tmap, iso) ? Number(tmap[iso]) : NaN;
        if (!Number.isFinite(n)) return demoMoney;
        var rounded = Math.round(n);
        if (useJa) return '\\u00a5' + rounded.toLocaleString('ja-JP');
        return '$' + rounded.toLocaleString('en-US');
      }"""

MONTHLY_RESOLVE_DAILY_SALES_NEW = """      function resolveDailySalesText(iso) {
        var daily = window.__ANNUAL_DATA && window.__ANNUAL_DATA.daily;
        var tmap = daily && daily.targetSalesByDate;
        var n = tmap && Object.prototype.hasOwnProperty.call(tmap, iso) ? Number(tmap[iso]) : NaN;
        if (!Number.isFinite(n) || n === 1234) return useJa ? '\\u00a50' : '$0';
        var rounded = Math.round(n);
        if (useJa) return '\\u00a5' + rounded.toLocaleString('ja-JP');
        return '$' + rounded.toLocaleString('en-US');
      }"""
