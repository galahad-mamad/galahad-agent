// Galahad Agent — Session Dashboard (runtime plugin)
// Contributed route + sidebar row: live session/gateway snapshot.

import { host, Button, ScrollArea, Separator, useValue, cn } from '@galahad/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'

function Row({ label, value }) {
  return jsxs('div', {
    className: 'flex items-center justify-between gap-4 py-1.5',
    children: [
      jsx('span', { className: 'text-(--ui-text-tertiary) text-sm', children: label }),
      jsx('span', { className: 'font-mono text-sm', children: value ?? '—' })
    ]
  })
}

function Dashboard() {
  const gateway = useValue(host.state.gateway)
  const model = useValue(host.state.model)
  const profile = useValue(host.state.profile)
  const cwd = useValue(host.state.cwd)
  const sessionId = useValue(host.state.activeSessionId)

  return jsx(ScrollArea, {
    className: 'mx-auto h-full w-full max-w-2xl p-6',
    children: jsxs('div', {
      className: 'space-y-1',
      children: [
        jsx('h2', { className: 'mb-3 text-lg font-semibold', children: 'Galahad Session Dashboard' }),
        jsx(Row, { label: 'Gateway', value: gateway }),
        jsx(Separator, {}),
        jsx(Row, { label: 'Model', value: model }),
        jsx(Separator, {}),
        jsx(Row, { label: 'Profile', value: profile }),
        jsx(Separator, {}),
        jsx(Row, { label: 'Workspace', value: cwd || '(detached)' }),
        jsx(Separator, {}),
        jsx(Row, { label: 'Session', value: sessionId ?? '(draft)' }),
        jsx(Separator, {}),
        jsx('div', {
          className: 'mt-4 flex gap-2',
          children: jsx(Button, {
            size: 'sm',
            variant: 'outline',
            onClick: async () => {
              try {
                const s = await host.status()
                host.notify({ message: `Status: ${JSON.stringify(s?.platforms ?? s).slice(0, 160)}` })
              } catch (e) {
                host.notify({ message: `status failed: ${e?.message ?? e}`, tone: 'error' })
              }
            },
            children: 'Refresh system status'
          })
        })
      ]
    })
  })
}

export default {
  id: 'galahad-session-dashboard',
  name: 'Session Dashboard',
  register(ctx) {
    ctx.register({
      id: 'route',
      area: 'routes',
      title: 'Dashboard',
      data: { path: '/session-dashboard' },
      render: () => jsx(Dashboard, {})
    })
    ctx.register({
      id: 'nav',
      area: 'sidebar.nav',
      order: 90,
      data: { codicon: 'dashboard', label: 'Dashboard', path: '/session-dashboard' }
    })
  }
}
