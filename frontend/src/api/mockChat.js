// Temporary fake backend for step 4-2. Step 4-3 replaces this with the real streaming API.
export function askQuestion(question) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(
        `(Demo reply) You asked: "${question}". The real answer will come from the backend in the next step.`,
      )
    }, 1500)
  })
}
