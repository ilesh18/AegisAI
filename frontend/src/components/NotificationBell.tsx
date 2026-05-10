import { useState } from 'react'
import { Bell } from 'lucide-react'
import { Link } from 'react-router-dom'

/**
 * NotificationBell — nav bar bell icon with unread count badge and dropdown.
 *
 * TODO (good first issue — static UI):
 *   - Implement the bell icon button with a red badge showing `unreadCount`.
 *   - On click, toggle a dropdown showing the last 5 notifications (use
 *     hardcoded dummy data for now).
 *   - Each row should show: title, short message snippet, timestamp.
 *   - Add a "View all" link pointing to "/notifications".
 *   - Acceptance criteria: clicking the bell opens/closes the dropdown.
 *
 * TODO (help wanted — API wiring):
 *   - Use useQuery to poll GET /api/v1/notifications?unread_only=true every
 *     60 seconds to keep the badge count fresh.
 *   - Clicking a notification row marks it as read via POST /notifications/read.
 *   - Acceptance criteria: unread badge count decrements when a notification
 *     is clicked.
 */

interface NotificationPreview {
  id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
}

// TODO (help wanted): replace with real API data via useQuery
const DUMMY_PREVIEWS: NotificationPreview[] = []

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)

  // TODO (help wanted): derive from real query data
  const unreadCount = DUMMY_PREVIEWS.filter((n) => !n.is_read).length

  return (
    <div className="relative">
      {/* Bell button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="relative p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
      >
        <Bell className="w-5 h-5" />
        {/* TODO (good first issue): show badge only when unreadCount > 0 */}
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl border border-gray-200 shadow-lg z-50">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900 text-sm">Notifications</h3>
          </div>

          {/* TODO (good first issue): map over DUMMY_PREVIEWS (or real data) here */}
          <div className="p-4 text-center text-sm text-gray-400">
            No notifications yet
          </div>

          <div className="p-3 border-t border-gray-100">
            <Link
              to="/notifications"
              className="block text-center text-sm text-primary-600 hover:text-primary-700"
              onClick={() => setIsOpen(false)}
            >
              View all notifications
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
