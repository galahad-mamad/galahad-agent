// Galahad Agent — Model Switcher (runtime plugin, plain ESM)
// Palette commands for one-shot model/provider switching with free presets.

import { host } from '@galahad/plugin-sdk'
import { jsx } from 'react/jsx-runtime'

const FREE_PRESETS = [
  { id: 'ollama', label: 'Ollama (Local)', models: ['llama3.1', 'qwen2.5', 'mistral', 'codellama', 'deepseek-coder'] },
  { id: 'groq', label: 'Groq Cloud', models: ['llama-3.1-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b', 'gemma2-9b-it'] },
  { id: 'openrouter', label: 'OpenRouter', models: ['meta-llama/llama-3.1-70b-instruct:free', 'mistralai/mistral-7b-instruct:free', 'google/gemma-2-9b-it:free'] },
  { id: 'together', label: 'Together AI', models: ['meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 'mistralai/Mixtral-8x7B-Instruct-v0.1'] },
  { id: 'deepinfra', label: 'DeepInfra', models: ['meta-llama/Meta-Llama-3.1-70B-Instruct', 'mistralai/Mixtral-8x7B-Instruct-v0.1'] },
  { id: 'huggingface', label: 'HuggingFace Inference', models: ['meta-llama/Meta-Llama-3.1-70B-Instruct'] },
  { id: 'gemini', label: 'Google Gemini', models: ['gemini-1.5-flash', 'gemini-1.5-pro'] },
  { id: 'mistral', label: 'Mistral AI', models: ['mistral-large-latest', 'codestral-latest'] }
]

async function switchModel(modelId) {
  try {
    await host.request('config.set', { key: 'model.default', value: modelId })
    host.notify({ message: `Model → ${modelId}`, tone: 'success' })
  } catch (error) {
    host.notify({ message: `Model switch failed: ${error?.message ?? error}`, tone: 'error' })
  }
}

export default {
  id: 'galahad-model-switcher',
  name: 'Model Switcher',
  register(ctx) {
    ctx.registerMany(
      FREE_PRESETS.flatMap(preset =>
        preset.models.map(model => ({
          id: `switch:${preset.id}:${model}`,
          area: 'palette',
          title: `Switch model → ${model} (${preset.label})`,
          run: () => switchModel(model)
        }))
      )
    )
    ctx.register({
      id: 'show-current',
      area: 'palette',
      title: 'Model Switcher: show current model',
      run: () => host.notify({ message: `Current model: ${host.state.model.get() || 'unknown'}` })
    })
  }
}
