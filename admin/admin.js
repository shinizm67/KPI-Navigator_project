(function () {
  'use strict';

  function apiBase() {
    if (window.__KPI_AUTH && typeof window.__KPI_AUTH.resolveAuthBase === 'function') {
      try {
        return window.__KPI_AUTH.resolveAuthBase().replace(/\/?$/, '');
      } catch (e) {}
    }
    var path = window.location.pathname || '';
    var idx = path.indexOf('/admin/');
    if (idx >= 0) {
      return path.slice(0, idx) + '/api/v1';
    }
    return '/kpi-navigator/api/v1';
  }

  function adminRoot() {
    var path = window.location.pathname || '';
    var idx = path.indexOf('/admin/');
    if (idx >= 0) {
      return path.slice(0, idx + '/admin'.length);
    }
    return '/kpi-navigator/admin';
  }

  function dash(v) {
    if (v === null || v === undefined || v === '') return 'N/A';
    return String(v);
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function fetchJson(url, opts) {
    var options = opts || {};
    var init = {
      credentials: 'include',
      cache: 'no-store',
      method: options.method || 'GET',
      headers: options.headers || {}
    };
    if (options.body !== undefined) {
      init.headers['Content-Type'] = 'application/json';
      init.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
    }
    return fetch(url, init).then(function (r) {
      return r.json().then(function (j) {
        return { status: r.status, data: j };
      }).catch(function () {
        return { status: r.status, data: null };
      });
    });
  }

  function showError(el, msg) {
    if (!el) return;
    el.hidden = false;
    el.textContent = msg;
  }

  function clearError(el) {
    if (!el) return;
    el.hidden = true;
    el.textContent = '';
  }

  function authFailMsg(res) {
    if (res.status === 401) return '401 unauthorized — sign in as Founder Super Admin.';
    if (res.status === 403) return '403 forbidden — Founder Super Admin required.';
    if (res.data && res.data.error) return 'Failed: ' + res.data.error;
    return '';
  }

  function jstDateTime(iso) {
    if (!iso) return 'N/A';
    var t = Date.parse(iso);
    if (isNaN(t)) return 'N/A';
    var d = new Date(t + 9 * 3600 * 1000);
    function p(n) { return (n < 10 ? '0' : '') + n; }
    return d.getUTCFullYear() + '-' + p(d.getUTCMonth() + 1) + '-' + p(d.getUTCDate()) + ' ' +
      p(d.getUTCHours()) + ':' + p(d.getUTCMinutes()) + ' JST';
  }

  function originHtml(origin) {
    if (origin === 'new') return 'NEW';
    if (origin === 'returned') return '<span class="tag-returned">RETURNED</span>';
    if (origin === 'legacy') return 'NEW <span class="muted" title="Created before lifecycle tracking">(pre-tracking)</span>';
    return '<span class="muted">UNKNOWN</span>';
  }

  function postExclusion(body) {
    return fetchJson(apiBase() + '/admin/set-metrics-exclusion.php', { method: 'POST', body: body });
  }

  function card(label, value, sub) {
    return '<div class="card"><div class="label">' + label + '</div><div class="value">' + value + '</div>' +
      (sub ? '<div class="card-sub">' + sub + '</div>' : '') + '</div>';
  }

  /* Catalog labels for Founder display only. Stored codes / API values are never rewritten. */
  var COUNTRY_EN = {
    JP: 'Japan', US: 'United States', GB: 'United Kingdom', CA: 'Canada', AU: 'Australia',
    NZ: 'New Zealand', IE: 'Ireland', SG: 'Singapore', TW: 'Taiwan', HK: 'Hong Kong',
    KR: 'South Korea', CN: 'China', DE: 'Germany', FR: 'France', IT: 'Italy', ES: 'Spain',
    NL: 'Netherlands', BE: 'Belgium', CH: 'Switzerland', AT: 'Austria', SE: 'Sweden',
    NO: 'Norway', DK: 'Denmark', FI: 'Finland', PT: 'Portugal',
    AE: 'United Arab Emirates', IN: 'India', ZA: 'South Africa'
  };
  var BTYPE_EN = {
    restaurant: 'Restaurant', retail: 'Retail', hair_salon: 'Hair salon',
    fitness: 'Fitness', hotel: 'Hotel', other: 'Other'
  };
  var CURRENCY_EN = {
    JPY: 'Japanese Yen', USD: 'US Dollar', GBP: 'British Pound', CAD: 'Canadian Dollar',
    AUD: 'Australian Dollar', NZD: 'New Zealand Dollar', EUR: 'Euro', SGD: 'Singapore Dollar',
    TWD: 'New Taiwan Dollar', HKD: 'Hong Kong Dollar', KRW: 'South Korean Won', CNY: 'Chinese Yuan',
    CHF: 'Swiss Franc', SEK: 'Swedish Krona', NOK: 'Norwegian Krone', DKK: 'Danish Krone',
    AED: 'UAE Dirham', INR: 'Indian Rupee', ZAR: 'South African Rand'
  };

  function catalogMap(dim) {
    if (dim === 'country') return COUNTRY_EN;
    if (dim === 'currency') return CURRENCY_EN;
    return BTYPE_EN;
  }

  function segmentBucketLabel(code) {
    if (code == null || String(code).trim() === '' || code === 'unknown') {
      return '<span class="seg-unknown">Unknown</span>';
    }
    if (code === 'other') {
      return '<span class="seg-other">Other</span>';
    }
    return null;
  }

  function segmentLabelHtml(dim, code) {
    var special = segmentBucketLabel(code);
    if (special) return special;
    var map = catalogMap(dim);
    if (map[code]) return esc(map[code]);
    return '<span class="seg-other">Other</span> <span class="muted">(' + esc(code) + ')</span>';
  }

  function historySegmentHtml(dim, raw) {
    if (raw == null || String(raw).trim() === '') {
      return '<span class="seg-unknown" title="No value stored (pre-M2 history or unavailable)">Unknown</span>';
    }
    var code = String(raw).trim();
    var special = segmentBucketLabel(code);
    if (special && code === 'unknown') return special;
    var map = catalogMap(dim);
    if (map[code] && code !== 'other') return esc(map[code]);
    if (code === 'other') return '<span class="seg-other" title="Canonical other">Other</span>';
    return '<span class="seg-other" title="Value outside the current catalog">Other</span> <span class="muted">(' + esc(code) + ')</span>';
  }

  function segmentTable(dim, title, rows, split) {
    var head = split
      ? '<th>Segment</th><th>Deleted</th><th>Churned</th><th>Early Churn</th>'
      : '<th>Segment</th><th>Deleted</th>';
    var body = (rows && rows.length)
      ? rows.map(function (b) {
          return '<tr><td>' + segmentLabelHtml(dim, b.code) + '</td><td>' + esc(dash(b.deleted)) + '</td>' +
            (split ? '<td>' + esc(dash(b.churned)) + '</td><td>' + esc(dash(b.earlyChurn)) + '</td>' : '') + '</tr>';
        }).join('')
      : '<tr><td colspan="' + (split ? 4 : 2) + '" class="muted">None</td></tr>';
    return '<div class="seg-block"><h3>' + title + '</h3><table class="seg-table"><thead><tr>' + head +
      '</tr></thead><tbody>' + body + '</tbody></table></div>';
  }

  function paintSegments(seg) {
    var section = document.getElementById('lifecycle-segments-section');
    var root = document.getElementById('lifecycle-segments-root');
    var note = document.getElementById('lifecycle-segments-note');
    if (!section || !root) return;
    section.hidden = false;
    if (!seg) {
      root.innerHTML = '<p class="muted">Segment history unavailable.</p>';
      if (note) note.textContent = '';
      return;
    }
    var mo = (seg.scopes && seg.scopes.month) || {};
    var rt = (seg.scopes && seg.scopes.retained) || {};
    var mt = mo.total || {};
    var rtTotal = (rt.total && rt.total.deleted) || 0;
    if (note) {
      var sk = seg.skipped || {};
      note.textContent =
        'Counts of deleted standalone accounts, separate from Monthly Churn above. This month is JST ' +
        dash(seg.month) + ' (' + dash(mt.deleted) + ' deleted). Retained history is the last 3 years (' +
        dash(rtTotal) + ' deleted). Skipped: ' + dash(sk.excluded) + ' excluded, ' + dash(sk.child) + ' child.';
    }
    root.innerHTML =
      '<h3 class="seg-scope-title">This month (JST ' + esc(dash(seg.month)) + ')</h3>' +
      '<div class="seg-grid">' +
        segmentTable('country', 'Country', mo.country, true) +
        segmentTable('businessType', 'Business Type', mo.businessType, true) +
        segmentTable('currency', 'Currency', mo.currency, true) +
      '</div>' +
      '<h3 class="seg-scope-title">Retained history (last 3 years)</h3>' +
      '<div class="seg-grid">' +
        segmentTable('country', 'Country', rt.country, false) +
        segmentTable('businessType', 'Business Type', rt.businessType, false) +
        segmentTable('currency', 'Currency', rt.currency, false) +
      '</div>';
  }

  function paintLifecycle(lc, months) {
    var section = document.getElementById('lifecycle-section');
    var cards = document.getElementById('lifecycle-cards');
    var aux = document.getElementById('lifecycle-aux');
    var note = document.getElementById('lifecycle-note');
    var sel = document.getElementById('lifecycle-month');
    if (!section || !cards) return;
    section.hidden = false;
    if (sel && months && sel.options.length !== months.length) {
      sel.innerHTML = months.map(function (m) {
        return '<option value="' + esc(m) + '">' + esc(m) + '</option>';
      }).join('');
    }
    if (!lc) {
      cards.innerHTML = '<div class="card"><div class="label">Lifecycle</div><div class="value">N/A</div>' +
        '<div class="card-sub">History storage unavailable.</div></div>';
      if (aux) aux.innerHTML = '';
      if (note) note.textContent = '';
      paintSegments(null);
      return;
    }
    if (sel) sel.value = lc.month;
    var c = lc.churn || {};
    var rate = c.ratePercent === null || c.ratePercent === undefined ? 'N/A' : (Number(c.ratePercent).toFixed(2) + '%');
    var nb = lc.newBreakdown || {};
    cards.innerHTML = [
      card('Active', dash(lc.active), 'Now · incl. disabled'),
      card('New', dash(lc.newAccounts), 'NEW ' + dash(nb['new']) + ' · RETURNED ' + dash(nb.returned) + ' · UNKNOWN ' + dash(nb.other)),
      card('Deleted', dash(lc.deleted), 'incl. Early Churn'),
      card('Monthly Churn', rate, dash(c.numerator) + ' / ' + dash(c.denominator) + ' at month start'),
      card('Returned', dash(lc.returned), 'Created this month as RETURNED')
    ].join('');
    if (aux) {
      aux.innerHTML = [
        card('Early Churn', dash(lc.earlyChurn), 'Created & deleted this month'),
        card('Child Deletions', dash(lc.childDeletions), 'Not in churn'),
        card('Disabled', dash(lc.disabled), 'Now · in denominator')
      ].join('');
    }
    if (note) {
      var ex = lc.excluded || {};
      note.textContent =
        'Standalone customer accounts only (role user, no parent). JST month ' + lc.month +
        (lc.monthToDate ? ' (month to date)' : '') + '. ' +
        'Monthly Churn = accounts deleted this month that existed at month start ÷ accounts at month start. ' +
        'Excluded from metrics: ' + dash(ex.accounts) + ' account(s), ' + dash(ex.historyRows) + ' history row(s).' +
        (lc.beforeRetentionWindow ? ' This month starts before the 3-year history window; deletions may be undercounted.' : '');
    }
  }

  function renderDashboard(month) {
    var err = document.getElementById('admin-error');
    var grid = document.getElementById('dash-cards');
    if (!grid) return;
    var sel = document.getElementById('lifecycle-month');
    if (sel && !sel.getAttribute('data-bound')) {
      sel.setAttribute('data-bound', '1');
      sel.addEventListener('change', function () {
        renderDashboard(sel.value);
      });
    }
    var url = apiBase() + '/admin/dashboard.php' + (month ? '?month=' + encodeURIComponent(month) : '');
    fetchJson(url).then(function (res) {
      if (res.status === 401) {
        showError(err, '401 unauthorized — sign in as Founder Super Admin.');
        return;
      }
      if (res.status === 403) {
        showError(err, '403 forbidden — Founder Super Admin required.');
        return;
      }
      if (!res.data || !res.data.ok) {
        showError(err, 'Failed to load dashboard.');
        return;
      }
      var d = res.data;
      paintLifecycle(d.lifecycle, d.lifecycleMonths);
      paintSegments(d.lifecycleSegments);
      var cards = [
        ['Total Users', d.totalUsers],
        ['Basic', d.basic],
        ['Pro', d.pro],
        ['Disabled', d.disabled],
        ['New Users 7d', d.newUsers7d],
        ['New Users 30d', d.newUsers30d],
        ['Latest Registration', d.latestRegistration],
      ];
      grid.innerHTML = cards.map(function (c) {
        return '<div class="card"><div class="label">' + c[0] + '</div><div class="value">' + dash(c[1]) + '</div></div>';
      }).join('');
    }).catch(function () {
      showError(err, 'Network error loading dashboard.');
    });
  }

  function renderUsers() {
    var err = document.getElementById('admin-error');
    var tbody = document.getElementById('users-tbody');
    if (!tbody) return;
    fetchJson(apiBase() + '/admin/users.php').then(function (res) {
      if (res.status === 401) {
        showError(err, '401 unauthorized — sign in as Founder Super Admin.');
        return;
      }
      if (res.status === 403) {
        showError(err, '403 forbidden — Founder Super Admin required.');
        return;
      }
      if (!res.data || !res.data.ok) {
        showError(err, 'Failed to load users.');
        return;
      }
      var users = res.data.users || [];
      tbody.innerHTML = users.map(function (u) {
        var rel = u.parentUserId ? ('P:' + u.parentUserId) : ('C:' + (u.childCount || 0));
        var profile = u.profileSynced ? dash(u.businessName) : 'Not synced';
        var detail = adminRoot() + '/users/detail/?id=' + encodeURIComponent(u.userId);
        return (
          '<tr data-href="' + detail + '">' +
          '<td>' + dash(u.userId) + '</td>' +
          '<td>' + dash(u.email) + '</td>' +
          '<td>' + dash(u.plan) + '</td>' +
          '<td>' + dash(u.planUpdatedAt) + '</td>' +
          '<td>' + dash(u.createdAt) + '</td>' +
          '<td>' + dash(u.lastLoginAt) + '</td>' +
          '<td>' + rel + '</td>' +
          '<td>' + profile + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.companyName) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.businessType) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.genre) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.locale) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.country) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.stateRegion) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.city) : 'N/A') + '</td>' +
          '<td>' + (u.profileSynced ? dash(u.currency) : 'N/A') + '</td>' +
          '<td>' + dash(u.accountStatus) + '</td>' +
          '<td>' + originHtml(u.signupOrigin) + '</td>' +
          '<td class="cell-toggle"><label class="toggle-label"><input type="checkbox" data-exclude-user="' + esc(u.userId) + '"' +
            (u.excludeFromMetrics ? ' checked' : '') + '> Exclude</label></td>' +
          '</tr>'
        );
      }).join('');
      Array.prototype.forEach.call(tbody.querySelectorAll('tr[data-href]'), function (tr) {
        tr.addEventListener('click', function (ev) {
          if (ev.target && ev.target.closest && ev.target.closest('.cell-toggle')) return;
          window.location.href = tr.getAttribute('data-href');
        });
      });
      Array.prototype.forEach.call(tbody.querySelectorAll('input[data-exclude-user]'), function (box) {
        box.addEventListener('change', function () {
          var next = box.checked;
          box.disabled = true;
          postExclusion({ userId: box.getAttribute('data-exclude-user'), exclude: next }).then(function (r) {
            box.disabled = false;
            if (!r.data || !r.data.ok) {
              box.checked = !next;
              showError(err, authFailMsg(r) || 'Exclude from metrics update failed.');
              return;
            }
            clearError(err);
          }).catch(function () {
            box.disabled = false;
            box.checked = !next;
            showError(err, 'Network error updating Exclude from metrics.');
          });
        });
      });
    }).catch(function () {
      showError(err, 'Network error loading users.');
    });
  }

  function postSetParent(childUserId, parentUserId) {
    return fetchJson(apiBase() + '/admin/set-parent.php', {
      method: 'POST',
      body: {
        userId: childUserId,
        parentUserId: parentUserId
      }
    });
  }

  function userOptionLabel(u) {
    return dash(u.email) + ' (' + dash(u.userId) + ')';
  }

  function paintDetail(root, err, detailId, detailPayload, allUsers) {
    var u = detailPayload.user || {};
    var p = detailPayload.profile || {};
    var hist = detailPayload.planHistory || [];
    var parent = detailPayload.parent;
    var children = detailPayload.children || [];
    var detailBase = adminRoot() + '/users/detail/?id=';
    var users = allUsers || [];

    function kv(label, value) {
      return '<div class="k">' + label + '</div><div class="v">' + dash(value) + '</div>';
    }

    var histHtml;
    if (!hist.length) {
      histHtml =
        '<div class="plan-history">' +
          '<h4>Plan History</h4>' +
          '<div class="muted">No plan history yet.</div>' +
        '</div>';
    } else {
      histHtml =
        '<div class="plan-history">' +
          '<h4>Plan History</h4>' +
          '<ul class="history-list">' +
          hist.map(function (h) {
            var plan = dash(h.newPlan);
            var when = dash(h.changedAt);
            var metaParts = [];
            if (h.oldPlan) metaParts.push(dash(h.oldPlan) + ' → ' + plan);
            if (h.source) metaParts.push(dash(h.source));
            if (h.changedBy) metaParts.push('by ' + dash(h.changedBy));
            var meta = metaParts.length ? '<div class="hist-meta">' + esc(metaParts.join(' · ')) + '</div>' : '';
            return (
              '<li>' +
                '<div class="hist-row"><span class="hist-k">Plan</span><span class="hist-v">' + esc(plan) + '</span></div>' +
                '<div class="hist-row"><span class="hist-k">Changed At</span><span class="hist-v">' + esc(when) + '</span></div>' +
                meta +
              '</li>'
            );
          }).join('') +
          '</ul>' +
        '</div>';
    }

    var parentHtml = parent
      ? '<a href="' + detailBase + encodeURIComponent(parent.userId) + '">' + esc(dash(parent.email)) + ' (' + esc(parent.userId) + ')</a>'
      : '<span class="muted">None</span>';

    var childRows = children.length
      ? children.map(function (c) {
          return (
            '<div class="rel-child-row">' +
              '<a href="' + detailBase + encodeURIComponent(c.userId) + '">' + esc(dash(c.email)) + ' (' + esc(c.userId) + ')</a>' +
              ' <button type="button" class="btn-admin btn-danger" data-rel-action="remove-child" data-child-id="' + esc(c.userId) + '">Remove</button>' +
            '</div>'
          );
        }).join('')
      : '<span class="muted">None</span>';

    var parentChoices = users.filter(function (x) {
      return x.userId && x.userId !== u.userId && !x.disabled;
    });
    var parentOpts = '<option value="">No Parent</option>' + parentChoices.map(function (x) {
      var sel = parent && parent.userId === x.userId ? ' selected' : '';
      return '<option value="' + esc(x.userId) + '"' + sel + '>' + esc(userOptionLabel(x)) + '</option>';
    }).join('');

    var childIds = {};
    children.forEach(function (c) { childIds[c.userId] = true; });
    var childChoices = users.filter(function (x) {
      return x.userId && x.userId !== u.userId && !x.disabled && !childIds[x.userId];
    });
    var childOpts = '<option value="">Select user…</option>' + childChoices.map(function (x) {
      return '<option value="' + esc(x.userId) + '">' + esc(userOptionLabel(x)) + '</option>';
    }).join('');

    var profileNote = p.synced ? '' : '<div class="muted">Server profile: Not synced</div>';

    root.innerHTML =
      '<div class="dossier">' +
      '<h2>User Dossier</h2>' +
      '<div class="section"><h3>Account</h3><div class="kv">' +
        kv('User ID', u.userId) +
        kv('Email', u.email) +
        kv('Status', u.disabled ? 'disabled' : 'active') +
        kv('Role', u.role) +
        kv('Created At', u.createdAt) +
        kv('Last Login', u.lastLoginAt) +
      '</div></div>' +
      '<div class="section"><h3>Subscription</h3><div class="kv">' +
        kv('Current Plan', u.plan) +
        kv('Plan Changed At', u.planUpdatedAt) +
      '</div>' + histHtml + '</div>' +
      '<div class="section"><h3>Business Profile</h3>' + profileNote + '<div class="kv">' +
        kv('Business Name', p.synced ? p.businessName : null) +
        kv('Company Name', p.synced ? p.companyName : null) +
        kv('Business Type', p.synced ? p.businessType : null) +
        kv('Genre', p.synced ? p.genre : null) +
      '</div></div>' +
      '<div class="section"><h3>Location</h3><div class="kv">' +
        kv('Language', p.synced ? p.locale : null) +
        kv('Country', p.synced ? p.country : null) +
        kv('State / Region', p.synced ? p.stateRegion : null) +
        kv('City', p.synced ? p.city : null) +
        kv('Currency', p.synced ? p.currency : null) +
      '</div></div>' +
      '<div class="section"><h3>Related Accounts</h3>' +
        '<div class="kv">' +
          '<div class="k">Parent Account</div><div class="v">' + parentHtml + '</div>' +
          '<div class="k">Child Accounts</div><div class="v">' + childRows + '</div>' +
        '</div>' +
        '<div class="rel-actions">' +
          '<button type="button" class="btn-admin" data-rel-action="toggle-parent">Change Parent</button>' +
          '<button type="button" class="btn-admin" data-rel-action="toggle-child">Add Child</button>' +
        '</div>' +
        '<div id="rel-parent-panel" class="rel-edit-panel" hidden>' +
          '<label class="rel-label">New parent</label>' +
          '<select id="rel-parent-select" class="admin-select">' + parentOpts + '</select>' +
          '<div class="rel-actions">' +
            '<button type="button" class="btn-admin" data-rel-action="save-parent">Save Parent</button>' +
            '<button type="button" class="btn-admin btn-muted" data-rel-action="cancel-parent">Cancel</button>' +
          '</div>' +
        '</div>' +
        '<div id="rel-child-panel" class="rel-edit-panel" hidden>' +
          '<label class="rel-label">Add child account</label>' +
          '<select id="rel-child-select" class="admin-select">' + childOpts + '</select>' +
          '<div class="rel-actions">' +
            '<button type="button" class="btn-admin" data-rel-action="save-child">Add Child</button>' +
            '<button type="button" class="btn-admin btn-muted" data-rel-action="cancel-child">Cancel</button>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="section"><h3>Admin Actions</h3>' +
        '<div class="actions-box">' +
          '<p class="actions-note">Password is never displayed.</p>' +
          '<div class="rel-actions">' +
            '<button type="button" class="btn-admin" data-admin-action="force-logout">Force Logout</button>' +
            '<button type="button" class="btn-admin" data-admin-action="send-reset">Send Password Reset</button>' +
            '<button type="button" class="btn-admin btn-danger" data-admin-action="toggle-disabled">' +
              (u.disabled ? 'Enable User' : 'Disable User') +
            '</button>' +
            '<button type="button" class="btn-admin btn-muted" data-admin-action="delete" disabled title="Reserved">Delete (reserved)</button>' +
          '</div>' +
          '<div id="admin-action-msg" class="actions-msg muted" hidden></div>' +
        '</div>' +
      '</div>' +
      '</div>';

    function reloadDetail() {
      clearError(err);
      renderDetail();
    }

    function failMsg(res) {
      if (res.status === 401) return '401 unauthorized — sign in as Founder Super Admin.';
      if (res.status === 403) return '403 forbidden — Founder Super Admin required.';
      if (res.data && res.data.error) return 'Failed: ' + res.data.error;
      return 'Related Accounts update failed.';
    }

    function actionFailMsg(res) {
      if (res.status === 401) return '401 unauthorized — sign in as Founder Super Admin.';
      if (res.status === 403) return '403 forbidden — Founder Super Admin required.';
      if (res.data && res.data.error) return 'Failed: ' + res.data.error;
      return 'Admin action failed.';
    }

    function showActionMsg(text, isError) {
      var msg = document.getElementById('admin-action-msg');
      if (!msg) return;
      msg.hidden = false;
      msg.textContent = text || '';
      msg.className = 'actions-msg' + (isError ? ' actions-msg-error' : ' actions-msg-ok');
    }

    function postAdminAction(path, body) {
      return fetchJson(apiBase() + path, { method: 'POST', body: body || {} });
    }

    root.querySelectorAll('[data-admin-action]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var action = btn.getAttribute('data-admin-action');
        if (action === 'delete') return;

        if (action === 'force-logout') {
          if (!window.confirm('Force logout this user on all active sessions? They can sign in again afterward.')) {
            return;
          }
          btn.disabled = true;
          postAdminAction('/admin/force-logout.php', { userId: detailId }).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, actionFailMsg(res));
              showActionMsg(actionFailMsg(res), true);
              return;
            }
            clearError(err);
            showActionMsg('Force logout completed. Active sessions invalidated.', false);
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error during force logout.');
          });
          return;
        }

        if (action === 'send-reset') {
          if (!window.confirm('Send a password reset email to this user?')) return;
          btn.disabled = true;
          postAdminAction('/admin/send-password-reset.php', { userId: detailId, locale: 'ja' }).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, actionFailMsg(res));
              showActionMsg(actionFailMsg(res), true);
              return;
            }
            clearError(err);
            showActionMsg('Password reset email sent.', false);
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error sending password reset.');
          });
          return;
        }

        if (action === 'toggle-disabled') {
          var nextDisabled = !u.disabled;
          var confirmText = nextDisabled
            ? 'Disable this user? They will be unable to sign in.'
            : 'Enable this user? They will be able to sign in again.';
          if (!window.confirm(confirmText)) return;
          btn.disabled = true;
          postAdminAction('/admin/set-disabled.php', {
            userId: detailId,
            disabled: nextDisabled
          }).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, actionFailMsg(res));
              showActionMsg(actionFailMsg(res), true);
              return;
            }
            clearError(err);
            showActionMsg(nextDisabled ? 'User disabled.' : 'User enabled.', false);
            reloadDetail();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error updating disabled status.');
          });
        }
      });
    });


    root.querySelectorAll('[data-rel-action]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var action = btn.getAttribute('data-rel-action');
        var parentPanel = document.getElementById('rel-parent-panel');
        var childPanel = document.getElementById('rel-child-panel');

        if (action === 'toggle-parent') {
          if (parentPanel) parentPanel.hidden = !parentPanel.hidden;
          if (childPanel) childPanel.hidden = true;
          return;
        }
        if (action === 'toggle-child') {
          if (childPanel) childPanel.hidden = !childPanel.hidden;
          if (parentPanel) parentPanel.hidden = true;
          return;
        }
        if (action === 'cancel-parent') {
          if (parentPanel) parentPanel.hidden = true;
          return;
        }
        if (action === 'cancel-child') {
          if (childPanel) childPanel.hidden = true;
          return;
        }
        if (action === 'save-parent') {
          var sel = document.getElementById('rel-parent-select');
          var nextParent = sel && sel.value ? sel.value : null;
          var label = nextParent ? nextParent : 'No Parent';
          if (!window.confirm('Change parent of this account to: ' + label + ' ?')) return;
          btn.disabled = true;
          postSetParent(detailId, nextParent).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, failMsg(res));
              return;
            }
            reloadDetail();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error updating parent.');
          });
          return;
        }
        if (action === 'save-child') {
          var csel = document.getElementById('rel-child-select');
          var childId = csel && csel.value ? csel.value : '';
          if (!childId) {
            showError(err, 'Select a child account first.');
            return;
          }
          if (!window.confirm('Set parent of ' + childId + ' to this account (' + detailId + ')?')) return;
          btn.disabled = true;
          postSetParent(childId, detailId).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, failMsg(res));
              return;
            }
            reloadDetail();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error adding child.');
          });
          return;
        }
        if (action === 'remove-child') {
          var rid = btn.getAttribute('data-child-id') || '';
          if (!rid) return;
          if (!window.confirm('Remove child link for ' + rid + ' (clear parent)?')) return;
          btn.disabled = true;
          postSetParent(rid, null).then(function (res) {
            btn.disabled = false;
            if (!res.data || !res.data.ok) {
              showError(err, failMsg(res));
              return;
            }
            reloadDetail();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error removing child.');
          });
        }
      });
    });
  }

  function renderDetail() {
    var err = document.getElementById('admin-error');
    var root = document.getElementById('detail-root');
    if (!root) return;
    var params = new URLSearchParams(window.location.search);
    var id = params.get('id') || '';
    if (!id) {
      showError(err, 'Missing user id.');
      return;
    }
    clearError(err);
    Promise.all([
      fetchJson(apiBase() + '/admin/user-detail.php?id=' + encodeURIComponent(id)),
      fetchJson(apiBase() + '/admin/users.php')
    ]).then(function (pair) {
      var res = pair[0];
      var usersRes = pair[1];
      if (res.status === 401) {
        showError(err, '401 unauthorized — sign in as Founder Super Admin.');
        return;
      }
      if (res.status === 403) {
        showError(err, '403 forbidden — Founder Super Admin required.');
        return;
      }
      if (res.status === 404) {
        showError(err, 'User not found.');
        return;
      }
      if (!res.data || !res.data.ok) {
        showError(err, 'Failed to load user detail.');
        return;
      }
      var allUsers = (usersRes.data && usersRes.data.ok && usersRes.data.users) ? usersRes.data.users : [];
      paintDetail(root, err, id, res.data, allUsers);
    }).catch(function () {
      showError(err, 'Network error loading detail.');
    });
  }

  function renderDeletedAccounts() {
    var err = document.getElementById('admin-error');
    var tbody = document.getElementById('lc-tbody');
    var status = document.getElementById('lc-status');
    var form = document.getElementById('lc-lookup-form');
    var input = document.getElementById('lc-lookup-email');
    var clearBtn = document.getElementById('lc-lookup-clear');
    var msg = document.getElementById('lc-lookup-msg');
    if (!tbody) return;
    var lookupRows = null;

    function setMsg(text, isError) {
      if (!msg) return;
      msg.hidden = !text;
      msg.textContent = text || '';
      msg.className = 'actions-msg' + (isError ? ' actions-msg-error' : ' actions-msg-ok');
    }

    function paint(rows, label) {
      if (status) status.textContent = label;
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="15" class="muted">No history rows.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (r) {
        var cleanup = r.cleanupStatus === 'complete' ? 'complete'
          : '<span class="danger">' + esc(dash(r.cleanupStatus)) + '</span>' +
            (r.cleanupDetail ? ' <span class="muted">' + esc(r.cleanupDetail) + '</span>' : '');
        return (
          '<tr>' +
          '<td>' + esc(dash(r.previousUserId)) + '</td>' +
          '<td>' + jstDateTime(r.accountCreatedAt) + '</td>' +
          '<td>' + jstDateTime(r.deletedAt) + '</td>' +
          '<td>' + esc(dash(r.lifetimeDays)) + ' d</td>' +
          '<td>' + esc(dash(r.planAtDeletion)) + '</td>' +
          '<td>' + esc(dash(r.accountKind)) + '</td>' +
          '<td>' + historySegmentHtml('country', r.country) + '</td>' +
          '<td>' + historySegmentHtml('businessType', r.businessType) + '</td>' +
          '<td>' + historySegmentHtml('currency', r.currency) + '</td>' +
          '<td>' + originHtml(r.signupOrigin) + '</td>' +
          '<td>' + cleanup + '</td>' +
          '<td>' + (r.returned ? '<span class="tag-returned">Returned</span> <span class="muted">' + jstDateTime(r.returnedAt) + '</span>' : 'Not Returned') + '</td>' +
          '<td>' + esc(dash(r.returnCount)) + '</td>' +
          '<td><label class="toggle-label"><input type="checkbox" data-exclude-lc="' + esc(r.lifecycleId) + '"' +
            (r.excludeFromMetrics ? ' checked' : '') + '> Exclude</label></td>' +
          '<td><button type="button" class="btn-admin btn-danger" data-erase-lc="' + esc(r.lifecycleId) + '" data-prev-id="' +
            esc(r.previousUserId) + '">Delete Row</button></td>' +
          '</tr>'
        );
      }).join('');
      Array.prototype.forEach.call(tbody.querySelectorAll('input[data-exclude-lc]'), function (box) {
        box.addEventListener('change', function () {
          var next = box.checked;
          box.disabled = true;
          postExclusion({ lifecycleId: box.getAttribute('data-exclude-lc'), exclude: next }).then(function (res) {
            box.disabled = false;
            if (!res.data || !res.data.ok) {
              box.checked = !next;
              showError(err, authFailMsg(res) || 'Exclude from metrics update failed.');
              return;
            }
            clearError(err);
          }).catch(function () {
            box.disabled = false;
            box.checked = !next;
            showError(err, 'Network error updating Exclude from metrics.');
          });
        });
      });
      Array.prototype.forEach.call(tbody.querySelectorAll('button[data-erase-lc]'), function (btn) {
        btn.addEventListener('click', function () {
          var id = btn.getAttribute('data-erase-lc');
          if (!window.confirm('Permanently delete the history row for ' + btn.getAttribute('data-prev-id') +
            '? Use this for erasure requests. This cannot be undone.')) return;
          btn.disabled = true;
          fetchJson(apiBase() + '/admin/lifecycle-erase.php', { method: 'POST', body: { lifecycleId: id } }).then(function (res) {
            if (!res.data || !res.data.ok) {
              btn.disabled = false;
              showError(err, authFailMsg(res) || 'History row delete failed.');
              return;
            }
            clearError(err);
            if (lookupRows) {
              lookupRows = lookupRows.filter(function (r) { return r.lifecycleId !== id; });
            }
            setMsg('History row deleted.', false);
            load();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error deleting history row.');
          });
        });
      });
    }

    function load() {
      fetchJson(apiBase() + '/admin/deleted-accounts.php').then(function (res) {
        if (!res.data || !res.data.ok) {
          showError(err, authFailMsg(res) || 'Failed to load deleted accounts.');
          return;
        }
        var all = res.data.rows || [];
        var readyNote = res.data.ready ? '' : ' · WARNING: lifecycle not ready (HMAC key or storage missing) — account deletion is blocked';
        if (lookupRows) {
          var ids = {};
          lookupRows.forEach(function (r) { ids[r.lifecycleId] = true; });
          lookupRows = all.filter(function (r) { return ids[r.lifecycleId]; });
          paint(lookupRows, lookupRows.length + ' matching row(s) for the looked-up email · ' + all.length + ' total' + readyNote);
        } else {
          paint(all, all.length + ' history row(s)' + readyNote);
        }
      }).catch(function () {
        showError(err, 'Network error loading deleted accounts.');
      });
    }

    if (form && input) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var entered = input.value;
        if (!entered || entered.indexOf('@') < 0) {
          setMsg('Enter an email address.', true);
          return;
        }
        fetchJson(apiBase() + '/admin/lifecycle-lookup.php', { method: 'POST', body: { email: entered } }).then(function (res) {
          input.value = '';
          if (!res.data || !res.data.ok) {
            setMsg(authFailMsg(res) || 'Lookup failed.', true);
            return;
          }
          lookupRows = res.data.rows || [];
          setMsg('Matched lookup: ' + entered, false);
          if (clearBtn) clearBtn.hidden = false;
          load();
        }).catch(function () {
          setMsg('Network error during lookup.', true);
        });
      });
    }
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        lookupRows = null;
        clearBtn.hidden = true;
        setMsg('', false);
        load();
      });
    }
    load();
  }

  function mktStatusHtml(r) {
    if (r.status === 'subscribed') return 'Subscribed';
    if (r.evidenceOnly) return 'Unsubscribed · evidence-only';
    return 'Unsubscribed';
  }

  function renderMarketing() {
    var err = document.getElementById('admin-error');
    var tbody = document.getElementById('mkt-tbody');
    var cards = document.getElementById('mkt-cards');
    var status = document.getElementById('mkt-status');
    var msg = document.getElementById('mkt-msg');
    if (!tbody) return;

    function setMsg(text, isError) {
      if (!msg) return;
      msg.hidden = !text;
      msg.textContent = text || '';
      msg.className = 'actions-msg' + (isError ? ' actions-msg-error' : ' actions-msg-ok');
    }

    function postAction(id, action) {
      return fetchJson(apiBase() + '/admin/marketing-action.php', { method: 'POST', body: { id: id, action: action } });
    }

    function paint(data) {
      var counts = data.counts || {};
      if (cards) {
        cards.innerHTML = [
          card('Subscribed', dash(counts.subscribed), 'Active recipients'),
          card('Evidence-only', dash(counts.evidenceOnly), 'Unsubscribed, retained after a send'),
          card('Total', dash(counts.total), 'Rows now')
        ].join('');
      }
      if (status) {
        status.textContent = (data.ready ? '' : 'WARNING: marketing store not ready · ') +
          dash(counts.total) + ' row(s). Token / hash / secret are never shown.';
      }
      var rows = data.rows || [];
      if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="muted">No email-update subscribers.</td></tr>';
        return;
      }
      tbody.innerHTML = rows.map(function (r) {
        var unsubBtn = r.status === 'subscribed'
          ? '<button type="button" class="btn-admin" data-mkt-action="unsubscribe" data-mkt-id="' + esc(String(r.id)) +
            '" data-mkt-email="' + esc(r.email) + '">Unsubscribe</button> '
          : '';
        var eraseBtn = '<button type="button" class="btn-admin btn-danger" data-mkt-action="erase" data-mkt-id="' +
          esc(String(r.id)) + '" data-mkt-email="' + esc(r.email) + '" data-mkt-sent="' +
          (r.lastMarketingSentAt ? '1' : '0') + '">Erase</button>';
        return (
          '<tr>' +
          '<td>' + esc(dash(r.email)) + '</td>' +
          '<td>' + mktStatusHtml(r) + '</td>' +
          '<td>' + esc(dash(r.locale)) + '</td>' +
          '<td>' + esc(dash(r.consentSource)) + '</td>' +
          '<td>' + jstDateTime(r.consentAt) + '</td>' +
          '<td>' + (r.lastMarketingSentAt ? jstDateTime(r.lastMarketingSentAt) : 'Never') + '</td>' +
          '<td>' + (r.hasAccount ? 'Yes' : 'No') + '</td>' +
          '<td>' + (r.unsubscribedAt ? jstDateTime(r.unsubscribedAt) + (r.unsubscribeSource ? ' · ' + esc(r.unsubscribeSource) : '') : '—') + '</td>' +
          '<td>' + (r.retainUntil ? jstDateTime(r.retainUntil) : '—') + '</td>' +
          '<td>' + unsubBtn + eraseBtn + '</td>' +
          '</tr>'
        );
      }).join('');
      Array.prototype.forEach.call(tbody.querySelectorAll('[data-mkt-action]'), function (btn) {
        btn.addEventListener('click', function () {
          var action = btn.getAttribute('data-mkt-action');
          var id = Number(btn.getAttribute('data-mkt-id'));
          var em = btn.getAttribute('data-mkt-email') || '';
          if (action === 'unsubscribe') {
            if (!window.confirm('Unsubscribe ' + em + ' from email updates? This cannot send mail.')) return;
          } else {
            var sent = btn.getAttribute('data-mkt-sent') === '1';
            var confirmText = sent
              ? 'Erase is blocked while this address is under legal hold (already mailed). Continue to check the hold?'
              : 'Permanently erase ' + em + '? Never mailed — the row and events will be deleted.';
            if (!window.confirm(confirmText)) return;
          }
          btn.disabled = true;
          postAction(id, action).then(function (res) {
            btn.disabled = false;
            if (res.status === 409) {
              setMsg('Legal hold: evidence must be kept until ' + dash(res.data && res.data.retainUntil) + '.', true);
              return;
            }
            if (!res.data || !res.data.ok) {
              showError(err, authFailMsg(res) || 'Email updates action failed.');
              return;
            }
            clearError(err);
            setMsg(action === 'unsubscribe'
              ? (res.data.result === 'already' ? 'Already unsubscribed.' : 'Unsubscribed.')
              : (res.data.result === 'erased' ? 'Row erased.' : 'Moved to evidence-only.'), false);
            load();
          }).catch(function () {
            btn.disabled = false;
            showError(err, 'Network error updating email updates.');
          });
        });
      });
    }

    function load() {
      fetchJson(apiBase() + '/admin/marketing-subscribers.php').then(function (res) {
        if (!res.data || !res.data.ok) {
          showError(err, authFailMsg(res) || 'Failed to load email updates.');
          return;
        }
        paint(res.data);
      }).catch(function () {
        showError(err, 'Network error loading email updates.');
      });
    }

    load();
  }

  document.addEventListener('DOMContentLoaded', function () {
    var page = document.body.getAttribute('data-admin-page');
    if (page === 'dashboard') renderDashboard();
    if (page === 'users') renderUsers();
    if (page === 'detail') renderDetail();
    if (page === 'deleted') renderDeletedAccounts();
    if (page === 'marketing') renderMarketing();
  });
})();
