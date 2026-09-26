// Galahad Agent — Skill Manager (runtime plugin)
// Palette commands to list and reload skills through the gateway.

import { host } from '@galahad/plugin-sdk'

export default {
  id: 'galahad-skill-manager',
  name: 'Skill Manager',
  register(ctx) {
    ctx.register({
      id: 'list',
      area: 'palette',
      title: 'Skills: list installed skills',
      run: async () => {
        try {
          const res = await host.request('config.get', { key: 'skills.config' })
          const text = typeof res === 'string' ? res : JSON.stringify(res ?? {})
          host.notify({ message: `Skills: ${text.slice(0, 200)}` })
        } catch (e) {
          host.notify({ message: `skills list failed: ${e?.message ?? e}`, tone: 'error' })
        }
      }
    })
    ctx.register({
      id: 'open-folder',
      area: 'palette',
      title: 'Skills: open skills folder',
      run: () => {
        const home = host.state.cwd.get()
        ctx.os.revealPath(home ? `${home}/skills` : 'skills')
      }
    })
  }
}
