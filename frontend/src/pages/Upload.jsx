import { useState, useEffect } from 'react'
import api from '../api/axios'

const SOURCES = [
  { key: 'sap', label: 'SAP Fuel & Procurement', icon: '🏭', desc: 'CSV export from SAP (MB51/ME2M). Columns: PLANT, MATERIAL, QUANTITY, UNIT, POSTING_DATE, MATERIAL_DESC' },
  { key: 'utility', label: 'Utility Electricity', icon: '⚡', desc: 'Portal CSV export. Columns: METER_ID, SITE, PERIOD_START, PERIOD_END, CONSUMPTION_KWH' },
  { key: 'travel', label: 'Corporate Travel', icon: '✈️', desc: 'Concur/Navan CSV export. Columns: TRAVELER, TRAVEL_TYPE, ORIGIN, DESTINATION, TRAVEL_DATE, NIGHTS, DISTANCE_KM' },
]

export default function Upload() {
  const [clients, setClients] = useState([])
  const [clientId, setClientId] = useState('')
  const [newClient, setNewClient] = useState('')
  const [files, setFiles] = useState({})
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState({})

  useEffect(() => {
    api.get('/api/clients/').then(r => setClients(r.data))
  }, [])

  const createClient = async () => {
    if (!newClient.trim()) return
    const res = await api.post('/api/clients/', { name: newClient })
    setClients([...clients, res.data])
    setClientId(res.data.id)
    setNewClient('')
  }

  const handleUpload = async (sourceKey) => {
    if (!clientId) return alert('Please select a client first')
    if (!files[sourceKey]) return alert('Please select a file')

    setLoading(l => ({ ...l, [sourceKey]: true }))
    const form = new FormData()
    form.append('source_type', sourceKey)
    form.append('client_id', clientId)
    form.append('file', files[sourceKey])

    try {
      const res = await api.post('/api/ingest/', form)
      setResults(r => ({ ...r, [sourceKey]: { success: true, ...res.data } }))
    } catch (e) {
      setResults(r => ({ ...r, [sourceKey]: { success: false, error: e.response?.data?.error || 'Upload failed' } }))
    } finally {
      setLoading(l => ({ ...l, [sourceKey]: false }))
    }
  }

  return (
    <div className="page">
      <h1 style={{ marginBottom: '1.5rem' }}>Upload Data</h1>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Client</h3>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <select value={clientId} onChange={e => setClientId(e.target.value)} style={{ width: 'auto', marginBottom: 0 }}>
            <option value="">Select existing client</option>
            {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <span style={{ color: '#999' }}>or</span>
          <input
            placeholder="New client name"
            value={newClient}
            onChange={e => setNewClient(e.target.value)}
            style={{ marginBottom: 0 }}
          />
          <button className="btn btn-primary" onClick={createClient}>Create</button>
        </div>
      </div>

      <div className="upload-grid">
        {SOURCES.map(src => (
          <div key={src.key} className="upload-box">
            <h3>{src.icon} {src.label}</h3>
            <p>{src.desc}</p>
            <input
              type="file"
              accept=".csv"
              onChange={e => setFiles(f => ({ ...f, [src.key]: e.target.files[0] }))}
            />
            <button
              className="btn btn-primary"
              onClick={() => handleUpload(src.key)}
              disabled={loading[src.key]}
            >
              {loading[src.key] ? 'Uploading...' : 'Upload'}
            </button>
            {results[src.key] && (
              <div style={{ marginTop: '1rem', fontSize: '0.85rem' }}>
                {results[src.key].success
                  ? <span style={{ color: '#10b981' }}>✓ {results[src.key].rows_ingested} rows ingested, {results[src.key].errors} errors</span>
                  : <span style={{ color: '#ef4444' }}>✗ {results[src.key].error}</span>
                }
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}