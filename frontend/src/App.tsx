import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState<string>('Loading...')

  // Enable dark mode by default
  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])

  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('Error connecting to backend'))
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 p-8">
      <h1 className="text-4xl font-bold mb-4">Multi-Agent Debate System</h1>
      <p className="text-slate-400 mb-6">Welcome to the debate platform</p>
      <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
        <p className="text-slate-300">
          Backend status: <strong className="text-pro">{status}</strong>
        </p>
      </div>
    </div>
  )
}

export default App
