import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import api from '../api/axios'

const COLORS = ['#1a1a2e', '#10b981', '#f59e0b']

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/api/dashboard/').then(r => setStats(r.data))
  }, [])

  if (!stats) return <div className="page">Loading...</div>

  const scopeData = stats.by_scope.map(s => ({
    name: `Scope ${s.scope}`,
    kgCO2e: Math.round(s.total_kgco2e || 0),
  }))

  const sourceData = stats.by_source.map(s => ({
    name: s.batch__source_type?.toUpperCase() || 'Unknown',
    kgCO2e: Math.round(s.total_kgco2e || 0),
  }))

  return (
    <div className="page">
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard</h1>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="number">{stats.total}</div>
          <div className="label">Total Records</div>
        </div>
        <div className="stat-card pending">
          <div className="number">{stats.pending}</div>
          <div className="label">Pending Review</div>
        </div>
        <div className="stat-card flagged">
          <div className="number">{stats.flagged}</div>
          <div className="label">Flagged</div>
        </div>
        <div className="stat-card approved">
          <div className="number">{stats.approved}</div>
          <div className="label">Approved</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.rejected}</div>
          <div className="label">Rejected</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Emissions by Scope (kgCO2e)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={scopeData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="kgCO2e">
                {scopeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Emissions by Source (kgCO2e)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={sourceData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="kgCO2e">
                {sourceData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}