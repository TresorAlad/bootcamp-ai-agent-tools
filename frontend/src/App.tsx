import { useEffect, useRef, useState } from 'react'
import './App.css'
import {
  createConversation,
  createNote,
  getMessages,
  listConversations,
  listModels,
  sendMessageStream,
  type ConversationSummary,
  type TokenUsage,
} from './api'
import ChatWindow, { type ChatMessage } from './components/ChatWindow'
import Sidebar from './components/Sidebar'

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Une erreur est survenue.'
}

export default function App() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [activeId, setActiveId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [models, setModels] = useState<string[]>([])
  const [selectedModel, setSelectedModel] = useState('')
  const [noteMode, setNoteMode] = useState(false)
  const [canRetry, setCanRetry] = useState(false)
  const lastFailedMessage = useRef<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    Promise.all([listConversations(), listModels()])
      .then(([list, { models: allowed, default: defaultModel }]) => {
        setConversations(list)
        setModels(allowed)
        setSelectedModel(defaultModel)
        if (list.length > 0) setActiveId(list[0].id)
      })
      .catch((err) => setError(errorMessage(err)))
  }, [])

  useEffect(() => {
    if (activeId === null) return
    let cancelled = false
    getMessages(activeId)
      .then((list) => {
        if (!cancelled) {
          setMessages(list.map(({ role, content }) => ({ role, content })))
          setCanRetry(false)
          lastFailedMessage.current = null
        }
      })
      .catch((err) => !cancelled && setError(errorMessage(err)))
    return () => {
      cancelled = true
    }
  }, [activeId])

  function selectConversation(id: number) {
    if (loading || id === activeId) return
    abortRef.current?.abort()
    setError(null)
    setDraft('')
    setMessages([])
    setCanRetry(false)
    setActiveId(id)
  }

  async function handleNew() {
    if (loading) return
    setError(null)
    try {
      const id = await createConversation()
      setConversations((list) => [
        { id, created_at: new Date().toISOString(), preview: null },
        ...list,
      ])
      setDraft('')
      setMessages([])
      setCanRetry(false)
      setActiveId(id)
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  async function runChat(text: string, isFirstMessage: boolean) {
    if (activeId === null) return
    setCanRetry(false)
    lastFailedMessage.current = null
    setLoading(true)

    setMessages((list) => [
      ...list,
      { role: 'user', content: text },
      { role: 'assistant', content: '', streaming: true },
    ])

    const controller = new AbortController()
    abortRef.current = controller

    let failed = false

    try {
      await sendMessageStream(activeId, text, selectedModel, {
        signal: controller.signal,
        onDelta: (chunk) => {
          setMessages((list) =>
            list.map((m, i) =>
              i === list.length - 1 && m.role === 'assistant'
                ? { ...m, content: m.content + chunk, streaming: true }
                : m,
            ),
          )
        },
        onTool: (event) => {
          const name = event.name ?? 'outil'
          if (event.status === 'running') {
            setMessages((list) => [
              ...list.filter((m) => m.role !== 'tool-status'),
              {
                role: 'tool-status',
                content: `Outil en cours : ${name}…`,
                toolName: name,
              },
            ])
          }
          if (event.status === 'done') {
            setMessages((list) => list.filter((m) => m.role !== 'tool-status'))
          }
        },
        onDone: ({ notification, usage }) => {
          setMessages((list) =>
            list.map((m, i) =>
              i === list.length - 1 && m.role === 'assistant'
                ? { ...m, streaming: false, usage: usage as TokenUsage | null }
                : m,
            ),
          )
          if (notification) {
            setMessages((list) => [
              ...list,
              { role: 'system-notification', content: notification },
            ])
          }
        },
        onError: (detail) => {
          failed = true
          setMessages((list) => list.slice(0, -2))
          setDraft(text)
          lastFailedMessage.current = text
          setCanRetry(true)
          setError(detail)
        },
      })

      if (!failed && !controller.signal.aborted && isFirstMessage) {
        setConversations(await listConversations())
      }
    } catch (err) {
      setMessages((list) => list.slice(0, -2))
      setDraft(text)
      lastFailedMessage.current = text
      setCanRetry(true)
      setError(errorMessage(err))
    } finally {
      setLoading(false)
      abortRef.current = null
    }
  }

  async function handleSend() {
    if (activeId === null) return
    const text = draft.trim()
    const isFirstMessage = messages.length === 0
    setError(null)
    setDraft('')

    if (!noteMode && !selectedModel) {
      setError('Aucun modèle disponible. Vérifiez que le backend tourne et GET /models.')
      setDraft(text)
      return
    }

    if (noteMode) {
      setLoading(true)
      try {
        const note = await createNote(activeId, text)
        setMessages((list) => [...list, { role: note.role, content: note.content }])
        if (isFirstMessage) setConversations(await listConversations())
      } catch (err) {
        setDraft(text)
        setError(errorMessage(err))
      } finally {
        setLoading(false)
      }
      return
    }

    await runChat(text, isFirstMessage)
  }

  function handleStop() {
    abortRef.current?.abort()
    setMessages((list) => {
      const withoutPartial = list.slice(0, -2)
      const lastUser = list[list.length - 2]
      if (lastUser?.role === 'user') setDraft(lastUser.content)
      return withoutPartial
    })
    setLoading(false)
    setError('Génération interrompue : rien n’a été enregistré côté serveur.')
  }

  function handleRetry() {
    const text = lastFailedMessage.current ?? draft.trim()
    if (!text || activeId === null) return
    setDraft('')
    setError(null)
    void runChat(text, messages.length === 0)
  }

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={handleNew}
      />
      <main className="main">
        {error && (
          <div className="error" role="alert">
            {error}
            <button onClick={() => setError(null)} aria-label="Fermer">
              ×
            </button>
          </div>
        )}
        {activeId === null ? (
          <div className="empty">
            <p>Aucune conversation ouverte.</p>
            <button className="new-button" onClick={handleNew}>
              + Nouvelle conversation
            </button>
          </div>
        ) : (
          <ChatWindow
            messages={messages}
            loading={loading}
            draft={draft}
            models={models}
            selectedModel={selectedModel}
            noteMode={noteMode}
            canRetry={canRetry}
            onDraftChange={setDraft}
            onModelChange={setSelectedModel}
            onNoteModeChange={setNoteMode}
            onSend={() => void handleSend()}
            onStop={handleStop}
            onRetry={handleRetry}
          />
        )}
      </main>
    </div>
  )
}
