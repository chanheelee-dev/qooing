import { describe, expect, it } from 'bun:test'

import { consumeSse, createSseParser } from './sse'

describe('createSseParser', () => {
  it('parses events split across arbitrary chunks', () => {
    const events: Array<{ event: string; data: unknown }> = []
    const parser = createSseParser((event) => events.push(event))

    parser.push('event: delta\ndata: {"te')
    parser.push('xt":"안녕"}\n\nevent: done\r')
    parser.push('\ndata: {}\r\n\r\n')
    parser.finish()

    expect(events).toEqual([
      { event: 'delta', data: { text: '안녕' } },
      { event: 'done', data: {} },
    ])
  })

  it('throws when the stream ends with an incomplete event', () => {
    const parser = createSseParser(() => undefined)
    parser.push('event: delta\ndata: {"text":"partial"}')

    expect(() => parser.finish()).toThrow('Incomplete SSE event')
  })

  it('rejects a cleanly framed stream that disconnects before done', async () => {
    const response = new Response('event: delta\ndata: {"text":"partial"}\n\n')

    await expect(consumeSse(response, () => undefined)).rejects.toThrow(
      'SSE stream ended before done',
    )
  })
})
