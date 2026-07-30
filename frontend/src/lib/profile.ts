export interface BabyInfo {
  name: string
  birth_date: string
  notes: string
}

export const EMPTY_PROFILE: BabyInfo = { name: '', birth_date: '', notes: '' }
const STORAGE_KEY = 'qooing.baby-info.v1'

function validDate(value: string): boolean {
  if (value === '') return true
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!match) return false
  const [, year, month, day] = match.map(Number)
  const parsed = new Date(Date.UTC(year, month - 1, day))
  return (
    parsed.getUTCFullYear() === year &&
    parsed.getUTCMonth() === month - 1 &&
    parsed.getUTCDate() === day
  )
}

function normalizeBabyInfo(value: unknown): BabyInfo | null {
  if (!value || typeof value !== 'object') return null
  const record = value as Record<string, unknown>
  if (record.name !== undefined && typeof record.name !== 'string') return null
  if (record.birth_date !== undefined && typeof record.birth_date !== 'string') return null
  if (record.notes !== undefined && typeof record.notes !== 'string') return null
  const profile = {
    name: record.name ?? '',
    birth_date: record.birth_date ?? '',
    notes: record.notes ?? '',
  } as BabyInfo
  if (profile.name.length > 100 || profile.notes.length > 2000) return null
  return validDate(profile.birth_date) ? profile : null
}

export function loadProfile(): BabyInfo {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) return { ...EMPTY_PROFILE }
  try {
    const parsed: unknown = JSON.parse(stored)
    return normalizeBabyInfo(parsed) ?? { ...EMPTY_PROFILE }
  } catch {
    return { ...EMPTY_PROFILE }
  }
}

export function saveProfile(profile: BabyInfo): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
}

export function exportProfile(profile: BabyInfo): string {
  return JSON.stringify({ version: 1, baby_info: profile }, null, 2)
}

export function importProfile(text: string): BabyInfo {
  let parsed: unknown
  try {
    parsed = JSON.parse(text)
  } catch {
    throw new Error('Invalid profile JSON')
  }
  if (!parsed || typeof parsed !== 'object') throw new Error('Unsupported profile file')
  const record = parsed as Record<string, unknown>
  if (record.version !== 1) {
    throw new Error('Unsupported profile file')
  }
  const profile = normalizeBabyInfo(record.baby_info)
  if (!profile) throw new Error('Invalid baby profile')
  saveProfile(profile)
  return profile
}
