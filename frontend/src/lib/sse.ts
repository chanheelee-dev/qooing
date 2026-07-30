export interface SseEvent {
  event: string
  data: unknown
}

export interface SseParser {
  push(chunk: string): void
  finish(): void
}

export function createSseParser(onEvent: (event: SseEvent) => void): SseParser {
  let buffer = ''

  function consume(): void {
    while (true) {
      const match = /\r?\n\r?\n/.exec(buffer)
      if (!match || match.index === undefined) return
      const block = buffer.slice(0, match.index)
      buffer = buffer.slice(match.index + match[0].length)
      if (!block.trim()) continue

      let event = 'message'
      const dataLines: string[] = []
      for (const line of block.split(/\r?\n/)) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        if (line.startsWith('data:')) dataLines.push(line.slice(5).trimStart())
      }
      const rawData = dataLines.join('\n')
      onEvent({ event, data: rawData ? JSON.parse(rawData) : null })
    }
  }

  return {
    push(chunk: string) {
      buffer += chunk
      consume()
    },
    finish() {
      consume()
      if (buffer.trim()) throw new Error('Incomplete SSE event')
    },
  }
}

export async function consumeSse(
  response: Response,
  onEvent: (event: SseEvent) => void,
): Promise<void> {
  if (!response.ok) throw new Error(`Chat request failed (${response.status})`)
  if (!response.body) throw new Error('Chat response has no stream')
  let completed = false
  const parser = createSseParser((event) => {
    if (event.event === 'done') completed = true
    onEvent(event)
  })
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    parser.push(decoder.decode(value, { stream: true }))
  }
  parser.push(decoder.decode())
  parser.finish()
  if (!completed) throw new Error('SSE stream ended before done')
}
