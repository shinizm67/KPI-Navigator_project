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

  function fetchJson(url) {
    return fetch(url, { credentials: 'include', cache: 'no-store' }).then(function (r) {
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

  function renderDashboard() {
    var err = document.getElementById('admin-error');
    var grid = document.getElementById('dash-cards');
    if (!grid) return;
    fetchJson(apiBase() + '/admin/dashboard.php').then(function (res) {
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
          '</tr>'
        );
      }).join('');
      Array.prototype.forEach.call(tbody.querySelectorAll('tr[data-href]'), function (tr) {
        tr.addEventListener('click', function () {
          window.location.href = tr.getAttribute('data-href');
        });
      });
    }).catch(function () {
      showError(err, 'Network error loading users.');
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
    fetchJson(apiBase() + '/admin/user-detail.php?id=' + encodeURIComponent(id)).then(function (res) {
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
      var u = res.data.user || {};
      var p = res.data.profile || {};
      var hist = res.data.planHistory || [];
      var parent = res.data.parent;
      var children = res.data.children || [];
      var detailBase = adminRoot() + '/users/detail/?id=';

      function kv(label, value) {
        return '<div class="k">' + label + '</div><div class="v">' + dash(value) + '</div>';
      }

      var histHtml = hist.length
        ? '<ul class="history-list">' + hist.map(function (h) {
            return '<li>' + dash(h.changedAt) + ' · ' + dash(h.oldPlan) + ' → ' + dash(h.newPlan) +
              ' · ' + dash(h.source) + (h.changedBy ? (' · by ' + h.changedBy) : '') + '</li>';
          }).join('') + '</ul>'
        : '<div class="muted">No plan history yet.</div>';

      var parentHtml = parent
        ? '<a href="' + detailBase + encodeURIComponent(parent.userId) + '">' + dash(parent.email) + ' (' + parent.userId + ')</a>'
        : '<span class="muted">None</span>';

      var childHtml = children.length
        ? children.map(function (c) {
            return '<div><a href="' + detailBase + encodeURIComponent(c.userId) + '">' + dash(c.email) + ' (' + c.userId + ')</a></div>';
          }).join('')
        : '<span class="muted">None</span>';

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
        '</div><div style="margin-top:10px">' + histHtml + '</div></div>' +
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
        '<div class="section"><h3>Related Accounts</h3><div class="kv">' +
          '<div class="k">Parent Account</div><div class="v">' + parentHtml + '</div>' +
          '<div class="k">Child Accounts</div><div class="v">' + childHtml + '</div>' +
        '</div></div>' +
        '<div class="section"><h3>Admin Actions</h3>' +
          '<div class="actions-box">Force Logout / Password Reset / Disable / Delete — reserved for later phases. Password is never displayed.</div>' +
        '</div>' +
        '</div>';
    }).catch(function () {
      showError(err, 'Network error loading detail.');
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var page = document.body.getAttribute('data-admin-page');
    if (page === 'dashboard') renderDashboard();
    if (page === 'users') renderUsers();
    if (page === 'detail') renderDetail();
  });
})();
