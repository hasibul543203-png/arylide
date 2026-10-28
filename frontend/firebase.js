/* Optional Firebase adapter. Configuration is intentionally blank until the owner supplies Firebase IDs. */
(function () {
  const cfg = window.CONFIG || {};
  const required = ['FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN', 'FIREBASE_PROJECT_ID', 'FIREBASE_APP_ID'];
  const state = { app: null, auth: null, db: null, ready: false, enabled: required.every(key => String(cfg[key] || '').trim()), loading: null, phoneConfirmation: null, recaptcha: null, currentUser: null, authStateReady: null, resolveAuthState: null };
  const SDK = 'https://www.gstatic.com/firebasejs/10.14.1/';
  function loadScript(name) {
    return new Promise((resolve, reject) => {
      if (document.querySelector('script[data-firebase-sdk="' + name + '"]')) { resolve(); return; }
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
        if (state.resolveAuthState) { state.resolveAuthState(state.currentUser); state.resolveAuthState = null; }
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
    const snap = await ref.get();
    await ref.set({
      uid: user.uid,
      name: name || user.displayName || (snap.exists ? snap.data().name : '') || '',
      email: user.email || '',
      phone: phone || user.phoneNumber || (snap.exists ? snap.data().phone : '') || '',
      createdAt: snap.exists ? snap.data().createdAt : window.firebase.firestore.FieldValue.serverTimestamp(),
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
    try { return await state.auth.signInWithPopup(provider); }
    catch (error) {
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
    if (state.phoneName && credential.user && !credential.user.displayName) await credential.user.updateProfile({ displayName: state.phoneName });
    await saveUser(credential.user, state.phoneName, phone);
    return credential;
  }
  async function saveMeeting(meeting) {
    if (!state.db || !state.currentUser) return false;
    await state.db.collection('meetings').doc(String(meeting.id)).set({
      ...meeting,
      uid: state.currentUser.uid,
      email: meeting.email || state.currentUser.email || '',
      status: meeting.status || 'Pending',
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
    return true;
  }
  async function updateMeeting(meetingId, patch) {
    if (!state.db || !state.currentUser) return false;
    await state.db.collection('meetings').doc(String(meetingId)).set({ ...patch, uid: state.currentUser.uid, updatedAt: window.firebase.firestore.FieldValue.serverTimestamp() }, { merge: true });
    return true;
  }
  async function signOut() { if (state.auth) await state.auth.signOut(); }
  window.ARYLIDE_FIREBASE = { init, signInEmail, signUpEmail, signInGoogle, startPhone, verifyPhone, saveUser, saveMeeting, updateMeeting, signOut, get enabled() { return state.enabled; }, get ready() { return state.ready; }, get currentUser() { return state.currentUser; } };
})();
