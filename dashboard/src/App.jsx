import { useState, useEffect } from 'react'
import WebhookStream from './components/WebhookStream'
import SubscriptionList from './components/SubscriptionList'

function App() {
  const [activeTab, setActiveTab] = useState('stream')

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-50 font-sans">
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center font-bold text-xl">W</div>
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                Webhook platform Engine
              </span>
            </div>
            <div className="flex gap-4">
              <button 
                onClick={() => setActiveTab('stream')}
                className={`px-4 py-2 rounded-md transition-all ${activeTab === 'stream' ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/50' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Log Stream
              </button>
              <button 
                onClick={() => setActiveTab('subs')}
                className={`px-4 py-2 rounded-md transition-all ${activeTab === 'subs' ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/50' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Subscriptions
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'stream' ? <WebhookStream /> : <SubscriptionList />}
      </main>
    </div>
  )
}

export default App
