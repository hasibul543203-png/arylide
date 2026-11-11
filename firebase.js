/* Firebase Cloud Firestore & Auth Adapter for ARYLIDE Holdings Limited */
(function () {
  const cfg = window.CONFIG || {};
  const required = ['FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN', 'FIREBASE_PROJECT_ID', 'FIREBASE_APP_ID'];
  const state = {
    app: null,
    auth: null,
    db: null,
    ready: false,
    enabled: required.every(key => String(cfg[key] || '').trim()),
    loading: null,
    phoneConfirmation: null,
    recaptcha: null,
    currentUser: null,
    authStateReady: null,
    resolveAuthState: null
  };
  const SDK = 'https://www.gstatic.com/firebasejs/10.14.1/';

  function loadScript(name) {
    return new Promise((resolve, reject) => {
      if (document.querySelector('script[data-firebase-sdk="' + name + '"]')) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = SDK + 'firebase-' + name + '-compat.js';
      script.async = true;
      script.dataset.firebaseSdk = name;
      script.onload = resolve;
      script.onerror = () => reject(new Error('Could not load Firebase ' + name + ' SDK.'));
      document.head.appendChild(script);
    });
  }

  async function init() {
    if (!state.enabled) return false;
    if (state.ready) return true;
    if (state.loading) return state.loading;
    state.loading = (async () => {
      await loadScript('app');
      await loadScript('auth');
      await loadScript('firestore');
      state.app = window.firebase.apps.length ? window.firebase.app() : window.firebase.initializeApp({
        apiKey: cfg.FIREBASE_API_KEY,
        authDomain: cfg.FIREBASE_AUTH_DOMAIN,
        projectId: cfg.FIREBASE_PROJECT_ID,
        storageBucket: cfg.FIREBASE_STORAGE_BUCKET || undefined,
        appId: cfg.FIREBASE_APP_ID,
        messagingSenderId: cfg.FIREBASE_MESSAGING_SENDER_ID || undefined
      });
      state.auth = window.firebase.auth();
      state.db = window.firebase.firestore();
      state.authStateReady = new Promise(resolve => { state.resolveAuthState = resolve; });

      state.auth.onAuthStateChanged(async user => {
        state.currentUser = user || null;
        if (state.resolveAuthState) {
          state.resolveAuthState(state.currentUser);
          state.resolveAuthState = null;
        }
        if (user) {
          const profile = user.displayName || '';
          await saveUser(user, profile, user.phoneNumber || '').catch(() => {});
        }
        window.dispatchEvent(new CustomEvent('aryl-auth-change', { detail: { user: user || null } }));
      });

      await state.auth.getRedirectResult().catch(() => null);
      await state.authStateReady;
      state.ready = true;
      return true;
    })();
    try { return await state.loading; } finally { state.loading = null; }
  }

  async function saveUser(user, name, phone) {
    if (!state.db || !user) return;
    const ref = state.db.collection('users').doc(user.uid);
    const snap = await ref.get().catch(() => ({ exists: false }));
    const data = snap.exists ? snap.data() : {};
    await ref.set({
      uid: user.uid,
      name: name || user.displayName || data.name || '',
      email: user.email || data.email || '',
      phone: phone || user.phoneNumber || data.phone || '',
      createdAt: data.createdAt || window.firebase.firestore.FieldValue.serverTimestamp(),
      updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
  }

  async function signInEmail(email, password) {
    await init();
    return state.auth.signInWithEmailAndPassword(email, password);
  }

  async function signUpEmail(name, phone, email, password) {
    await init();
    const credential = await state.auth.createUserWithEmailAndPassword(email, password);
    if (name) await credential.user.updateProfile({ displayName: name });
    await saveUser(credential.user, name, phone);
    return credential;
  }

  async function signInGoogle() {
    await init();
    const provider = new window.firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    try {
      return await state.auth.signInWithPopup(provider);
    } catch (error) {
      if (error && ['auth/popup-blocked', 'auth/operation-not-supported-in-this-environment', 'auth/web-storage-unsupported'].includes(error.code)) {
        await state.auth.signInWithRedirect(provider);
        return null;
      }
      throw error;
    }
  }

  async function startPhone(phone, name) {
    await init();
    if (!state.recaptcha) {
      state.recaptcha = new window.firebase.auth.RecaptchaVerifier('firebase-recaptcha', { size: 'normal' });
      await state.recaptcha.render();
    }
    state.phoneName = name || '';
    state.phoneConfirmation = await state.auth.signInWithPhoneNumber(phone, state.recaptcha);
    return true;
  }

  async function verifyPhone(code, phone) {
    if (!state.phoneConfirmation) throw new Error('Send a phone verification code first.');
    const credential = await state.phoneConfirmation.confirm(code);
    if (state.phoneName && credential.user && !credential.user.displayName) {
      await credential.user.updateProfile({ displayName: state.phoneName });
    }
    await saveUser(credential.user, state.phoneName, phone);
    return credential;
  }

  async function sendPasswordReset(email) {
    await init();
    return state.auth.sendPasswordResetEmail(email);
  }

  async function signOut() {
    if (state.auth) await state.auth.signOut();
  }

  // --- CLOUD FIRESTORE ZERO-DATA-LOSS CMS METHODS ---

  async function getPublicCms() {
    await init();
    if (!state.db) return window.ARYLIDE_CMS_SEED || null;
    try {
      const docRef = state.db.collection('cms').doc('public');
      const snap = await docRef.get();
      if (snap.exists) {
        return snap.data();
      }
      // Strictly additive seeding: Seed ONLY IF doc does not exist
      if (window.ARYLIDE_CMS_SEED) {
        await docRef.set({
          ...window.ARYLIDE_CMS_SEED,
          seededAt: window.firebase.firestore.FieldValue.serverTimestamp()
        }, { merge: true }).catch(err => console.warn('Could not auto-seed CMS (likely non-admin client):', err));
      }
      return window.ARYLIDE_CMS_SEED || null;
    } catch (err) {
      console.warn('getPublicCms fallback to seed:', err);
      return window.ARYLIDE_CMS_SEED || null;
    }
  }

  function subscribePublicCms(callback) {
    init().then(() => {
      if (!state.db) return;
      return state.db.collection('cms').doc('public').onSnapshot(snap => {
        if (snap.exists) {
          callback(snap.data());
        }
      }, err => console.warn('CMS onSnapshot error:', err));
    });
  }

  // --- BOOKING SLOTS & MEETINGS ---

  async function getBookedSlots() {
    await init();
    if (!state.db) return {};
    try {
      const snap = await state.db.collection('booked_slots').get();
      const slots = {};
      snap.forEach(doc => { slots[doc.id] = true; });
      return slots;
    } catch (err) {
      console.warn('getBookedSlots fallback:', err);
      return {};
    }
  }

  async function bookMeetingCloud(meeting) {
    await init();
    if (!state.db) throw new Error('Cloud database unavailable');
    const slotKey = `${meeting.date}|${meeting.time}`;
    const slotRef = state.db.collection('booked_slots').doc(slotKey);
    const meetingId = meeting.id || ('MTG-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2, 6).toUpperCase());
    const meetingRef = state.db.collection('meetings').doc(meetingId);

    // Double-booking check
    const slotSnap = await slotRef.get();
    if (slotSnap.exists && slotSnap.data().status !== 'cancelled') {
      throw new Error('This time slot is already booked. Please choose another.');
    }

    const uid = state.currentUser ? state.currentUser.uid : (meeting.uid || '');
    const email = meeting.email || (state.currentUser ? state.currentUser.email : '');

    // Reserve slot
    await slotRef.set({
      slot: slotKey,
      meetingId: meetingId,
      date: meeting.date,
      time: meeting.time,
      status: 'booked',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });

    // Save meeting details
    await meetingRef.set({
      ...meeting,
      id: meetingId,
      uid: uid,
      email: email,
      status: meeting.status || 'Pending',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });

    return { ok: true, id: meetingId };
  }

  async function manageMeetingCloud(meetingId, action, newDate, newTime) {
    await init();
    if (!state.db) throw new Error('Cloud database unavailable');
    const meetingRef = state.db.collection('meetings').doc(meetingId);
    const snap = await meetingRef.get();
    if (!snap.exists) throw new Error('Meeting not found');
    const m = snap.data();

    if (action === 'cancel') {
      await meetingRef.set({
        status: 'Cancelled',
        cancelledAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });
      if (m.date && m.time) {
        const oldSlotKey = `${m.date}|${m.time}`;
        await state.db.collection('booked_slots').doc(oldSlotKey).delete().catch(() => {});
      }
      return { ok: true, status: 'Cancelled' };
    }

    if (action === 'reschedule') {
      if (!newDate || !newTime) throw new Error('New date and time required');
      const newSlotKey = `${newDate}|${newTime}`;
      const newSlotRef = state.db.collection('booked_slots').doc(newSlotKey);
      const newSlotSnap = await newSlotRef.get();
      if (newSlotSnap.exists) throw new Error('New time slot is already booked');

      // Free old slot
      if (m.date && m.time) {
        await state.db.collection('booked_slots').doc(`${m.date}|${m.time}`).delete().catch(() => {});
      }

      // Reserve new slot
      await newSlotRef.set({
        slot: newSlotKey,
        meetingId: meetingId,
        date: newDate,
        time: newTime,
        status: 'booked',
        createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      // Update meeting
      await meetingRef.set({
        date: newDate,
        time: newTime,
        status: 'Rescheduled',
        updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      return { ok: true, status: 'Rescheduled' };
    }

    throw new Error('Unknown action: ' + action);
  }

  async function getUserMeetings(uid) {
    await init();
    if (!state.db) return [];
    try {
      const userUid = uid || (state.currentUser ? state.currentUser.uid : null);
      if (!userUid) return [];
      const snap = await state.db.collection('meetings').where('uid', '==', userUid).get();
      const list = [];
      snap.forEach(doc => list.push(doc.data()));
      return list;
    } catch (err) {
      console.warn('getUserMeetings fallback:', err);
      return [];
    }
  }

  // --- LEADS, REFERRALS & APPOINTMENTS ---

  async function submitLeadCloud(values) {
    await init();
    if (!state.db) throw new Error('Cloud database unavailable');
    const id = values.id || ('LEAD-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2, 6).toUpperCase());
    const referralCode = 'ARY-' + Math.random().toString(36).substring(2, 10).toUpperCase();

    const data = {
      ...values,
      id: id,
      referral_code_generated: referralCode,
      status: values.status || 'pending',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    };

    await state.db.collection('leads').doc(id).set(data, { merge: true });

    // Store generated referral code in public index
    await state.db.collection('referral_codes').doc(referralCode).set({
      code: referralCode,
      leadId: id,
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true }).catch(() => {});

    return { ok: true, id: id, referral_code: referralCode, created_at: new Date().toISOString() };
  }

  async function submitReferralCloud(values) {
    await init();
    if (!state.db) throw new Error('Cloud database unavailable');
    const id = values.id || ('REF-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2, 6).toUpperCase());
    const data = {
      ...values,
      id: id,
      status: values.status || 'pending',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    };
    await state.db.collection('referral_leads').doc(id).set(data, { merge: true });
    return { ok: true, id: id, created_at: new Date().toISOString() };
  }

  async function submitAppointmentCloud(values) {
    await init();
    if (!state.db) throw new Error('Cloud database unavailable');
    const id = values.id || ('APT-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).slice(2, 6).toUpperCase());
    const data = {
      ...values,
      id: id,
      status: values.status || 'pending',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    };
    await state.db.collection('appointments').doc(id).set(data, { merge: true });
    return { ok: true, id: id, created_at: new Date().toISOString() };
  }

  // --- MULTI-ADMIN AUTH & SETUP METHODS ---

  async function getAdminAccessStatus() {
    await init();
    const user = state.currentUser;
    if (!user) return { signedIn: false, isAdmin: false, isSuperAdmin: false, needsSetup: false };

    const email = (user.email || '').toLowerCase();
    const uid = user.uid;

    if (!state.db) return { signedIn: true, isAdmin: false, isSuperAdmin: false, needsSetup: false };

    try {
      const adminDocRef = state.db.collection('settings').doc('admins');
      const snap = await adminDocRef.get();

      if (!snap.exists) {
        // First-time setup needed: recognize owner or admin email
        const isOwnerCandidate = false; // Bootstrap via claimFirstAdmin after sign-in
        return {
          signedIn: true,
          isAdmin: isOwnerCandidate,
          isSuperAdmin: isOwnerCandidate,
          needsSetup: true,
          role: isOwnerCandidate ? 'Super Admin' : 'None'
        };
      }

      const doc = snap.data();
      const uids = doc.uids || [];
      const emails = (doc.emails || []).map(e => String(e).toLowerCase());
      const superEmails = (doc.superEmails || []).map(e => String(e).toLowerCase());
      const primaryEmail = (doc.primaryEmail || '').toLowerCase();
      const primaryUid = doc.primaryUid || '';

      const isOwner = (uid && uid === primaryUid) || (email && email === primaryEmail);
      const isSuper = isOwner || superEmails.includes(email);
      const isAnyAdmin = isSuper || uids.includes(uid) || emails.includes(email);

      const roles = doc.roles || {};
      const userRole = roles[email] || roles[uid] || (isSuper ? 'Super Admin' : (isAnyAdmin ? 'Admin' : 'None'));

      return {
        signedIn: true,
        isAdmin: isAnyAdmin,
        isSuperAdmin: isSuper,
        isOwner: isOwner,
        needsSetup: false,
        role: userRole,
        primaryEmail: doc.primaryEmail,
        adminDoc: doc
      };
    } catch (err) {
      console.warn('getAdminAccessStatus error:', err);
      return { signedIn: true, isAdmin: false, isSuperAdmin: false, needsSetup: false, error: err.message };
    }
  }

  async function claimFirstAdmin(name) {
    await init();
    const user = state.currentUser;
    if (!user) throw new Error('Sign in first to claim Primary Admin role.');

    const email = (user.email || '').toLowerCase();
    const uid = user.uid;
    const adminDocRef = state.db.collection('settings').doc('admins');
    const snap = await adminDocRef.get().catch(() => ({ exists: false }));

    if (snap.exists) {
      throw new Error('Admin registry is already bootstrapped.');
    }

    const payload = {
      primaryUid: uid,
      primaryEmail: email,
      primaryName: name || user.displayName || 'Primary Super Admin',
      uids: [uid],
      emails: [email],
      superEmails: [email],
      roles: {
        [email]: 'Super Admin'
      },
      directory: [
        {
          uid: uid,
          email: email,
          name: name || user.displayName || 'Primary Super Admin',
          role: 'Super Admin',
          addedAt: new Date().toISOString(),
          isPrimary: true
        }
      ],
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp(),
      updatedAt: window.firebase.firestore.FieldValue.serverTimestamp()
    };

    await adminDocRef.set(payload, { merge: true });
    return { ok: true, role: 'Super Admin' };
  }

  // Preserve existing methods and export full suite
  window.ARYLIDE_FIREBASE = {
    init,
    signInEmail,
    signUpEmail,
    signInGoogle,
    startPhone,
    verifyPhone,
    saveUser,
    saveMeeting: bookMeetingCloud,
    updateMeeting: manageMeetingCloud,
    sendPasswordReset,
    signOut,
    getPublicCms,
    subscribePublicCms,
    getBookedSlots,
    bookMeetingCloud,
    manageMeetingCloud,
    getUserMeetings,
    submitLeadCloud,
    submitReferralCloud,
    submitAppointmentCloud,
    getAdminAccessStatus,
    claimFirstAdmin,
    get enabled() { return state.enabled; },
    get ready() { return state.ready; },
    get currentUser() { return state.currentUser; },
    get db() { return state.db; },
    get auth() { return state.auth; }
  };
})();
