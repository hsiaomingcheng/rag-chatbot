import { useState } from 'react'
import { askQuestion } from './api/mockChat'
import ChatHeader from './components/ChatHeader'
import ChatInput from './components/ChatInput'
import MessageList from './components/MessageList'

const WELCOME = {
  id: 'welcome',
  role: 'assistant',
  text: "Hi! I'm an AI assistant that answers questions about Chris Hsiao using his CV. Try one of the questions below, or ask your own.",
}

export default function App() {
  const [messages, setMessages] = useState([WELCOME])
  const [loading, setLoading] = useState(false)

  const handleSend = async (question) => {
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', text: question },
    ])
    setLoading(true)
    const reply = await askQuestion(question)
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'assistant', text: reply },
    ])
    setLoading(false)
  }

  return (
    <div className="mx-auto flex h-full max-w-3xl flex-col bg-white dark:bg-slate-950">
      <ChatHeader />
      <MessageList
        messages={messages}
        loading={loading}
        onPickQuestion={handleSend}
      />
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  )
}
