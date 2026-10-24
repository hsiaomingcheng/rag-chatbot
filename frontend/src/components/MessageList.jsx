import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import SuggestedQuestions from './SuggestedQuestions'
import TypingIndicator from './TypingIndicator'

export default function MessageList({ messages, loading, onPickQuestion }) {
  const bottomRef = useRef(null)

  // Keep the newest message in view.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const showSuggestions = messages.length === 1

  return (
    <div className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
      {messages.map((message) => (
        <MessageBubble key={message.id} role={message.role} text={message.text} />
      ))}
      {showSuggestions && (
        <SuggestedQuestions onPick={onPickQuestion} disabled={loading} />
      )}
      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
