import { useState, useEffect } from 'react'

export default function WebhookStream() {
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState('connecting')

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/stream')

    ws.onopen = () => setStatus('connected')
    ws.onclose = () => setStatus('disconnected')
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLogs(prev => [data, ...prev].slice(0, 50))
    }

    return () => ws.close()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold">Real-time Delivery Stream</h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-emerald-500' : 'bg-rose-500'} animate-pulse`}></div>
          <span className="text-sm text-slate-400 capitalize">{status}</span>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="grid grid-cols-6 gap-4 p-4 border-b border-slate-800 text-sm font-medium text-slate-400">
          <div className="col-span-1">Status</div>
          <div className="col-span-2">Event ID</div>
          <div className="col-span-1">Code</div>
          <div className="col-span-1">Attempt</div>
          <div className="col-span-1 text-right">Time</div>
        </div>
        
        <div className="divide-y divide-slate-800">
          {logs.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              Waiting for events... Ingest something via /api/v1/events to see it here.
            </div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="grid grid-cols-6 gap-4 p-4 text-sm items-center hover:bg-slate-800/50 transition-colors">
                <div className="col-span-1">
                  <span className={`px-2 py-1 rounded-md text-xs font-bold uppercase ${
                    log.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 
                    log.status === 'failed' || log.status === 'dlq' ? 'bg-rose-500/10 text-rose-400' : 
                    'bg-amber-500/10 text-amber-400'
                  }`}>
                    {log.status}
                  </span>
                </div>
                <div className="col-span-2 font-mono text-slate-300 truncate">{log.event_id}</div>
                <div className="col-span-1 font-mono text-slate-300">{log.response_code || '---'}</div>
                <div className="col-span-1 text-slate-300">#{log.attempt_number}</div>
                <div className="col-span-1 text-right text-slate-500 text-xs">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
