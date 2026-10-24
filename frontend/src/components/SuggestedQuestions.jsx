const QUESTIONS = [
  'Which companies has Chris worked for?',
  'What is Chris studying?',
  'What are Chris’s technical skills?',
  'What did Chris do at Bravo Star?',
]

export default function SuggestedQuestions({ onPick, disabled }) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUESTIONS.map((question) => (
        <button
          key={question}
          type="button"
          disabled={disabled}
          onClick={() => onPick(question)}
          className="rounded-full border border-indigo-200 px-3 py-1.5 text-sm text-indigo-700 transition hover:bg-indigo-50 disabled:opacity-50 dark:border-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-950"
        >
          {question}
        </button>
      ))}
    </div>
  )
}
