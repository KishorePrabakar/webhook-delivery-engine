import { useState, useEffect } from 'react'

export default function SubscriptionList() {
  const [subs, setSubs] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    event_type: '',
    target_url: '',
    secret_key: Math.random().toString(36).substring(7)
  })

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/subscriptions')
      .then(res => res.json())
      .then(data => setSubs(data))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch('http://localhost:8000/api/v1/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
    if (res.ok) {
      const newSub = await res.json()
      setSubs([newSub, ...subs])
      setShowForm(false)
      setFormData({
        event_type: '',
        target_url: '',
        secret_key: Math.random().toString(36).substring(7)
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold">Event Subscriptions</h2>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          {showForm ? 'Cancel' : '+ New Subscription'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-700 p-6 rounded-xl space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-sm font-medium text-slate-400">Event Type</label>
              <input 
                type="text" 
                required
                placeholder="e.g. user.created"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                value={formData.event_type}
                onChange={e => setFormData({...formData, event_type: e.target.value})}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-medium text-slate-400">Secret Key (for HMAC)</label>
              <input 
                type="text" 
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 font-mono text-xs focus:ring-2 focus:ring-indigo-500 outline-none"
                value={formData.secret_key}
                onChange={e => setFormData({...formData, secret_key: e.target.value})}
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-400">Target URL</label>
            <input 
              type="url" 
              required
              placeholder="https://webhook.site/..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
              value={formData.target_url}
              onChange={e => setFormData({...formData, target_url: e.target.value})}
            />
          </div>
          <button type="submit" className="w-full bg-indigo-600 py-3 rounded-lg font-bold hover:bg-indigo-700 transition-colors">
            Create Webhook
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subs.map(sub => (
          <div key={sub.id} className="bg-slate-900 border border-slate-800 p-6 rounded-xl hover:border-slate-700 transition-all group">
            <div className="flex justify-between items-start mb-4">
              <div className="bg-indigo-500/10 text-indigo-400 text-xs font-bold px-2 py-1 rounded uppercase tracking-wider">
                {sub.event_type}
              </div>
              <div className={`w-2 h-2 rounded-full ${sub.is_active ? 'bg-emerald-500' : 'bg-slate-700'}`}></div>
            </div>
            <h3 className="text-sm font-medium text-slate-300 mb-2 break-all">{sub.target_url}</h3>
            <p className="text-xs text-slate-500 mb-4 font-mono">Secret: {sub.secret_key.substring(0, 8)}***</p>
            <div className="flex gap-2">
               <button className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded transition-colors">Edit</button>
               <button className="text-xs bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 px-3 py-1.5 rounded transition-colors">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
