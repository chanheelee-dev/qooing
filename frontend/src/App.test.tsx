import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, expect, it, mock, spyOn } from 'bun:test'

import App from './App'

beforeEach(() => {
  localStorage.clear()
  mock.restore()
})

it('loads and renders the selected wiki document', async () => {
  spyOn(globalThis, 'fetch')
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify([{ slug: 'sleep', title: 'Sleep', description: 'Basics' }]),
      ),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          slug: 'sleep',
          type: 'Wiki',
          title: 'Sleep',
          description: 'Basics',
          body: '# Rest well',
          sources: [],
        }),
      ),
    )

  render(<App />)
  fireEvent.click(await screen.findByRole('button', { name: 'Sleep' }))

  expect(await screen.findByRole('heading', { name: 'Rest well' })).not.toBeNull()
})

it('streams a chat response and prevents an empty submission', async () => {
  spyOn(globalThis, 'fetch')
    .mockResolvedValueOnce(new Response(JSON.stringify([])))
    .mockResolvedValueOnce(
      new Response('event: delta\ndata: {"text":"hello"}\n\nevent: done\ndata: {}\n\n', {
        headers: { 'content-type': 'text/event-stream' },
      }),
    )

  render(<App />)
  const send = screen.getByRole('button', { name: 'Send' })
  expect(send.hasAttribute('disabled')).toBe(true)

  fireEvent.change(screen.getByLabelText('Prompt'), { target: { value: 'sleep?' } })
  fireEvent.click(send)

  await waitFor(() => expect(screen.getByText('hello')).not.toBeNull())
})
