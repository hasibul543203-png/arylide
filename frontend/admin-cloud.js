/* ARYLIDE Sovereign Cloud Admin Suite 24/7 (Client-Side Firebase Auth & Firestore Engine) */
(() => {
  'use strict';

  // State Management
  const state = {
    user: null,
    adminStatus: null,
    activeTab: 'dashboard',
    cms: {
      stats: {},
      company: {},
      projects: [],
      videos: [],
      social: {},
      calculator: {},
      meeting_settings: {}
    },
    unsubscribers: [],
    leads: [],
    referrals: [],
    appointments: [],
    meetings: [],
    auditLogs: [],
    adminsList: []
  };

  const getEl = id => document.getElementById(id);

  // Notifications / Toast
  function showToast(msg, type = 'info') {
    const existing = document.querySelector('.admin-toast');
    if (existing) existing.remove();
    const t = document.createElement('div');
    t.className = `admin-toast ${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { t.remove(); }, 4000);
  }

  // --- TAB SWITCHING ---
  function switchTab(tabId) {
    state.activeTab = tabId;
    document.querySelectorAll('.sidebar .nav-link').forEach(btn => {
      const match = btn.dataset.tab === tabId;
      btn.classList.toggle('active', match);
    });
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.hidden = panel.id !== `panel-${tabId}`;
    });
    const titleNode = document.querySelector('.header-title');
    if (titleNode && tabId === 'dashboard') titleNode.textContent = 'Executive Dashboard';
  }

  // Bind sidebar nav links and data-switch-tab buttons
  function bindTabs() {
    document.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    document.querySelectorAll('[data-switch-tab]').forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.switchTab));
    });
  }

  // --- FIREBASE INITIALIZATION & AUTH GATE ---
  async function initAuthGate() {
    if (!window.ARYLIDE_FIREBASE || !window.ARYLIDE_FIREBASE.enabled) {
      showToast('Firebase configuration missing.', 'error');
      return;
    }

    try {
      await window.ARYLIDE_FIREBASE.init();
    } catch (err) {
      console.warn('Firebase init warning:', err);
    }

    // Check query params for invite activation link (?setup=1&email=...)
    const params = new URLSearchParams(window.location.search);
    if (params.get('setup') === '1' && params.get('email')) {
      const inviteEmail = params.get('email').trim();
      const emailField = getEl('authEmail');
      const setupEmailField = getEl('setupEmail');
      if (emailField) emailField.value = inviteEmail;
      if (setupEmailField) setupEmailField.value = inviteEmail;
      typeof window.toggleAuthMode === 'function' && window.toggleAuthMode('setup');
    }

    // Auth State Observer
    window.addEventListener('aryl-auth-change', async e => {
      state.user = e.detail.user;
      await evaluateAdminAccess();
    });

    // Evaluate initial access
    state.user = window.ARYLIDE_FIREBASE.currentUser;
    await evaluateAdminAccess();
  }

  async function evaluateAdminAccess() {
    const overlay = getEl('adminAuthOverlay');
    if (!state.user) {
      if (overlay) overlay.hidden = false;
      return;
    }

    const status = await window.ARYLIDE_FIREBASE.getAdminAccessStatus();
    state.adminStatus = status;

    if (status.needsSetup) {
      // First-time Primary Owner Bootstrap required
      if (overlay) overlay.hidden = false;
      typeof window.toggleAuthMode === 'function' && window.toggleAuthMode('setup');
      const note = getEl('authSetupNotice');
      if (note) {
        note.hidden = false;
        note.textContent = 'Welcome! You are bootstrapping the ARYLIDE Sovereign Multi-Admin Suite as Primary Super Admin.';
      }
      return;
    }

    if (!status.isAdmin) {
      if (overlay) overlay.hidden = false;
      const err = getEl('authErrorMsg');
      if (err) {
        err.hidden = false;
        err.textContent = `Access Denied: ${state.user.email} is not registered in the Admin directory. Ask the Primary Super Admin for an invite.`;
      }
      return;
    }

    // Granted Admin Access!
    if (overlay) overlay.hidden = true;
    updateAdminProfileUI(status);
    startRealtimeSync();
  }

  function updateAdminProfileUI(status) {
    const emailNode = getEl('adminHeaderEmail');
    const roleNode = getEl('adminHeaderRole');
    if (emailNode && state.user) emailNode.textContent = state.user.email;
    if (roleNode) roleNode.textContent = status.role || 'Super Admin';

    // Update make admin visibility based on Super Admin role
    const makeAdminCard = getEl('makeAdminCard');
    if (makeAdminCard) {
      makeAdminCard.hidden = !status.isSuperAdmin && !status.isOwner;
    }
  }

  // --- REAL-TIME FIRESTORE SYNC ---
  function startRealtimeSync() {
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;

    // Clear previous snapshot listeners
    state.unsubscribers.forEach(u => u());
    state.unsubscribers = [];

    // 1. Sync CMS Public
    const unsubCms = db.collection('cms').doc('public').onSnapshot(snap => {
      if (snap.exists) {
        state.cms = { ...state.cms, ...snap.data() };
        renderCmsForms(state.cms);
        renderProjects(state.cms.projects || []);
        renderVideos(state.cms.videos || []);
        renderSocial(state.cms.social || {});
        renderCalculator(state.cms.calculator || {});
        renderMeetingSettings(state.cms.meeting_settings || {});
      } else {
        // Seed CMS if missing
        if (window.ARYLIDE_CMS_SEED) {
          db.collection('cms').doc('public').set(window.ARYLIDE_CMS_SEED, { merge: true }).catch(() => {});
        }
      }
    }, handleFirestoreError);
    state.unsubscribers.push(unsubCms);

    // 2. Sync Leads & Enquiries
    const unsubLeads = db.collection('leads').onSnapshot(snap => {
      const list = [];
      snap.forEach(doc => list.push({ id: doc.id, ...doc.data() }));
      state.leads = list;
      renderEnquiries(list);
      updateKpis();
    }, handleFirestoreError);
    state.unsubscribers.push(unsubLeads);

    // 3. Sync Referral Leads
    const unsubRefs = db.collection('referral_leads').onSnapshot(snap => {
      const list = [];
      snap.forEach(doc => list.push({ id: doc.id, ...doc.data() }));
      state.referrals = list;
      renderReferrals(list);
      updateKpis();
    }, handleFirestoreError);
    state.unsubscribers.push(unsubRefs);

    // 4. Sync Appointments
    const unsubAppts = db.collection('appointments').onSnapshot(snap => {
      const list = [];
      snap.forEach(doc => list.push({ id: doc.id, ...doc.data() }));
      state.appointments = list;
      renderAppointments(list);
      updateKpis();
    }, handleFirestoreError);
    state.unsubscribers.push(unsubAppts);

    // 5. Sync Meetings
    const unsubMtgs = db.collection('meetings').onSnapshot(snap => {
      const list = [];
      snap.forEach(doc => list.push({ id: doc.id, ...doc.data() }));
      state.meetings = list;
      renderMeetings(list);
      renderApprovals();
      updateKpis();
    }, handleFirestoreError);
    state.unsubscribers.push(unsubMtgs);

    // 6. Sync Admins Directory
    const unsubAdmins = db.collection('settings').doc('admins').onSnapshot(snap => {
      if (snap.exists) {
        const d = snap.data();
        state.adminsList = d.directory || [];
        renderAdminsDirectory(d);
      }
    }, handleFirestoreError);
    state.unsubscribers.push(unsubAdmins);

    // 7. Sync Audit Logs
    const unsubLogs = db.collection('audit_logs').limit(50).onSnapshot(snap => {
      const list = [];
      snap.forEach(doc => list.push({ id: doc.id, ...doc.data() }));
      state.auditLogs = list;
      renderAuditLogs(list);
    }, () => {});
    state.unsubscribers.push(unsubLogs);
  }

  function handleFirestoreError(err) {
    if (err && err.code === 'permission-denied') {
      const helper = getEl('firestoreRulesHelper');
      if (helper) helper.hidden = false;
      showToast('Permission denied. Please verify your firestore.rules deployment.', 'error');
    }
  }

  // --- RENDER FUNCTIONS ---

  function updateKpis() {
    const pendingMeetings = state.meetings.filter(m => (m.status || '').toLowerCase() === 'pending').length;
    const pendingEnquiries = state.leads.filter(l => (l.status || '').toLowerCase() === 'pending').length;
    const pendingAppts = state.appointments.filter(a => (a.status || '').toLowerCase() === 'pending').length;
    const totalPending = pendingMeetings + pendingEnquiries + pendingAppts;

    const elTotalPending = getEl('kpiTotalPending');
    if (elTotalPending) elTotalPending.textContent = `${totalPending} Requiring Action`;

    const elRegLeads = getEl('kpiRegisteredLeads');
    if (elRegLeads) elRegLeads.textContent = state.leads.length + state.referrals.length + state.appointments.length;

    const elPendingMeetings = getEl('kpiPendingMeetings');
    if (elPendingMeetings) elPendingMeetings.textContent = `${pendingMeetings} Pending`;

    const elActiveProjects = getEl('kpiActiveProjects');
    if (elActiveProjects) elActiveProjects.textContent = (state.cms.projects || []).length;
  }

  function renderApprovals() {
    const list = getEl('approvalsList');
    if (!list) return;

    const pending = [
      ...state.meetings.filter(m => (m.status || '').toLowerCase() === 'pending').map(m => ({ ...m, type: 'Meeting' })),
      ...state.leads.filter(l => (l.status || '').toLowerCase() === 'pending').map(l => ({ ...l, type: 'Lead' })),
      ...state.appointments.filter(a => (a.status || '').toLowerCase() === 'pending').map(a => ({ ...a, type: 'Appointment' }))
    ];

    if (pending.length === 0) {
      list.innerHTML = '<div class="empty-state">No pending actions requiring immediate attention. All items confirmed.</div>';
      return;
    }

    list.innerHTML = pending.slice(0, 8).map(item => {
      const isMtg = item.type === 'Meeting';
      const cleanPhone = (item.mobile || item.phone || '').replace(/[^0-9+]/g, '');
      const waLink = cleanPhone ? `https://wa.me/${cleanPhone.replace('+', '')}?text=${encodeURIComponent('Hello from ARYLIDE Holdings Limited.')}` : '#';
      const callLink = cleanPhone ? `tel:${cleanPhone}` : '#';

      return `
        <div class="approval-item" data-id="${item.id}" data-type="${item.type}">
          <div class="approval-info">
            <span class="badge ${isMtg ? 'gold' : 'blue'}">${item.type}</span>
            <strong>${item.name || 'Anonymous Client'}</strong>
            <small>${item.project || item.service || 'General Enquiry'} &bull; ${item.meeting_date || item.date || 'Pending'}</small>
          </div>
          <div class="approval-actions">
            ${cleanPhone ? `<a href="${waLink}" target="_blank" class="btn btn-sm" title="WhatsApp">WA</a>` : ''}
            ${cleanPhone ? `<a href="${callLink}" class="btn btn-sm" title="Call">Call</a>` : ''}
            <button class="btn btn-sm btn-gold" onclick="window.ARYLIDE_ADMIN.confirmItem('${item.id}', '${item.type}')">Confirm</button>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderEnquiries(leads) {
    const tbody = document.querySelector('.enquiry-table tbody');
    if (!tbody) return;
    if (leads.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">No customer enquiries received yet.</td></tr>';
      return;
    }
    tbody.innerHTML = leads.map(l => {
      const cleanPhone = (l.phone || '').replace(/[^0-9+]/g, '');
      return `
        <tr>
          <td>${formatDate(l.createdAt || l.created_at)}</td>
          <td><strong>${l.name || ''}</strong><br><small>${l.email || ''}</small></td>
          <td><a href="tel:${cleanPhone}">${l.phone || ''}</a></td>
          <td>${l.interest || 'General'}</td>
          <td>${l.message || ''}</td>
          <td><span class="status-badge ${l.status || 'pending'}">${l.status || 'pending'}</span></td>
          <td>
            <button class="btn btn-sm" onclick="window.ARYLIDE_ADMIN.updateStatus('leads', '${l.id}', 'contacted')">Contacted</button>
          </td>
        </tr>
      `;
    }).join('');
  }

  function renderReferrals(refs) {
    const tbody = document.querySelector('.ref-table tbody');
    if (!tbody) return;
    if (refs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center">No referral leads submitted yet.</td></tr>';
      return;
    }
    tbody.innerHTML = refs.map(r => `
      <tr>
        <td>${formatDate(r.createdAt || r.created_at)}</td>
        <td>${r.referrer_name || r.name || ''}</td>
        <td>${r.referrer_mobile || r.phone || ''}</td>
        <td><strong>${r.buyer_name || ''}</strong></td>
        <td>${r.buyer_mobile || ''}</td>
        <td>${r.project || ''}</td>
        <td><span class="status-badge ${r.status || 'pending'}">${r.status || 'pending'}</span></td>
        <td><button class="btn btn-sm btn-danger" onclick="window.ARYLIDE_ADMIN.deleteDoc('referral_leads', '${r.id}')">Delete</button></td>
      </tr>
    `).join('');
  }

  function renderAppointments(appts) {
    const tbody = document.querySelector('.appt-table tbody');
    if (!tbody) return;
    if (appts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">No site appointments booked yet.</td></tr>';
      return;
    }
    tbody.innerHTML = appts.map(a => `
      <tr>
        <td>${a.appointment_date || a.date || ''}</td>
        <td><strong>${a.name || ''}</strong></td>
        <td>${a.phone || ''}</td>
        <td>${a.service || 'Site Visit'}</td>
        <td>${a.message || ''}</td>
      </tr>
    `).join('');
  }

  function renderMeetings(mtgs) {
    const tbody = document.querySelector('.meeting-table tbody');
    if (!tbody) return;
    if (mtgs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center">No calendar meetings scheduled yet.</td></tr>';
      return;
    }
    tbody.innerHTML = mtgs.map(m => `
      <tr>
        <td><code>${m.serial_number || m.id.slice(-6)}</code></td>
        <td>${m.meeting_date || m.date || ''}</td>
        <td>${m.meeting_time || m.time || ''}</td>
        <td><strong>${m.name || ''}</strong><br><small>${m.email || ''}</small></td>
        <td>${m.mobile || ''}</td>
        <td>${m.project || ''}</td>
        <td><span class="status-badge ${(m.status || '').toLowerCase()}">${m.status || 'Pending'}</span></td>
        <td>
          <button class="btn btn-sm btn-gold" onclick="window.ARYLIDE_ADMIN.confirmItem('${m.id}', 'Meeting')">Confirm</button>
          <button class="btn btn-sm btn-danger" onclick="window.ARYLIDE_ADMIN.cancelMeetingCloud('${m.id}')">Cancel</button>
        </td>
      </tr>
    `).join('');
  }

  function renderProjects(projects) {
    const list = getEl('projectCatalogList');
    if (!list) return;
    list.innerHTML = projects.map(p => `
      <div class="project-item-card">
        <img src="${(p.images && p.images[0]) || '/assets/sky-high-tower.jpg'}" alt="${p.name}">
        <div class="project-item-details">
          <strong>${p.name}</strong> <span>(${p.name_bn || ''})</span>
          <p>${p.location || ''} &bull; Sector: ${p.sector || 'N/A'} &bull; ${p.status || 'details'}</p>
          <div class="project-actions">
            <button class="btn btn-sm" onclick="window.ARYLIDE_ADMIN.editProject('${p.id}')">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="window.ARYLIDE_ADMIN.deleteProject('${p.id}')">Remove</button>
          </div>
        </div>
      </div>
    `).join('');
  }

  function renderVideos(videos) {
    const list = getEl('videoList');
    if (!list) return;
    list.innerHTML = videos.map((v, i) => `
      <div class="video-list-item">
        <span>#${i+1}</span>
        <strong>${v.title_en || v.title || 'Walkthrough'}</strong>
        <code>${v.youtube_url}</code>
        <button class="btn btn-sm btn-danger" onclick="window.ARYLIDE_ADMIN.removeVideo(${i})">Delete</button>
      </div>
    `).join('');
  }

  function renderSocial(social) {
    const form = getEl('socialForm');
    if (!form) return;
    for (const [k, v] of Object.entries(social)) {
      const field = form.querySelector(`[name="${k}"]`);
      if (field) field.value = v || '';
    }
  }

  function renderCalculator(calc) {
    const form = getEl('calculatorForm');
    if (!form) return;
    for (const [k, v] of Object.entries(calc)) {
      const field = form.querySelector(`[name="${k}"]`);
      if (field) field.value = v ?? '';
    }
  }

  function renderMeetingSettings(ms) {
    const form = getEl('meetingSettingsForm');
    if (!form) return;
    for (const [k, v] of Object.entries(ms)) {
      const field = form.querySelector(`[name="${k}"]`);
      if (field) field.value = Array.isArray(v) ? v.join(',') : v;
    }
  }

  function renderCmsForms(cms) {
    const stats = cms.stats || {};
    for (const [k, v] of Object.entries(stats)) {
      const field = getEl(`stat_${k}`);
      if (field) field.value = v || '';
    }
    const comp = cms.company || {};
    for (const [k, v] of Object.entries(comp)) {
      const field = getEl(`company_${k}`);
      if (field) field.value = v || '';
    }
    const reward = getEl('referral_reward_bdt');
    if (reward && cms.referral_reward_bdt) reward.value = cms.referral_reward_bdt;
  }

  function renderAuditLogs(logs) {
    const tbody = document.querySelector('#panel-activity-logs tbody');
    if (!tbody) return;
    if (logs.length === 0) return;
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>${formatDate(l.timestamp || l.createdAt)}</td>
        <td><strong>${l.operator || 'Admin'}</strong></td>
        <td>${l.action || ''}</td>
        <td><code>${l.target || ''}</code></td>
        <td><span class="tag">${l.tag || 'SYSTEM'}</span></td>
      </tr>
    `).join('');
  }

  // --- MULTI-ADMIN "MAKE ANYONE ADMIN" SYSTEM ---
  function renderAdminsDirectory(adminDoc) {
    const tbody = getEl('adminsTableBody');
    if (!tbody) return;

    const directory = adminDoc.directory || [];
    const primaryEmail = (adminDoc.primaryEmail || '').toLowerCase();

    tbody.innerHTML = directory.map(adm => {
      const email = (adm.email || '').toLowerCase();
      const isPrimary = email === primaryEmail || adm.isPrimary;
      const inviteUrl = `${window.location.origin}/admin.html?setup=1&email=${encodeURIComponent(email)}`;

      return `
        <tr>
          <td><strong>${adm.name || 'Admin'}</strong></td>
          <td><code>${email}</code></td>
          <td><span class="role-badge ${adm.role === 'Super Admin' ? 'gold' : 'blue'}">${adm.role}</span></td>
          <td>${isPrimary ? '<span class="status-badge success">PRIMARY OWNER</span>' : '<span class="status-badge">ACTIVE</span>'}</td>
          <td>
            <button class="btn btn-sm" onclick="window.ARYLIDE_ADMIN.copyInvite('${inviteUrl}')">Copy Invite</button>
            ${isPrimary ? '<span class="locked-badge" title="Primary Owner is permanently protected">&#128274; Permanent</span>' : `
              <button class="btn btn-sm btn-danger" onclick="window.ARYLIDE_ADMIN.revokeAdmin('${email}')">Revoke</button>
            `}
          </td>
        </tr>
      `;
    }).join('');
  }

  // --- FORM SUBMISSIONS & ACTIONS ---

  async function saveCms(event) {
    event.preventDefault();
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;

    const stats = {
      projects: getEl('stat_projects')?.value || '3+',
      completed: getEl('stat_completed')?.value || '3',
      happy_clients: getEl('stat_happy_clients')?.value || '30+',
      years_trust: getEl('stat_years_trust')?.value || '2',
      area_built: getEl('stat_area_built')?.value || '51,000',
      vision_sqft: getEl('stat_vision_sqft')?.value || '27,394,800'
    };

    const company = {
      phone: getEl('company_phone')?.value || '',
      email: getEl('company_email')?.value || '',
      address: getEl('company_address')?.value || ''
    };

    const reward = getEl('referral_reward_bdt')?.value || '200000';

    try {
      await db.collection('cms').doc('public').set({
        stats,
        company,
        referral_reward_bdt: reward,
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      logAudit('UPDATE_CMS', 'Homepage Stats & Company Contact', 'CMS');
      showToast('Homepage CMS updated successfully!', 'success');
    } catch (err) {
      showToast('Failed to save CMS: ' + err.message, 'error');
    }
  }

  async function saveSocial(event) {
    event.preventDefault();
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;

    const form = getEl('socialForm');
    const values = Object.fromEntries(new FormData(form).entries());

    try {
      await db.collection('cms').doc('public').set({
        social: values,
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
      logAudit('UPDATE_SOCIAL', 'Social Media Links & Embeds', 'SOCIAL');
      showToast('Social settings saved!', 'success');
    } catch (err) {
      showToast('Error saving social: ' + err.message, 'error');
    }
  }

  async function saveCalculator(event) {
    event.preventDefault();
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;

    const form = getEl('calculatorForm');
    const values = Object.fromEntries(new FormData(form).entries());
    for (const k in values) {
      values[k] = Number(values[k]) || 0;
    }

    try {
      await db.collection('cms').doc('public').set({
        calculator: values,
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
      logAudit('UPDATE_CALCULATOR', 'Investment Calculator Assumptions', 'CALC');
      showToast('Calculator settings saved!', 'success');
    } catch (err) {
      showToast('Error saving calculator: ' + err.message, 'error');
    }
  }

  async function addAdmin(event) {
    event.preventDefault();
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;

    const email = (getEl('newAdminEmail')?.value || '').trim().toLowerCase();
    const name = (getEl('newAdminName')?.value || '').trim();
    const role = getEl('newAdminRole')?.value || 'Admin';

    if (!email) {
      showToast('Please enter a valid email address.', 'error');
      return;
    }

    try {
      const adminDocRef = db.collection('settings').doc('admins');
      const snap = await adminDocRef.get();
      if (!snap.exists) throw new Error('Admin registry not initialized.');

      const doc = snap.data();
      const emails = doc.emails || [];
      const superEmails = doc.superEmails || [];
      const roles = doc.roles || {};
      const directory = doc.directory || [];

      if (!emails.includes(email)) emails.push(email);
      if (role === 'Super Admin' && !superEmails.includes(email)) superEmails.push(email);
      roles[email] = role;

      const existingIndex = directory.findIndex(d => (d.email || '').toLowerCase() === email);
      const adminEntry = {
        email: email,
        name: name || 'Admin',
        role: role,
        addedAt: new Date().toISOString(),
        addedBy: state.user?.email || 'Owner',
        isPrimary: false
      };

      if (existingIndex >= 0) {
        directory[existingIndex] = adminEntry;
      } else {
        directory.push(adminEntry);
      }

      await adminDocRef.set({
        emails: emails,
        superEmails: superEmails,
        roles: roles,
        directory: directory,
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      logAudit('ADD_ADMIN', `Added ${email} as ${role}`, 'ACCESS');
      showToast(`Admin ${email} added! Share the 1-click invite link.`, 'success');
      getEl('addAdminForm')?.reset();
    } catch (err) {
      showToast('Failed to add admin: ' + err.message, 'error');
    }
  }

  async function revokeAdmin(email) {
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;
    const cleanEmail = email.toLowerCase();

    if (!confirm(`Revoke administrative access for ${cleanEmail}?`)) return;

    try {
      const adminDocRef = db.collection('settings').doc('admins');
      const snap = await adminDocRef.get();
      if (!snap.exists) return;

      const doc = snap.data();
      if ((doc.primaryEmail || '').toLowerCase() === cleanEmail) {
        showToast('The Primary Owner cannot be revoked or locked out!', 'error');
        return;
      }

      const emails = (doc.emails || []).filter(e => e.toLowerCase() !== cleanEmail);
      const superEmails = (doc.superEmails || []).filter(e => e.toLowerCase() !== cleanEmail);
      const directory = (doc.directory || []).filter(d => (d.email || '').toLowerCase() !== cleanEmail);
      const roles = { ...doc.roles };
      delete roles[cleanEmail];

      await adminDocRef.set({
        emails: emails,
        superEmails: superEmails,
        directory: directory,
        roles: roles,
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      logAudit('REVOKE_ADMIN', `Revoked ${cleanEmail}`, 'ACCESS');
      showToast(`Access revoked for ${cleanEmail}.`, 'info');
    } catch (err) {
      showToast('Error revoking admin: ' + err.message, 'error');
    }
  }

  async function logAudit(action, target, tag) {
    const db = window.ARYLIDE_FIREBASE.db;
    if (!db) return;
    try {
      await db.collection('audit_logs').add({
        operator: state.user?.email || 'Admin',
        action: action,
        target: target,
        tag: tag,
        createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
      });
    } catch (_) {}
  }

  function formatDate(ts) {
    if (!ts) return '';
    try {
      const date = ts.toDate ? ts.toDate() : new Date(ts);
      return date.toLocaleString();
    } catch (_) {
      return String(ts);
    }
  }


  function generateInviteLink(email) {
    if (!email) return '';
    return `${window.location.origin}/admin.html?setup=1&email=${encodeURIComponent(email)}`;
  }

  // --- EXPORT GLOBAL HELPER ---
  window.ARYLIDE_ADMIN = {
    switchTab,
    saveCms,
    saveSocial,
    saveCalculator,
    addAdmin,
    revokeAdmin,
    claimFirstAdmin: async (name) => {
      if (!window.ARYLIDE_FIREBASE) return;
      return window.ARYLIDE_FIREBASE.claimFirstAdmin(name);
    },
    generateInviteLink,
    copyInvite: url => {
      navigator.clipboard.writeText(url).then(() => showToast('Invite activation link copied!', 'success'));
    },
    confirmItem: async (id, type) => {
      const db = window.ARYLIDE_FIREBASE.db;
      if (!db) return;
      const col = type === 'Meeting' ? 'meetings' : (type === 'Lead' ? 'leads' : 'appointments');
      await db.collection(col).doc(id).set({ status: 'Confirmed' }, { merge: true });
      showToast(`${type} confirmed!`, 'success');
    },
    updateStatus: async (col, id, status) => {
      const db = window.ARYLIDE_FIREBASE.db;
      if (!db) return;
      await db.collection(col).doc(id).set({ status: status }, { merge: true });
      showToast(`Status updated to ${status}.`, 'info');
    },
    cancelMeetingCloud: async id => {
      if (!confirm('Cancel this meeting?')) return;
      await window.ARYLIDE_FIREBASE.manageMeetingCloud(id, 'cancel');
      showToast('Meeting cancelled.', 'info');
    },
    deleteDoc: async (col, id) => {
      if (!confirm('Permanently delete this record?')) return;
      const db = window.ARYLIDE_FIREBASE.db;
      if (!db) return;
      await db.collection(col).doc(id).delete();
      showToast('Record deleted.', 'info');
    }
  };

  // Wire on DOM Ready
  window.addEventListener('DOMContentLoaded', () => {
    bindTabs();
    initAuthGate();

    getEl('cmsForm')?.addEventListener('submit', saveCms);
    getEl('socialForm')?.addEventListener('submit', saveSocial);
    getEl('calculatorForm')?.addEventListener('submit', saveCalculator);
    getEl('addAdminForm')?.addEventListener('submit', addAdmin);
    getEl('signOutBtn')?.addEventListener('click', async () => {
      if (window.ARYLIDE_FIREBASE) await window.ARYLIDE_FIREBASE.signOut();
      location.reload();
    });
  });
})();
