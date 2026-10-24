// Where the backend lives. Locally this is the FastAPI server; when deployed,
// set VITE_API_BASE_URL to the Render URL (see .env.example).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ChatError extends Error {}

async function readErrorMessage(response) {
  const fallback = 'Something went wrong. Please try again.'
  try {
    const body = await response.json()
    // The backend sends friendly text as a string; validation errors are lists.
    if (typeof body.detail === 'string') return body.detail
    if (response.status === 422) return 'Please keep your question between 1 and 500 characters.'
  } catch {
    // Response was not JSON; use the fallback below.
  }
  return fallback
}

/**
 * Ask a question and receive the answer piece by piece.
 * `onText` is called with each new piece of text as it arrives.
 */
export async function streamAnswer(question, onText) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })
  } catch {
    throw new ChatError(
      "Can't reach the server. It may be waking up (this can take up to a minute). Please try again shortly.",
    )
  }

  if (!response.ok) {
    throw new ChatError(await readErrorMessage(response))
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    // Server-Sent Events are separated by a blank line. The last piece may be
    // incomplete, so keep it in the buffer until more data arrives.
    const events = buffer.split('\n\n')
    buffer = events.pop()

    for (const rawEvent of events) {
      const line = rawEvent.trim()
      if (!line.startsWith('data:')) continue
      const payload = JSON.parse(line.slice(5).trim())
      if (payload.error) throw new ChatError(payload.error)
      if (payload.text) onText(payload.text)
    }
  }
}
