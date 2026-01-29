import React, { useState, useEffect } from 'react';

console.log('[React App] App.jsx mounted');

function App() {
  const [view, setView] = useState('home');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regFullName, setRegFullName] = useState('');
  const [regMsg, setRegMsg] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginMsg, setLoginMsg] = useState('');
  const [user, setUser] = useState(null);

  useEffect(() => {
    console.log('regMsg changed:', regMsg);
  }, [regMsg]);

  useEffect(() => {
    console.log('view changed:', view);
  }, [view]);

  function validateEmail(email) {
    return /.+@.+\..+/.test(email);
  }

  function handleRegister(e) {
    e.preventDefault();
    console.log('handleRegister called', { regEmail, regPassword, regFullName });
    if (!validateEmail(regEmail)) {
      console.log('Setting message: Invalid email');
      setRegMsg('Invalid email');
      return;
    }
    if (!regPassword || !regFullName) {
      console.log('Setting message: All fields required');
      setRegMsg('All fields required');
      return;
    }
    console.log('Setting message: Registration successful');
    setRegMsg('Registration successful');
    // Don't auto-switch view - let user see the success message
    // They can click Login button to proceed
  }

  function handleLogin(e) {
    e.preventDefault();
    if (loginEmail === regEmail && loginPassword === regPassword) {
      setUser({ name: regFullName });
      setLoginMsg('');
    } else {
      setLoginMsg('Invalid credentials');
    }
  }

  if (user) {
    return (
      <div>
        <h1>Welcome, {user.name}</h1>
        <button onClick={() => setUser(null)}>Logout</button>
      </div>
    );
  }

  return (
    <div>
      <h1>Welcome to Anantam Home Interior Design Collaboration App</h1>
      <p>Your collaborative platform for home design.</p>
      <div id="mount-check">[App Mounted]</div>
      <nav>
        <button onClick={() => setView('register')}>Register</button>
        <button onClick={() => setView('login')}>Login</button>
      </nav>
      {view === 'register' && (
        <div>
          <h2>Register</h2>
          <input
            type="text"
            name="email"
            placeholder="Email"
            value={regEmail}
            onChange={e => setRegEmail(e.target.value)}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={regPassword}
            onChange={e => setRegPassword(e.target.value)}
          />
          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={regFullName}
            onChange={e => setRegFullName(e.target.value)}
          />
          <button type="button" data-testid="register-submit-button" onClick={() => {
            console.log('Register button clicked!');
            const fakeEvent = { preventDefault: () => {} };
            handleRegister(fakeEvent);
          }}>Register</button>
          <div data-testid="registration-message" style={{ display: regMsg ? 'block' : 'none' }}>
            {regMsg || 'No message'}
          </div>
        </div>
      )}
      {view === 'login' && (
        <div>
          <h2>Login</h2>
          <input
            type="text"
            name="email"
            placeholder="Email"
            value={loginEmail}
            onChange={e => setLoginEmail(e.target.value)}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={loginPassword}
            onChange={e => setLoginPassword(e.target.value)}
          />
          <button type="button" data-testid="login-submit-button" onClick={() => {
            console.log('Login button clicked!');
            const fakeEvent = { preventDefault: () => {} };
            handleLogin(fakeEvent);
          }}>Login</button>
          <div data-testid="login-message" style={{ display: loginMsg ? 'block' : 'none' }}>
            {loginMsg || 'No message'}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
