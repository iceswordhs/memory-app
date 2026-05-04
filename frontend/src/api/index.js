const BASE = '/api'

async function request(url, options = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

export const api = {
  // Tags
  getTags: () => request('/tags'),
  addTag: (data) => request('/tags', { method: 'POST', body: JSON.stringify(data) }),
  deleteTag: (id) => request(`/tags/${id}`, { method: 'DELETE' }),

  // Cards
  getCards: (tagId) => request('/cards' + (tagId ? `?tag_id=${tagId}` : '')),
  getCard: (id) => request(`/cards/${id}`),
  addCard: (data) => request('/cards', { method: 'POST', body: JSON.stringify(data) }),
  updateCard: (id, data) => request(`/cards/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCard: (id) => request(`/cards/${id}`, { method: 'DELETE' }),

  // Upload
  uploadImage: (file) => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE}/upload`, { method: 'POST', body: form }).then(r => r.json())
  },

  // Review
  getNextGroup: () => request('/review/next'),
  submitReview: (cardId, rating) => request(`/review/${cardId}`, {
    method: 'POST',
    body: JSON.stringify({ rating }),
  }),

  // Stats
  getStats: () => request('/stats'),
}
