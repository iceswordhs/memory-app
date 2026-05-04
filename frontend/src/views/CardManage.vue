<template>
  <div class="card-manage">
    <div class="page-header">
      <h1 class="page-title">卡片管理</h1>
      <button class="btn-primary" @click="openForm">+ 新建卡片</button>
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <select v-model="filterTag" class="filter-select" @change="loadCards">
        <option value="">全部标签</option>
        <option v-for="t in tags" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>
    </div>

    <!-- 卡片列表 -->
    <div v-if="cards.length === 0" class="empty">
      还没有卡片，点击右上角新建
    </div>
    <div v-else class="card-list">
      <div v-for="card in cards" :key="card.id" class="card-item">
        <div class="card-item-header">
          <div class="card-tags">
            <span v-for="t in card.tags" :key="t.id" class="tag-badge" :style="{ background: t.color + '22', color: t.color, borderColor: t.color + '44' }">
              {{ t.name }}
            </span>
          </div>
          <div class="card-item-actions">
            <button class="btn-icon" @click="editCard(card)" title="编辑">&#x270F;</button>
            <button class="btn-icon danger" @click="deleteCard(card.id)" title="删除">&#x2716;</button>
          </div>
        </div>
        <div class="card-item-body">
          <div class="card-item-q" v-html="renderText(card.question)"></div>
          <div class="card-item-divider"></div>
          <div class="card-item-a" v-html="renderText(card.answer)"></div>
        </div>
        <div class="card-item-footer">
          <span class="card-meta">间隔: {{ card.interval_days }}天</span>
          <span class="card-meta">下次: {{ formatDate(card.next_review_at) }}</span>
          <span class="card-meta">EF: {{ card.ease_factor }}</span>
        </div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <h2 class="modal-title">{{ editingCard ? '编辑卡片' : '新建卡片' }}</h2>

        <div class="form-group">
          <label class="form-label">问题</label>
          <div
            ref="qRef"
            class="editor"
            contenteditable="true"
            data-placeholder="输入问题..."
            @input="onEditorInput('question')"
            @paste="onPaste('question', $event)"
          ></div>
          <label class="upload-btn">
            <input type="file" accept="image/*" hidden @change="uploadImg('question', $event)">
            + 添加图片
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">答案</label>
          <div
            ref="aRef"
            class="editor"
            contenteditable="true"
            data-placeholder="输入答案..."
            @input="onEditorInput('answer')"
            @paste="onPaste('answer', $event)"
          ></div>
          <label class="upload-btn">
            <input type="file" accept="image/*" hidden @change="uploadImg('answer', $event)">
            + 添加图片
          </label>
        </div>

        <div class="form-group">
          <label class="form-label">标签</label>
          <div class="tag-select">
            <label v-for="t in tags" :key="t.id" class="tag-checkbox">
              <input type="checkbox" :value="t.id" v-model="form.tagIds">
              <span class="tag-badge" :style="{ background: t.color + '22', color: t.color, borderColor: t.color + '44' }">
                {{ t.name }}
              </span>
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeForm">取消</button>
          <button class="btn-primary" @click="saveCard" :disabled="!hasContent() || saving">
            {{ saving ? '保存中...' : (editingCard ? '保存' : '创建') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { api } from '../api'

const cards = ref([])
const tags = ref([])
const filterTag = ref('')
const showForm = ref(false)
const editingCard = ref(null)
const saving = ref(false)

const qRef = ref(null)
const aRef = ref(null)

const form = ref({
  question: '',
  answer: '',
  tagIds: [],
})

// ── 格式转换 ──

function markdownToHtml(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">')
    .replace(/\n/g, '<br>')
}

function htmlToMarkdown(html) {
  if (!html) return ''
  let text = html
  // 把 <img> 转回 ![](url)
  text = text.replace(/<img[^>]*src="([^"]*)"[^>]*>/g, '![]($1)')
  // 去掉包裹在 <img> 周围的空 <br>
  text = text.replace(/<br>\s*$/, '')
  // br → 换行
  text = text.replace(/<br\s*\/?>/gi, '\n')
  // div → 换行
  text = text.replace(/<div>/gi, '\n')
  text = text.replace(/<\/div>/gi, '')
  // 去掉其余 HTML 标签
  text = text.replace(/<[^>]+>/g, '')
  // 还原转义字符
  text = text.replace(/&amp;/g, '&')
  text = text.replace(/&lt;/g, '<')
  text = text.replace(/&gt;/g, '>')
  // 清除首尾多余空白行
  text = text.replace(/\n{2,}$/, '\n').trim()
  return text
}

function renderText(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="inline-img">')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
  return html
}

function formatDate(d) {
  if (!d) return '-'
  return d.slice(0, 10)
}

// ── 编辑器操作 ──

function setEditorHTML(refEl, markdown) {
  const el = refEl?.value
  if (!el) return
  el.innerHTML = markdownToHtml(markdown)
}

function getEditorHTML(refEl) {
  return refEl?.value?.innerHTML || ''
}

function insertImageAtCursor(refEl, imgUrl) {
  const el = refEl?.value
  if (!el) return
  el.focus()
  // 确保光标在编辑区域内
  const sel = window.getSelection()
  let range
  if (sel.rangeCount === 0 || !el.contains(sel.anchorNode)) {
    range = document.createRange()
    range.selectNodeContents(el)
    range.collapse(false)
  } else {
    range = sel.getRangeAt(0)
  }
  range.deleteContents()
  const img = document.createElement('img')
  img.src = imgUrl
  range.insertNode(img)
  // 在图片后面插入一个空格方便继续输入
  range.setStartAfter(img)
  range.collapse(true)
  sel.removeAllRanges()
  sel.addRange(range)
  // 触发 input 事件同步数据
  el.dispatchEvent(new Event('input', { bubbles: true }))
}

function onEditorInput(target) {
  const html = getEditorHTML(target === 'question' ? qRef : aRef)
  form.value[target] = html
}

function hasContent() {
  const isEmpty = (html) => {
    if (!html || html === '<br>' || html === '<br>') return true
    const stripped = html.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim()
    const hasImg = /<img[^>]+>/.test(html)
    return stripped === '' && !hasImg
  }
  return !isEmpty(form.value.question) && !isEmpty(form.value.answer)
}

// ── 数据操作 ──

async function loadCards() {
  cards.value = await api.getCards(filterTag.value || undefined)
}

async function loadTags() {
  tags.value = await api.getTags()
}

function openForm() {
  showForm.value = true
  editingCard.value = null
  form.value = { question: '', answer: '', tagIds: [] }
  nextTick(() => {
    setEditorHTML(qRef, '')
    setEditorHTML(aRef, '')
  })
}

function editCard(card) {
  editingCard.value = card
  showForm.value = true
  form.value = {
    question: card.question,
    answer: card.answer,
    tagIds: card.tags.map(t => t.id),
  }
  nextTick(() => {
    setEditorHTML(qRef, card.question)
    setEditorHTML(aRef, card.answer)
  })
}

function closeForm() {
  showForm.value = false
  editingCard.value = null
}

async function saveCard() {
  if (saving.value) return
  saving.value = true
  try {
    const data = {
      question: htmlToMarkdown(form.value.question),
      answer: htmlToMarkdown(form.value.answer),
      tag_ids: form.value.tagIds,
    }

    if (editingCard.value) {
      await api.updateCard(editingCard.value.id, data)
    } else {
      await api.addCard(data)
    }

    closeForm()
    loadCards()
  } finally {
    saving.value = false
  }
}

async function deleteCard(id) {
  if (!confirm('确定删除这张卡片？')) return
  await api.deleteCard(id)
  loadCards()
}

async function onPaste(target, event) {
  const items = event.clipboardData?.items
  if (!items) return
  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      const file = item.getAsFile()
      const result = await api.uploadImage(file)
      insertImageAtCursor(target === 'question' ? qRef : aRef, result.url)
      return
    }
  }
}

async function uploadImg(target, event) {
  const file = event.target.files[0]
  if (!file) return
  const result = await api.uploadImage(file)
  insertImageAtCursor(target === 'question' ? qRef : aRef, result.url)
}

onMounted(() => {
  loadTags()
  loadCards()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.3rem;
  font-weight: 400;
  color: #e8e8ff;
}

.btn-primary {
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  padding: 10px 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: transparent;
  color: rgba(212, 212, 232, 0.6);
  font-size: 0.9rem;
  cursor: pointer;
}

.filter-bar {
  margin-bottom: 20px;
}

.filter-select {
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  color: #d4d4e8;
  font-size: 0.85rem;
  outline: none;
}

.filter-select option {
  background: #1a1a2e;
}

.empty {
  text-align: center;
  padding: 60px 0;
  color: rgba(212, 212, 232, 0.3);
  font-size: 0.9rem;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 20px;
}

.card-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-badge {
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  border: 1px solid;
}

.card-item-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  background: none;
  border: none;
  color: rgba(212, 212, 232, 0.3);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(212, 212, 232, 0.6);
}

.btn-icon.danger:hover {
  color: #e06060;
}

.card-item-body {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  gap: 16px;
  margin-bottom: 12px;
}

.card-item-divider {
  width: 1px;
  background: rgba(255, 255, 255, 0.06);
}

.card-item-q, .card-item-a {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #d4d4e8;
}

.card-item-a {
  color: rgba(212, 212, 232, 0.65);
}

.card-item-q :deep(.inline-img),
.card-item-a :deep(.inline-img) {
  max-width: 100%;
  border-radius: 6px;
  margin: 4px 0;
}

.card-item-footer {
  display: flex;
  gap: 16px;
}

.card-meta {
  font-size: 0.7rem;
  color: rgba(212, 212, 232, 0.25);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 200;
  backdrop-filter: blur(4px);
}

.modal {
  background: #1a1a30;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 32px;
  width: 640px;
  max-width: 92vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 400;
  color: #e8e8ff;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 0.8rem;
  color: rgba(212, 212, 232, 0.4);
  margin-bottom: 8px;
}

/* ── 富文本编辑器 ── */
.editor {
  width: 100%;
  min-height: 160px;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.2);
  color: #d4d4e8;
  font-size: 0.95rem;
  font-family: inherit;
  line-height: 1.7;
  outline: none;
  cursor: text;
  word-break: break-word;
}

.editor:focus {
  border-color: rgba(99, 102, 241, 0.3);
}

.editor:empty::before {
  content: attr(data-placeholder);
  color: rgba(255, 255, 255, 0.15);
  pointer-events: none;
}

.editor :deep(img) {
  display: block;
  max-width: 100%;
  max-height: 240px;
  width: auto;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
  object-fit: contain;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.editor :deep(strong) {
  font-weight: 600;
  color: #e8e8ff;
}

.upload-btn {
  display: inline-block;
  margin-top: 8px;
  font-size: 0.8rem;
  color: rgba(99, 102, 241, 0.6);
  cursor: pointer;
  transition: color 0.2s;
}

.upload-btn:hover {
  color: rgba(99, 102, 241, 0.9);
}

.tag-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.tag-checkbox input {
  accent-color: #6366f1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 24px;
}
</style>
