console.log('[React App] App.jsx mounted');



import React, { useState } from 'react';

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

  function validateEmail(email) {
    return /.+@.+\..+/.test(email);
  }

  function handleRegister(e) {
    e.preventDefault();
    if (!validateEmail(regEmail)) {
      setRegMsg('Invalid email');
      return;
    }
    if (!regPassword || !regFullName) {
      setRegMsg('All fields required');
      return;
    }
    setRegMsg('Registration successful');
    setView('login');
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
        <form onSubmit={handleRegister}>
          <h2>Register</h2>
          <input
            type="email"
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
          <button type="submit">Register</button>
          {regMsg && <div>{regMsg}</div>}
        </form>
      )}
      {view === 'login' && (
        <form onSubmit={handleLogin}>
          <h2>Login</h2>
          <input
            type="email"
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
          <button type="submit">Login</button>
          {loginMsg && <div>{loginMsg}</div>}
        </form>
      )}
    </div>
  );
}

export default App;
