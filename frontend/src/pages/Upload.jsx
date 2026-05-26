import { useState, useEffect } from 'react'
import api from '../api/axios'

const SOURCES = [
  { key: 'sap', label: 'SAP Fuel & Procurement', icon: '🏭', desc: 'CSV upload' },
  { key: 'utility', label: 'Utility Electricity', icon: '⚡', desc: 'CSV upload' },
  { key: 'travel', label: 'Corporate Travel', icon: '✈️', desc: 'CSV upload' },
]

export default function Upload() {
  const [clients, setClients] = useState([])
  const [clientId, setClientId] = useState('')
  const [newClient, setNewClient] = useState('')
  const [files, setFiles] = useState({})
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState({})

  useEffect(() => {
    api.get('/api/clients/')
      .then(r => {
        setClients(Array.isArray(r.data) ? r.data : [])
      })
      .catch(err => {
        console.error(err)
        setClients([])
      })
  }, [])

  const createClient = async () => {
    if (!newClient.trim()) return

    try {
      const res = await api.post('/api/clients/', { name: newClient })
      setClients(prev => [...prev, res.data])
      setClientId(res.data.id)
      setNewClient('')
    } catch (err) {
      console.error(err)
    }
  }

  const handleUpload = async (sourceKey) => {
    if (!clientId) return alert('Select client first')
    if (!files[sourceKey]) return alert('Select file first')

    setLoading(l => ({ ...l, [sourceKey]: true }))

    const form = new FormData()
    form.append('source_type', sourceKey)
    form.append('client_id', clientId)
    form.append('file', files[sourceKey])

    try {
      const res = await api.post('/api/ingest/', form)
      setResults(r => ({ ...r, [sourceKey]: { success: true, ...res.data } }))
    } catch (e) {
      setResults(r => ({
        ...r,
        [sourceKey]: {
          success: false,
          error: e.response?.data?.error || 'Upload failed'
        }
      }))
    } finally {
      setLoading(l => ({ ...l, [sourceKey]: false }))
    }
  }

  return (
    <div className="page">
      <h1>Upload Data</h1>

      <div className="card">
        <select value={clientId} onChange={e => setClientId(e.target.value)}>
          <option value="">Select existing client</option>
          {(clients || []).map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <input
          placeholder="New client"
          value={newClient}
          onChange={e => setNewClient(e.target.value)}
        />

        <button onClick={createClient}>Create</button>
      </div>

      <div className="upload-grid">
        {SOURCES.map(src => (
          <div key={src.key} className="upload-box">
            <h3>{src.label}</h3>

            <input
              type="file"
              accept=".csv"
              onChange={e =>
                setFiles(f => ({ ...f, [src.key]: e.target.files[0] }))
              }
            />

            <button
              onClick={() => handleUpload(src.key)}
              disabled={loading[src.key]}
            >
              {loading[src.key] ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}