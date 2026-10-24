import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import SuggestedQuestions from './SuggestedQuestions'
import TypingIndicator from './TypingIndicator'

export default function MessageList({ messages, showTyping, busy, onPickQuestion }) {
  const bottomRef = useRef(null)

  // Keep the newest text in view while the answer streams in.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, showTyping])

  const showSuggestions = messages.length === 1

  return (
    <div className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          role={message.role}
          text={message.text}
          isError={message.isError}
        />
      ))}
      {showSuggestions && (
        <SuggestedQuestions onPick={onPickQuestion} disabled={busy} />
      )}
      {showTyping && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
