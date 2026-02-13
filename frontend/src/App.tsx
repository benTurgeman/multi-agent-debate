import { useState, useEffect } from 'react'

function App() {
  const [status, setStatus] = useState<string>('Loading...')

  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('Error connecting to backend'))
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Multi-Agent Debate System</h1>
      <p>Welcome to the debate platform</p>
      <div>
        <p>Backend status: <strong>{status}</strong></p>
      </div>
    </div>
  )
}

export default App
