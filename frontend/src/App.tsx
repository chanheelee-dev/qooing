import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'

import { consumeSse } from './lib/sse'
import {
  type BabyInfo,
  exportProfile,
  importProfile,
  loadProfile,
  saveProfile,
} from './lib/profile'
import './styles.css'

interface WikiSummary {
  slug: string
  title: string
  description: string
}

interface WikiDocument extends WikiSummary {
  type: string
  body: string
  sources: string[]
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export default function App() {
  const [wikis, setWikis] = useState<WikiSummary[]>([])
  const [document, setDocument] = useState<WikiDocument | null>(null)
  const [profile, setProfile] = useState<BabyInfo>(() => loadProfile())
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [prompt, setPrompt] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/wiki')
      .then((response) => {
        if (!response.ok) throw new Error('Could not load wiki list')
        return response.json() as Promise<WikiSummary[]>
      })
      .then(setWikis)
      .catch((reason: unknown) => setError(String(reason)))
  }, [])

  async function openWiki(slug: string): Promise<void> {
    setError('')
    try {
      const response = await fetch(`/api/wiki/${slug}`)
      if (!response.ok) throw new Error('Could not load wiki document')
      setDocument((await response.json()) as WikiDocument)
    } catch (reason) {
      setError(String(reason))
    }
  }

  function updateProfile(field: keyof BabyInfo, value: string): void {
    const next = { ...profile, [field]: value }
    setProfile(next)
    saveProfile(next)
  }

  function downloadProfile(): void {
    const url = URL.createObjectURL(
      new Blob([exportProfile(profile)], { type: 'application/json' }),
    )
    const anchor = globalThis.document.createElement('a')
    anchor.href = url
    anchor.download = 'qooing-baby-profile.json'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  async function uploadProfile(file: File | undefined): Promise<void> {
    if (!file) return
    try {
      setProfile(importProfile(await file.text()))
      setError('')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Invalid profile file')
    }
  }

  async function send(): Promise<void> {
    const question = prompt.trim()
    if (!question || sending) return
    setPrompt('')
    setSending(true)
    setError('')
    setMessages((current) => [
      ...current,
      { role: 'user', content: question },
      { role: 'assistant', content: '' },
    ])
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ prompt: question, baby_info: profile }),
      })
      await consumeSse(response, ({ event, data }) => {
        const payload = data as { text?: string; message?: string }
        if (event === 'error') throw new Error(payload.message ?? 'Chat service failed')
        if (event !== 'delta' || !payload.text) return
        setMessages((current) => {
          const next = [...current]
          const last = next.at(-1)
          if (last?.role === 'assistant') {
            next[next.length - 1] = { ...last, content: last.content + payload.text }
          }
          return next
        })
      })
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Chat service failed')
    } finally {
      setSending(false)
    }
  }

  return (
    <main>
      <header><h1>qooing</h1></header>
      {error && <p role="alert">{error}</p>}
      <div className="panels">
        <section aria-label="Wiki explorer">
          <h2>Wiki</h2>
          {wikis.length === 0 && <p>No wiki documents.</p>}
          <ul>
            {wikis.map((wiki) => (
              <li key={wiki.slug}>
                <button type="button" onClick={() => void openWiki(wiki.slug)}>
                  {wiki.title}
                </button>
                <small>{wiki.description}</small>
              </li>
            ))}
          </ul>
          <article>{document ? <ReactMarkdown>{document.body}</ReactMarkdown> : <p>Select a document.</p>}</article>
        </section>

        <section aria-label="Chat">
          <h2>Chat</h2>
          <div aria-live="polite">
            {messages.length === 0 && <p>Ask a baby-care question.</p>}
            {messages.map((message, index) => (
              <p key={`${message.role}-${index}`}>
                <strong>{message.role}:</strong> {message.content || '…'}
              </p>
            ))}
          </div>
          <label htmlFor="prompt">Prompt</label>
          <textarea id="prompt" value={prompt} onChange={(event) => setPrompt(event.target.value)} />
          <button type="button" disabled={sending || !prompt.trim()} onClick={() => void send()}>
            {sending ? 'Sending…' : 'Send'}
          </button>
        </section>

        <section aria-label="Baby profile">
          <h2>Baby profile</h2>
          <label>Name<input maxLength={100} value={profile.name} onChange={(event) => updateProfile('name', event.target.value)} /></label>
          <label>Birth date<input type="date" value={profile.birth_date} onChange={(event) => updateProfile('birth_date', event.target.value)} /></label>
          <label>Notes<textarea maxLength={2000} value={profile.notes} onChange={(event) => updateProfile('notes', event.target.value)} /></label>
          <button type="button" onClick={downloadProfile}>Export</button>
          <label className="file-label">Import<input type="file" accept="application/json" onChange={(event) => void uploadProfile(event.target.files?.[0])} /></label>
        </section>
      </div>
    </main>
  )
}
