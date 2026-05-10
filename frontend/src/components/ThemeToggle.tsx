import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'

/**
 * ThemeToggle — light/dark mode toggle with localStorage persistence.
 *
 * TODO (good first issue):
 *   - On mount, read `localStorage.getItem('theme')` and apply the class
 *     `dark` to `document.documentElement` if the stored value is "dark".
 *   - On toggle, flip the class and persist the new value to localStorage.
 *   - In tailwind.config.js set `darkMode: 'class'` so Tailwind's `dark:`
 *     variant is driven by the class on <html>.
 *   - Add `dark:` variants to Layout.tsx sidebar and main background so
 *     switching theme visibly changes the UI.
 *   - Acceptance criteria: toggling dark mode persists across page refreshes.
 */

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(() => {
    // TODO (good first issue): read initial value from localStorage
    return false
  })

  useEffect(() => {
    // TODO (good first issue): apply / remove `dark` class on documentElement
    // and persist to localStorage when isDark changes
  }, [isDark])

  return (
    <button
      type="button"
      onClick={() => setIsDark((d) => !d)}
      className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  )
}
