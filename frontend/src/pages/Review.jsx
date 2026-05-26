import { useEffect, useState } from 'react'
import api from '../api/axios'

export default function Review() {
  const [records, setRecords] = useState([])
  const [selected, setSelected] = useState(null)
  const [filters, setFilters] = useState({ status: '', scope: '', source_type: '' })
  const [auditLogs, setAuditLogs] = useState([])

  const fetchRecords = () => {
    const params = new URLSearchParams()
    if (filters.status) params.append('status', filters.status)
    if (filters.scope) params.append('scope', filters.scope)
    if (filters.source_type) params.append('source_type', filters.source_type)
    api.get(`/api/emissions/?${params}`).then(r => setRecords(r.data))
  }

  useEffect(() => { fetchRecords() }, [filters])

  const openDetail = async (record) => {
    setSelected(record)
    const logs = await api.get(`/api/emissions/${record.id}/audit/`)
    setAuditLogs(logs.data)
  }

  const approve = async (id) => {
    await api.post(`/api/emissions/${id}/approve/`)
    fetchRecords()
    setSelected(null)
  }

  const reject = async (id) => {
    await api.post(`/api/emissions/${id}/reject/`)
    fetchRecords()
    setSelected(null)
  }

  const badgeClass = (status) => {
    const map = { pending: 'pending', flagged: 'flagged', approved: 'approved', rejected: 'rejected', locked: 'locked' }
    return `badge ${map[status] || ''}`
  }

  return (
    <div className="page">
      <h1 style={{ marginBottom: '1.5rem' }}>Review Emissions</h1>

      <div className="filter-bar">
        <select value={filters.status} onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}>
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="flagged">Flagged</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <select value={filters.scope} onChange={e => setFilters(f => ({ ...f, scope: e.target.value }))}>
          <option value="">All Scopes</option>
          <option value="1">Scope 1</option>
          <option value="2">Scope 2</option>
          <option value="3">Scope 3</option>
        </select>
        <select value={filters.source_type} onChange={e => setFilters(f => ({ ...f, source_type: e.target.value }))}>
          <option value="">All Sources</option>
          <option value="sap">SAP</option>
          <option value="utility">Utility</option>
          <option value="travel">Travel</option>
        </select>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Scope</th>
              <th>Activity</th>
              <th>kgCO2e</th>
              <th>Period</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 && (
              <tr><td colSpan={8} style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>No records found</td></tr>
            )}
            {records.map(r => (
              <tr key={r.id}>
                <td>#{r.id}</td>
                <td>{r.category?.replace(/_/g, ' ')}</td>
                <td>Scope {r.scope}</td>
                <td>{r.activity_value} {r.activity_unit}</td>
                <td><strong>{r.normalized_kgco2e?.toFixed(2)}</strong></td>
                <td>{r.period_start}</td>
                <td><span className={badgeClass(r.review_status)}>{r.review_status}</span></td>
                <td>
                  <button className="btn btn-primary" style={{ fontSize: '0.75rem', padding: '4px 8px' }} onClick={() => openDetail(r)}>
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="detail-modal" onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <h3>Record #{selected.id}</h3>
              <button className="btn btn-primary" onClick={() => setSelected(null)}>✕ Close</button>
            </div>

            {[
              ['Category', selected.category?.replace(/_/g, ' ')],
              ['Scope', `Scope ${selected.scope}`],
              ['Activity', `${selected.activity_value} ${selected.activity_unit}`],
              ['Emissions', `${selected.normalized_kgco2e?.toFixed(4)} kgCO2e`],
              ['Emission Factor', `${selected.emission_factor} (${selected.emission_factor_source})`],
              ['Period', `${selected.period_start} → ${selected.period_end}`],
              ['Description', selected.description],
              ['Status', selected.review_status],
              ['Edited', selected.is_edited ? 'Yes' : 'No'],
            ].map(([k, v]) => (
              <div className="detail-row" key={k}>
                <span className="key">{k}</span>
                <span className="val">{v}</span>
              </div>
            ))}

            {selected.flags?.length > 0 && (
              <div style={{ marginTop: '1rem', background: '#fee2e2', borderRadius: 8, padding: '0.75rem' }}>
                <strong style={{ color: '#991b1b' }}>⚠ Flags</strong>
                {selected.flags.map(f => (
                  <div key={f.id} style={{ fontSize: '0.85rem', marginTop: 4 }}>{f.reason}: {f.detail}</div>
                ))}
              </div>
            )}

            {auditLogs.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <strong>Audit Log</strong>
                {auditLogs.map(l => (
                  <div key={l.id} style={{ fontSize: '0.8rem', color: '#666', marginTop: 4 }}>
                    {l.changed_at?.slice(0, 16)} — {l.field_name}: {l.old_value} → {l.new_value}
                  </div>
                ))}
              </div>
            )}

            {!selected.is_locked && (
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button className="btn btn-success" onClick={() => approve(selected.id)}>✓ Approve & Lock</button>
                <button className="btn btn-danger" onClick={() => reject(selected.id)}>✗ Reject</button>
              </div>
            )}
            {selected.is_locked && (
              <div style={{ marginTop: '1rem', color: '#1e40af', fontWeight: 600 }}>🔒 This record is locked</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}