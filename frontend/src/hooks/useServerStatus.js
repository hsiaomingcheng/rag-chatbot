import { useEffect, useState } from 'react'
import { checkHealth } from '../api/chatApi'

const RETRY_DELAY_MS = 3000
const MAX_ATTEMPTS = 30 // about 90 seconds, longer than a typical cold start
const SHOW_WAKING_AFTER_MS = 1500 // a fast server never flashes the banner

/**
 * Pings the backend when the page opens and keeps retrying while it wakes up.
 * Returns 'checking' | 'waking' | 'ready' | 'unavailable'.
 */
export default function useServerStatus() {
  const [status, setStatus] = useState('checking')

  useEffect(() => {
    let cancelled = false

    const wakingTimer = setTimeout(() => {
      if (!cancelled) setStatus((s) => (s === 'checking' ? 'waking' : s))
    }, SHOW_WAKING_AFTER_MS)

    async function waitForServer() {
      for (let attempt = 0; attempt < MAX_ATTEMPTS && !cancelled; attempt++) {
        if (await checkHealth()) {
          if (!cancelled) setStatus('ready')
          return
        }
        await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY_MS))
      }
      if (!cancelled) setStatus('unavailable')
    }
    waitForServer()

    return () => {
      cancelled = true
      clearTimeout(wakingTimer)
    }
  }, [])

  return status
}
