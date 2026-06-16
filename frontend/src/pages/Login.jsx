import { useState } from 'react'

export default function Login({ setUser }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleLogin = async () => {
    try {
      const res = await fetch('https://breathe-esg-e40y.onrender.com/api/auth/login/',{
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (res.ok) {
        setUser(data.username)
      } else {
        setError(data.error || 'Login failed')
      }
    } catch {
      setError('Cannot connect to server')
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <h2>Digital Heroes</h2>
        <p>Built for Digital Heroes | Emissions Data Review Platform</p>
        {error && <div className="error">{error}</div>}
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleLogin()}
        />
        <button className="btn btn-primary" style={{ width: '100%' }} onClick={handleLogin}>
          Login
        </button>

        <div
  style={{
    marginTop: '20px',
    textAlign: 'center',
    fontSize: '14px'
  }}
>
  <p><strong>Built by:</strong> Jashan Jindal</p>
  <p><strong>Email: jashanjindal25@gmail.com </strong></p>

  <a
    href="https://digitalheroesco.com"
    target="_blank"
    rel="noopener noreferrer"
  >
    <a
  href="https://digitalheroesco.com"
  target="_blank"
  rel="noopener noreferrer"
  style={{
    display: "inline-block",
    marginTop: "12px",
    background: "#181834",
    color: "#ff0000",
    textDecoration: "none",
    padding: "12px 24px",
    borderRadius: "8px",
    fontWeight: "600",
    width: "220px",
    textAlign: "center"
  }}
>
  Built for Digital Heroes
</a>
  </a>
</div>
      </div>
    </div>
  )
}


