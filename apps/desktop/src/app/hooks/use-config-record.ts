import { useQuery } from '@tanstack/react-query'

import { getGalahadConfigRecord } from '@/galahad'
import { queryClient, writeCache } from '@/lib/query-client'
import type { GalahadConfigRecord } from '@/types/galahad'

// One shared cache for the whole profile config record (`GET /api/config`).
// Every settings surface (MCP, model, config) reads and writes through this key
// so a save in one shows in the others, and revisiting a tab paints the cache
// instead of blanking on a fresh fetch.
//
// Distinct from session/hooks/use-galahad-config.ts, which is side-effecting —
// it pushes personality/cwd/voice/… into the session stores for live chat.
export const GALAHAD_CONFIG_KEY = ['galahad-config-record'] as const

// staleTime 0 → serve cache instantly, background-revalidate on every mount.
export const useGalahadConfigRecord = () =>
  useQuery({ queryKey: GALAHAD_CONFIG_KEY, queryFn: getGalahadConfigRecord, staleTime: 0 })

export const setGalahadConfigCache = writeCache<GalahadConfigRecord>(GALAHAD_CONFIG_KEY)

export const invalidateGalahadConfig = () => queryClient.invalidateQueries({ queryKey: GALAHAD_CONFIG_KEY })
