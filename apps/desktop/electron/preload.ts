import { contextBridge, ipcRenderer, webUtils } from 'electron'

contextBridge.exposeInMainWorld('galahadDesktop', {
  getConnection: profile => ipcRenderer.invoke('galahad:connection', profile),
  revalidateConnection: () => ipcRenderer.invoke('galahad:connection:revalidate'),
  touchBackend: profile => ipcRenderer.invoke('galahad:backend:touch', profile),
  getGatewayWsUrl: profile => ipcRenderer.invoke('galahad:gateway:ws-url', profile),
  openSessionWindow: (sessionId, opts) => ipcRenderer.invoke('galahad:window:openSession', sessionId, opts),
  openWindow: () => ipcRenderer.invoke('galahad:window:openInstance'),
  claimAmbientCue: key => ipcRenderer.invoke('galahad:ambient:claim', key),
  wakeIndicator: {
    getState: () => ipcRenderer.invoke('galahad:wake-indicator:get'),
    setState: state => ipcRenderer.send('galahad:wake-indicator:set', state),
    onState: callback => {
      const listener = (_event, state) => callback(state)
      ipcRenderer.on('galahad:wake-indicator:state', listener)

      return () => ipcRenderer.removeListener('galahad:wake-indicator:state', listener)
    }
  },
  petOverlay: {
    // Main renderer → main process: window lifecycle + drag. `request` is
    // `{ bounds, screen }`; resolves with the screen bounds it actually used.
    open: request => ipcRenderer.invoke('galahad:pet-overlay:open', request),
    close: () => ipcRenderer.invoke('galahad:pet-overlay:close'),
    setBounds: bounds => ipcRenderer.send('galahad:pet-overlay:set-bounds', bounds),
    setIgnoreMouse: ignore => ipcRenderer.send('galahad:pet-overlay:ignore-mouse', ignore),
    // Flip the overlay focusable (and focus it) while the composer needs keys.
    setFocusable: focusable => ipcRenderer.send('galahad:pet-overlay:set-focusable', focusable),
    // Main renderer → overlay (forwarded by main): push the latest pet state.
    pushState: payload => ipcRenderer.send('galahad:pet-overlay:state', payload),
    // Overlay → main renderer (forwarded by main): pop back in / composer submit.
    control: payload => ipcRenderer.send('galahad:pet-overlay:control', payload),
    // Overlay subscribes to state pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:pet-overlay:state', listener)

      return () => ipcRenderer.removeListener('galahad:pet-overlay:state', listener)
    },
    // Main renderer subscribes to overlay control messages.
    onControl: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:pet-overlay:control', listener)

      return () => ipcRenderer.removeListener('galahad:pet-overlay:control', listener)
    }
  },
  // Quick Entry: the global-hotkey mini composer window. Main owns the OS
  // shortcut + the persisted preference; the quick window only captures text
  // and hands it back, and the primary renderer submits it through the normal
  // prompt path.
  quickEntry: {
    getSettings: () => ipcRenderer.invoke('galahad:quick-entry:settings:get'),
    setSettings: patch => ipcRenderer.invoke('galahad:quick-entry:settings:set', patch),
    submit: payload => ipcRenderer.send('galahad:quick-entry:submit', payload),
    dismiss: () => ipcRenderer.send('galahad:quick-entry:dismiss'),
    // Primary renderer → main → quick window: gateway connection state + the
    // recent-session options the target picker offers. Main caches the latest
    // payload so a freshly spawned quick window starts from truth.
    pushState: payload => ipcRenderer.send('galahad:quick-entry:state', payload),
    // Quick window subscribes to those pushes.
    onState: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:quick-entry:state', listener)

      return () => ipcRenderer.removeListener('galahad:quick-entry:state', listener)
    },
    // Main → primary renderer: a submit captured by the quick window.
    onSubmit: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:quick-entry:submit', listener)

      return () => ipcRenderer.removeListener('galahad:quick-entry:submit', listener)
    },
    // Main → quick window: you were just summoned (reset draft + refocus).
    onShown: callback => {
      const listener = () => callback()
      ipcRenderer.on('galahad:quick-entry:shown', listener)

      return () => ipcRenderer.removeListener('galahad:quick-entry:shown', listener)
    }
  },
  getBootProgress: () => ipcRenderer.invoke('galahad:boot-progress:get'),
  getConnectionConfig: profile => ipcRenderer.invoke('galahad:connection-config:get', profile),
  saveConnectionConfig: payload => ipcRenderer.invoke('galahad:connection-config:save', payload),
  applyConnectionConfig: payload => ipcRenderer.invoke('galahad:connection-config:apply', payload),
  testConnectionConfig: payload => ipcRenderer.invoke('galahad:connection-config:test', payload),
  sshConfigHosts: () => ipcRenderer.invoke('galahad:ssh-config:hosts'),
  sshResolveHost: host => ipcRenderer.invoke('galahad:ssh-config:resolve', host),
  probeConnectionConfig: remoteUrl => ipcRenderer.invoke('galahad:connection-config:probe', remoteUrl),
  oauthLoginConnectionConfig: remoteUrl => ipcRenderer.invoke('galahad:connection-config:oauth-login', remoteUrl),
  oauthLogoutConnectionConfig: remoteUrl => ipcRenderer.invoke('galahad:connection-config:oauth-logout', remoteUrl),
  // Galahad Cloud: one portal login powers discovery + silent per-agent sign-in
  // (cloud-auto-discovery Phase 3).
  cloud: {
    status: () => ipcRenderer.invoke('galahad:cloud:status'),
    login: () => ipcRenderer.invoke('galahad:cloud:login'),
    logout: () => ipcRenderer.invoke('galahad:cloud:logout'),
    discover: org => ipcRenderer.invoke('galahad:cloud:discover', org),
    agentSignIn: dashboardUrl => ipcRenderer.invoke('galahad:cloud:agent-sign-in', dashboardUrl)
  },
  profile: {
    get: () => ipcRenderer.invoke('galahad:profile:get'),
    set: name => ipcRenderer.invoke('galahad:profile:set', name)
  },
  api: request => ipcRenderer.invoke('galahad:api', request),
  notify: payload => ipcRenderer.invoke('galahad:notify', payload),
  requestMicrophoneAccess: () => ipcRenderer.invoke('galahad:requestMicrophoneAccess'),
  readFileDataUrl: filePath => ipcRenderer.invoke('galahad:readFileDataUrl', filePath),
  readFileDataUrlForAttach: filePath => ipcRenderer.invoke('galahad:readFileDataUrlForAttach', filePath),
  dataUrlReadMax: {
    get: () => ipcRenderer.invoke('galahad:data-url-read-max:get'),
    set: maxMb => ipcRenderer.invoke('galahad:data-url-read-max:set', maxMb)
  },
  readFileText: filePath => ipcRenderer.invoke('galahad:readFileText', filePath),
  selectPaths: options => ipcRenderer.invoke('galahad:selectPaths', options),
  selectSavePath: options => ipcRenderer.invoke('galahad:selectSavePath', options),
  writeClipboard: text => ipcRenderer.invoke('galahad:writeClipboard', text),
  readClipboard: () => ipcRenderer.invoke('galahad:readClipboard'),
  saveImageFromUrl: url => ipcRenderer.invoke('galahad:saveImageFromUrl', url),
  saveImageBuffer: (data, ext) => ipcRenderer.invoke('galahad:saveImageBuffer', { data, ext }),
  saveClipboardImage: () => ipcRenderer.invoke('galahad:saveClipboardImage'),
  getPathForFile: file => {
    try {
      return webUtils.getPathForFile(file) || ''
    } catch {
      return ''
    }
  },
  normalizePreviewTarget: (target, baseDir) => ipcRenderer.invoke('galahad:normalizePreviewTarget', target, baseDir),
  watchPreviewFile: url => ipcRenderer.invoke('galahad:watchPreviewFile', url),
  watchDirectory: dir => ipcRenderer.invoke('galahad:watchDirectory', dir),
  stopPreviewFileWatch: id => ipcRenderer.invoke('galahad:stopPreviewFileWatch', id),
  setActiveWork: payload => ipcRenderer.send('galahad:active-work', payload),
  setTitleBarTheme: payload => ipcRenderer.send('galahad:titlebar-theme', payload),
  setNativeTheme: mode => ipcRenderer.send('galahad:native-theme', mode),
  setTranslucency: payload => ipcRenderer.send('galahad:translucency', payload),
  setKeepAwake: on => ipcRenderer.send('galahad:keep-awake', on),
  setPreviewShortcutActive: active => ipcRenderer.send('galahad:previewShortcutActive', Boolean(active)),
  openExternal: url => ipcRenderer.invoke('galahad:openExternal', url),
  openPreviewInBrowser: url => ipcRenderer.invoke('galahad:openPreviewInBrowser', url),
  fetchLinkTitle: url => ipcRenderer.invoke('galahad:fetchLinkTitle', url),
  sanitizeWorkspaceCwd: cwd => ipcRenderer.invoke('galahad:workspace:sanitize', cwd),
  settings: {
    getDefaultProjectDir: () => ipcRenderer.invoke('galahad:setting:defaultProjectDir:get'),
    setDefaultProjectDir: dir => ipcRenderer.invoke('galahad:setting:defaultProjectDir:set', dir),
    pickDefaultProjectDir: () => ipcRenderer.invoke('galahad:setting:defaultProjectDir:pick')
  },
  zoom: {
    // Current zoom of this window, as { level, percent }.
    get: () => ipcRenderer.invoke('galahad:zoom:get'),
    setPercent: percent => ipcRenderer.send('galahad:zoom:set-percent', percent),
    // Fires on every zoom change, including the Ctrl/Cmd +/-/0 shortcuts,
    // so the settings UI can stay in sync with the keyboard.
    onChanged: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:zoom:changed', listener)

      return () => ipcRenderer.removeListener('galahad:zoom:changed', listener)
    }
  },
  revealLogs: () => ipcRenderer.invoke('galahad:logs:reveal'),
  getRecentLogs: () => ipcRenderer.invoke('galahad:logs:recent'),
  readDir: dirPath => ipcRenderer.invoke('galahad:fs:readDir', dirPath),
  gitRoot: startPath => ipcRenderer.invoke('galahad:fs:gitRoot', startPath),
  revealPath: targetPath => ipcRenderer.invoke('galahad:fs:reveal', targetPath),
  openDir: dirPath => ipcRenderer.invoke('galahad:fs:openDir', dirPath),
  desktopPluginsRoot: () => ipcRenderer.invoke('galahad:fs:desktopPluginsRoot'),
  renamePath: (targetPath, newName) => ipcRenderer.invoke('galahad:fs:rename', targetPath, newName),
  writeTextFile: (filePath, content) => ipcRenderer.invoke('galahad:fs:writeText', filePath, content),
  trashPath: targetPath => ipcRenderer.invoke('galahad:fs:trash', targetPath),
  git: {
    worktreeList: repoPath => ipcRenderer.invoke('galahad:git:worktreeList', repoPath),
    worktreeAdd: (repoPath, options) => ipcRenderer.invoke('galahad:git:worktreeAdd', repoPath, options),
    worktreeRemove: (repoPath, worktreePath, options) =>
      ipcRenderer.invoke('galahad:git:worktreeRemove', repoPath, worktreePath, options),
    branchSwitch: (repoPath, branch) => ipcRenderer.invoke('galahad:git:branchSwitch', repoPath, branch),
    branchList: repoPath => ipcRenderer.invoke('galahad:git:branchList', repoPath),
    baseBranchList: repoPath => ipcRenderer.invoke('galahad:git:baseBranchList', repoPath),
    repoStatus: repoPath => ipcRenderer.invoke('galahad:git:repoStatus', repoPath),
    fileDiff: (repoPath, filePath) => ipcRenderer.invoke('galahad:git:fileDiff', repoPath, filePath),
    scanRepos: (roots, options) => ipcRenderer.invoke('galahad:git:scanRepos', roots, options),
    review: {
      list: (repoPath, scope, baseRef) => ipcRenderer.invoke('galahad:git:review:list', repoPath, scope, baseRef),
      diff: (repoPath, filePath, scope, baseRef, staged) =>
        ipcRenderer.invoke('galahad:git:review:diff', repoPath, filePath, scope, baseRef, staged),
      stage: (repoPath, filePath) => ipcRenderer.invoke('galahad:git:review:stage', repoPath, filePath),
      unstage: (repoPath, filePath) => ipcRenderer.invoke('galahad:git:review:unstage', repoPath, filePath),
      revert: (repoPath, filePath) => ipcRenderer.invoke('galahad:git:review:revert', repoPath, filePath),
      revParse: (repoPath, ref) => ipcRenderer.invoke('galahad:git:review:revParse', repoPath, ref),
      commit: (repoPath, message, push) => ipcRenderer.invoke('galahad:git:review:commit', repoPath, message, push),
      commitContext: repoPath => ipcRenderer.invoke('galahad:git:review:commitContext', repoPath),
      push: repoPath => ipcRenderer.invoke('galahad:git:review:push', repoPath),
      shipInfo: repoPath => ipcRenderer.invoke('galahad:git:review:shipInfo', repoPath),
      createPr: repoPath => ipcRenderer.invoke('galahad:git:review:createPr', repoPath)
    }
  },
  terminal: {
    cwd: id => ipcRenderer.invoke('galahad:terminal:cwd', id),
    dispose: id => ipcRenderer.invoke('galahad:terminal:dispose', id),
    resize: (id, size) => ipcRenderer.invoke('galahad:terminal:resize', id, size),
    start: options => ipcRenderer.invoke('galahad:terminal:start', options),
    write: (id, data) => ipcRenderer.invoke('galahad:terminal:write', id, data),
    onData: (id, callback) => {
      const channel = `galahad:terminal:${id}:data`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    },
    onExit: (id, callback) => {
      const channel = `galahad:terminal:${id}:exit`
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on(channel, listener)

      return () => ipcRenderer.removeListener(channel, listener)
    }
  },
  onClosePreviewRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('galahad:close-preview-requested', listener)

    return () => ipcRenderer.removeListener('galahad:close-preview-requested', listener)
  },
  onOpenFolderRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('galahad:open-folder-requested', listener)

    return () => ipcRenderer.removeListener('galahad:open-folder-requested', listener)
  },
  onOpenUpdatesRequested: callback => {
    const listener = () => callback()
    ipcRenderer.on('galahad:open-updates', listener)

    return () => ipcRenderer.removeListener('galahad:open-updates', listener)
  },
  onDeepLink: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:deep-link', listener)

    return () => ipcRenderer.removeListener('galahad:deep-link', listener)
  },
  signalDeepLinkReady: () => ipcRenderer.invoke('galahad:deep-link-ready'),
  onWindowStateChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:window-state-changed', listener)

    return () => ipcRenderer.removeListener('galahad:window-state-changed', listener)
  },
  onFocusSession: callback => {
    const listener = (_event, sessionId) => callback(sessionId)
    ipcRenderer.on('galahad:focus-session', listener)

    return () => ipcRenderer.removeListener('galahad:focus-session', listener)
  },
  onNotificationAction: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:notification-action', listener)

    return () => ipcRenderer.removeListener('galahad:notification-action', listener)
  },
  onPreviewFileChanged: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:preview-file-changed', listener)

    return () => ipcRenderer.removeListener('galahad:preview-file-changed', listener)
  },
  onBackendExit: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:backend-exit', listener)

    return () => ipcRenderer.removeListener('galahad:backend-exit', listener)
  },
  // Soft gateway-mode apply finished tearing down the primary backend. Renderer
  // should wipe session lists + re-dial without a window reload.
  onConnectionApplied: callback => {
    const listener = () => callback()
    ipcRenderer.on('galahad:connection:applied', listener)

    return () => ipcRenderer.removeListener('galahad:connection:applied', listener)
  },
  onPowerResume: callback => {
    const listener = () => callback()
    ipcRenderer.on('galahad:power-resume', listener)

    return () => ipcRenderer.removeListener('galahad:power-resume', listener)
  },
  // AC ↔ battery transitions; renderers slow their backstop polls on battery.
  getOnBattery: () => ipcRenderer.invoke('galahad:power-battery:get'),
  onBatteryChanged: callback => {
    const listener = (_event, onBattery) => callback(Boolean(onBattery))
    ipcRenderer.on('galahad:power-battery', listener)

    return () => ipcRenderer.removeListener('galahad:power-battery', listener)
  },
  onBootProgress: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:boot-progress', listener)

    return () => ipcRenderer.removeListener('galahad:boot-progress', listener)
  },
  // First-launch bootstrap progress -- emitted by the install.ps1 stage
  // runner in main.ts (apps/desktop/electron/bootstrap-runner.ts).
  // Renderer's install overlay subscribes to live events and queries the
  // current snapshot via getBootstrapState() to recover after a devtools
  // reload mid-bootstrap.
  getBootstrapState: () => ipcRenderer.invoke('galahad:bootstrap:get'),
  continueBootstrapLocal: () => ipcRenderer.invoke('galahad:bootstrap:continue-local'),
  resetBootstrap: () => ipcRenderer.invoke('galahad:bootstrap:reset'),
  repairBootstrap: () => ipcRenderer.invoke('galahad:bootstrap:repair'),
  cancelBootstrap: () => ipcRenderer.invoke('galahad:bootstrap:cancel'),
  onBootstrapEvent: callback => {
    const listener = (_event, payload) => callback(payload)
    ipcRenderer.on('galahad:bootstrap:event', listener)

    return () => ipcRenderer.removeListener('galahad:bootstrap:event', listener)
  },
  getVersion: () => ipcRenderer.invoke('galahad:version'),
  getRemoteDisplayReason: () => ipcRenderer.invoke('galahad:get-remote-display-reason'),
  uninstall: {
    summary: () => ipcRenderer.invoke('galahad:uninstall:summary'),
    run: mode => ipcRenderer.invoke('galahad:uninstall:run', { mode })
  },
  updates: {
    check: () => ipcRenderer.invoke('galahad:updates:check'),
    apply: opts => ipcRenderer.invoke('galahad:updates:apply', opts),
    getBranch: () => ipcRenderer.invoke('galahad:updates:branch:get'),
    setBranch: name => ipcRenderer.invoke('galahad:updates:branch:set', name),
    onProgress: callback => {
      const listener = (_event, payload) => callback(payload)
      ipcRenderer.on('galahad:updates:progress', listener)

      return () => ipcRenderer.removeListener('galahad:updates:progress', listener)
    }
  },
  themes: {
    fetchMarketplace: id => ipcRenderer.invoke('galahad:vscode-theme:fetch', id),
    searchMarketplace: query => ipcRenderer.invoke('galahad:vscode-theme:search', query)
  },
  // Find-in-page (Ctrl/Cmd+F): delegates to Electron's
  // webContents.findInPage on the IPC sender's window so a Cmd+F pressed
  // in a secondary session window searches THAT window, not the primary.
  // `onFoundInPage` returns the unsubscribe fn; the renderer wires it via
  // `initFindInPageListener` in store/find-in-page.ts and tears it down
  // when the FindBar unmounts.
  findInPage: (query, options) => ipcRenderer.invoke('galahad:find-in-page', query, options),
  stopFindInPage: () => ipcRenderer.invoke('galahad:stop-find-in-page'),
  onFoundInPage: callback => {
    const listener = (_event, result) => callback(result)
    ipcRenderer.on('galahad:found-in-page', listener)

    return () => ipcRenderer.removeListener('galahad:found-in-page', listener)
  }
})
