import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate()

  const handleLogout = async () => {
    await api.post('/api/auth/logout/')
    setUser(null)
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div>
        <span style={{ fontWeight: 700, fontSize: '1.1rem', marginRight: '2rem' }}>
          🌿 Breathe ESG
        </span>
        <Link to="/">Dashboard</Link>
        <Link to="/upload">Upload Data</Link>
        <Link to="/review">Review</Link>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span style={{ fontSize: '0.9rem', color: '#aaa' }}>👤 {user}</span>
        <button className="btn btn-warning" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}