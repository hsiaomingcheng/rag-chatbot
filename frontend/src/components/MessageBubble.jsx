import ReactMarkdown from 'react-markdown'

// Tailwind removes default list/paragraph styling, so give Markdown elements their look here.
const markdownComponents = {
  p: ({ node: _node, ...props }) => <p className="my-2 first:mt-0 last:mb-0" {...props} />,
  ul: ({ node: _node, ...props }) => (
    <ul className="my-2 list-disc space-y-1 pl-5 first:mt-0 last:mb-0" {...props} />
  ),
  ol: ({ node: _node, ...props }) => (
    <ol className="my-2 list-decimal space-y-1 pl-5 first:mt-0 last:mb-0" {...props} />
  ),
  strong: ({ node: _node, ...props }) => <strong className="font-semibold" {...props} />,
  a: ({ node: _node, ...props }) => (
    <a
      className="underline underline-offset-2"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),
  code: ({ node: _node, ...props }) => (
    <code className="rounded bg-slate-200 px-1 py-0.5 text-[0.85em] dark:bg-slate-700" {...props} />
  ),
}

export default function MessageBubble({ role, text, isError }) {
  const isUser = role === 'user'

  let style = 'rounded-bl-sm bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-slate-100'
  if (isUser) style = 'rounded-br-sm bg-indigo-600 text-white'
  if (isError) {
    style =
      'rounded-bl-sm border border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200'
  }

  // Only the assistant's answers are Markdown. What the visitor types stays plain text.
  const renderAsMarkdown = !isUser && !isError

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed sm:max-w-[75%] ${
          renderAsMarkdown ? '' : 'whitespace-pre-wrap'
        } ${style}`}
      >
        {renderAsMarkdown ? (
          <ReactMarkdown components={markdownComponents}>{text}</ReactMarkdown>
        ) : (
          text
        )}
      </div>
    </div>
  )
}
