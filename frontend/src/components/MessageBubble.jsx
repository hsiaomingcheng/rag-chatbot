export default function MessageBubble({ role, text, isError }) {
  const isUser = role === 'user'

  let style = 'rounded-bl-sm bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
  if (isUser) style = 'rounded-br-sm bg-indigo-600 text-white'
  if (isError) {
    style =
      'rounded-bl-sm border border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200'
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed sm:max-w-[75%] ${style}`}
      >
        {text}
      </div>
    </div>
  )
}
