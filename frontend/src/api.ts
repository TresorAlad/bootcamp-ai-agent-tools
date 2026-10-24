// Thin typed wrappers around the FastAPI backend (proxied under /api by Vite).

export type Role = 'user' | 'assistant' | 'system-notification' | 'note'

export interface ConversationSummary {
  id: number
  created_at: string
  preview: string | null
}

export interface Message {
  seq: number
  role: Role
  content: string
  created_at: string
}

export interface ModelsResponse {
  models: string[]
  default: string
}

export interface TokenUsage {
  prompt_tokens?: number
  completion_tokens?: number
  total_tokens?: number
}

export interface StreamDonePayload {
  notification: string | null
  usage: TokenUsage | null
}

type ToolEvent = {
  type: 'tool'
  name?: string
  status?: 'running' | 'done'
}

type StreamHandlers = {
  onDelta: (chunk: string) => void
  onTool?: (event: ToolEvent) => void
  onDone: (payload: StreamDonePayload) => void
  onError: (detail: string) => void
  signal?: AbortSignal
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new Error('Impossible de joindre le serveur.')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new Error(detail ?? `Erreur ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function listConversations(): Promise<ConversationSummary[]> {
  return request('/conversations')
}

export async function createConversation(): Promise<number> {
  const { conversation_id } = await request<{ conversation_id: number }>('/conversations', {
    method: 'POST',
  })
  return conversation_id
}

export function getMessages(conversationId: number): Promise<Message[]> {
  return request(`/conversations/${conversationId}/messages`)
}

export function listModels(): Promise<ModelsResponse> {
  return request('/models')
}

export function createNote(conversationId: number, content: string): Promise<Message> {
  return request(`/conversations/${conversationId}/notes`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}

export async function sendMessageStream(
  conversationId: number,
  message: string,
  model: string,
  handlers: StreamHandlers,
): Promise<void> {
  let response: Response
  try {
    response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: conversationId, message, model }),
      signal: handlers.signal,
    })
  } catch (err) {
    if (handlers.signal?.aborted) return
    throw new Error('Impossible de joindre le serveur.')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new Error(detail ?? `Erreur ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) throw new Error('Flux de réponse indisponible.')

  const decoder = new TextDecoder()
  let buffer = ''
  let streamFinished = false

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''

    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data: ')) continue
      const json = line.slice(6)
      try {
        const event = JSON.parse(json) as {
          type: string
          content?: string
          detail?: string
          notification?: string | null
          usage?: TokenUsage | null
          name?: string
          status?: 'running' | 'done'
        }
        if (event.type === 'delta' && event.content) handlers.onDelta(event.content)
        if (event.type === 'tool') handlers.onTool?.(event)
        if (event.type === 'done') {
          streamFinished = true
          handlers.onDone({
            notification: event.notification ?? null,
            usage: event.usage ?? null,
          })
        }
        if (event.type === 'error') {
          handlers.onError(event.detail ?? 'Erreur pendant la génération.')
          return
        }
      } catch {
        // Ignore malformed SSE chunks.
      }
    }
  }

  if (!streamFinished && !handlers.signal?.aborted) {
    handlers.onError('Le flux s’est terminé sans réponse complète.')
  }
}
