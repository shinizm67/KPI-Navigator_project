/**
 * Optional server profile sync after local profile save.
 * Keeps localStorage UX; best-effort PUT /api/v1/profile.php.
 */
(function (global) {
  'use strict';

  function resolveProfileApi() {
    if (global.__KPI_AUTH && typeof global.__KPI_AUTH.resolveAuthBase === 'function') {
      try {
        return global.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '') + '/profile.php';
      } catch (e) {}
    }
    return '/kpi-navigator/api/v1/profile.php';
  }

  function saveServerProfile(data) {
    var payload = {
      businessName: data && data.businessName != null ? data.businessName : '',
      companyName: data && (data.company != null ? data.company : data.companyName),
      businessType: data && (data.businessType != null ? data.businessType : data.industry),
      genre: data && data.genre != null ? data.genre : '',
      locale: data && data.locale != null ? data.locale : (document.documentElement.getAttribute('lang') || ''),
      country: data && data.country != null ? data.country : '',
      stateRegion: data && (data.state != null ? data.state : data.stateRegion),
      city: data && data.city != null ? data.city : '',
      currency: data && data.currency != null ? data.currency : '',
    };
    return fetch(resolveProfileApi(), {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function (r) {
      return r.json().catch(function () { return { ok: false }; });
    }).catch(function () {
      return { ok: false };
    });
  }

  global.__KPI_PROFILE_SERVER = {
    saveServerProfile: saveServerProfile,
  };
})(typeof window !== 'undefined' ? window : this);
