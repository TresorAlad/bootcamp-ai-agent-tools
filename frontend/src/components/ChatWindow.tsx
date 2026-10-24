import { useEffect, useRef, type FormEvent, type KeyboardEvent } from 'react'
import Markdown from 'react-markdown'
import type { Role, TokenUsage } from '../api'

export interface ChatMessage {
  role: Role | 'tool-status'
  content: string
  usage?: TokenUsage | null
  streaming?: boolean
  toolName?: string
}

interface ChatWindowProps {
  messages: ChatMessage[]
  loading: boolean
  draft: string
  models: string[]
  selectedModel: string
  noteMode: boolean
  canRetry: boolean
  onDraftChange: (value: string) => void
  onModelChange: (model: string) => void
  onNoteModeChange: (value: boolean) => void
  onSend: () => void
  onStop: () => void
  onRetry: () => void
}

export default function ChatWindow({
  messages,
  loading,
  draft,
  models,
  selectedModel,
  noteMode,
  canRetry,
  onDraftChange,
  onModelChange,
  onNoteModeChange,
  onSend,
  onStop,
  onRetry,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!loading && draft.trim()) onSend()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) handleSubmit(event)
  }

  return (
    <section className="chat">
      <header className="chat-toolbar">
        <label className="model-select">
          <span>Modèle</span>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={loading || models.length === 0}
          >
            {models.length === 0 ? (
              <option value="">Chargement…</option>
            ) : (
              models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))
            )}
          </select>
        </label>
        <label className="note-toggle">
          <input
            type="checkbox"
            checked={noteMode}
            onChange={(e) => onNoteModeChange(e.target.checked)}
            disabled={loading}
          />
          Note personnelle (non envoyée au LLM)
        </label>
        {canRetry && (
          <button type="button" className="retry-button" onClick={onRetry} disabled={loading}>
            Réessayer le dernier message
          </button>
        )}
      </header>

      <div className="messages">
        {messages.length === 0 && !loading && (
          <p className="muted center">
            Pose une question : météo, actualités, calendrier, emails, Notion, Drive…
          </p>
        )}
        {messages.map((m, i) => {
          if (m.role === 'system-notification') {
            return (
              <div key={i} className="notification">
                {m.content}
              </div>
            )
          }
          if (m.role === 'note') {
            return (
              <div key={i} className="note-bubble">
                <span className="note-label">Note</span>
                <p>{m.content}</p>
              </div>
            )
          }
          if (m.role === 'tool-status') {
            return (
              <div key={i} className="tool-status">
                {m.content}
              </div>
            )
          }
          return (
            <div key={i} className={`bubble ${m.role}${m.streaming ? ' streaming' : ''}`}>
              {m.role === 'assistant' ? <Markdown>{m.content || '…'}</Markdown> : m.content}
              {m.role === 'assistant' && m.usage?.total_tokens != null && (
                <p className="usage">
                  Tokens : {m.usage.total_tokens}
                  {m.usage.prompt_tokens != null && m.usage.completion_tokens != null
                    ? ` (prompt ${m.usage.prompt_tokens}, réponse ${m.usage.completion_tokens})`
                    : ''}
                </p>
              )}
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          value={draft}
          onChange={(e) => onDraftChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            noteMode
              ? 'Écris une note visible dans le fil mais jamais envoyée à l’agent…'
              : 'Demande une action ou pose une question…'
          }
          rows={2}
          disabled={loading}
          autoFocus
        />
        {loading ? (
          <button type="button" className="stop-button" onClick={onStop}>
            Arrêter
          </button>
        ) : (
          <button
            type="submit"
            disabled={!draft.trim() || (!noteMode && !selectedModel)}
          >
            {noteMode ? 'Enregistrer la note' : 'Envoyer'}
          </button>
        )}
      </form>
    </section>
  )
}
