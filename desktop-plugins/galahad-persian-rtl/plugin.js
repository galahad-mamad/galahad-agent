// Galahad Agent — Persian RTL (runtime plugin)
// Injects a Persian/RTL friendly stylesheet toggle + palette command.

import { host } from '@galahad/plugin-sdk'

const CSS = `
[data-galahad-rtl="on"] .message-content,
[data-galahad-rtl="on"] .composer-input,
[data-galahad-rtl="on"] textarea {
  direction: rtl;
  text-align: right;
  font-family: "Vazirmatn", "Segoe UI", Tahoma, sans-serif;
}
`

function applyRtl(on) {
  if (typeof document === 'undefined') return
  let style = document.getElementById('galahad-persian-rtl')
  if (!style) {
    style = document.createElement('style')
    style.id = 'galahad-persian-rtl'
    style.textContent = CSS
    document.head.appendChild(style)
  }
  if (on) document.documentElement.setAttribute('data-galahad-rtl', 'on')
  else document.documentElement.removeAttribute('data-galahad-rtl')
}

export default {
  id: 'galahad-persian-rtl',
  name: 'Persian RTL',
  register(ctx) {
    let on = ctx.storage.get('rtl', false)
    applyRtl(on)
    ctx.onDispose(() => applyRtl(false))
    ctx.register({
      id: 'toggle',
      area: 'palette',
      title: 'Persian RTL: toggle right-to-left text',
      run: () => {
        on = !on
        ctx.storage.set('rtl', on)
        applyRtl(on)
        host.notify({ message: on ? 'RTL فعال شد' : 'RTL خاموش شد' })
      }
    })
  }
}
