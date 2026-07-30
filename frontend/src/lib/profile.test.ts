import { beforeEach, describe, expect, it } from 'bun:test'

import { importProfile, loadProfile, saveProfile } from './profile'

describe('baby profile persistence', () => {
  beforeEach(() => localStorage.clear())

  it('round-trips a valid profile', () => {
    const profile = { name: '아기', birth_date: '2026-06-01', notes: '건강함' }
    saveProfile(profile)

    expect(loadProfile()).toEqual(profile)
  })

  it('rejects malformed imports without replacing stored data', () => {
    const original = { name: '기존', birth_date: '', notes: '' }
    saveProfile(original)

    expect(() => importProfile('{"version":2,"baby_info":{}}')).toThrow(
      'Unsupported profile file',
    )
    expect(loadProfile()).toEqual(original)
  })

  it('accepts optional fields and fills missing values for the editor', () => {
    expect(importProfile('{"version":1,"baby_info":{"name":"아기"}}')).toEqual({
      name: '아기',
      birth_date: '',
      notes: '',
    })
  })

  it('rejects invalid birth dates without replacing stored data', () => {
    const original = { name: '기존', birth_date: '2026-06-01', notes: '' }
    saveProfile(original)

    expect(() =>
      importProfile(
        '{"version":1,"baby_info":{"name":"새 값","birth_date":"not-a-date","notes":""}}',
      ),
    ).toThrow('Invalid baby profile')
    expect(loadProfile()).toEqual(original)
  })

  it('rejects profile fields that exceed the API limits', () => {
    expect(() =>
      importProfile(
        JSON.stringify({
          version: 1,
          baby_info: { name: 'n'.repeat(101), notes: '', birth_date: '' },
        }),
      ),
    ).toThrow('Invalid baby profile')
  })
})
