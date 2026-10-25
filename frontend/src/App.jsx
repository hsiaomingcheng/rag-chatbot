import { useState } from 'react'
import { ChatError, streamAnswer } from './api/chatApi'
import ChatHeader from './components/ChatHeader'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'
import ServerBanner from './components/ServerBanner'
import useServerStatus from './hooks/useServerStatus'

const WELCOME = {
  id: 'welcome',
  role: 'assistant',
  text: "Hi! I'm an AI assistant that answers questions about Chris Hsiao using his CV. Try one of the questions below, or ask your own.",
}

const GENERIC_ERROR = 'Something went wrong. Please try again.'

export default function App() {
  const [messages, setMessages] = useState([WELCOME])
  // idle: ready | waiting: sent, no text yet | streaming: answer arriving
  const [status, setStatus] = useState('idle')
  const serverStatus = useServerStatus()
  // Hold off sending while the server is still waking up.
  const blocked = status !== 'idle' || serverStatus === 'waking'

  const handleSend = async (question) => {
    const answerId = crypto.randomUUID()
    let answerStarted = false

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', text: question },
    ])
    setStatus('waiting')

    try {
      await streamAnswer(question, (piece) => {
        if (!answerStarted) {
          // First piece: create the answer bubble (this removes the typing dots).
          answerStarted = true
          setStatus('streaming')
          setMessages((prev) => [
            ...prev,
            { id: answerId, role: 'assistant', text: piece },
          ])
        } else {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === answerId ? { ...m, text: m.text + piece } : m,
            ),
          )
        }
      })
    } catch (error) {
      const message = error instanceof ChatError ? error.message : GENERIC_ERROR
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', text: message, isError: true },
      ])
    } finally {
      setStatus('idle')
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col bg-white dark:bg-slate-950">
      <ChatHeader />
      <ServerBanner serverStatus={serverStatus} />
      <MessageList
        messages={messages}
        showTyping={status === 'waiting'}
        busy={blocked}
        onPickQuestion={handleSend}
      />
      <ChatInput onSend={handleSend} disabled={blocked} />
    </div>
  )
}
