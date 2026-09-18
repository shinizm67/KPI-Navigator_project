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

  document.addEventListener('DOMContentLoaded', function () {
    var page = document.body.getAttribute('data-admin-page');
    if (page === 'dashboard') renderDashboard();
    if (page === 'users') renderUsers();
    if (page === 'detail') renderDetail();
  });
})();
