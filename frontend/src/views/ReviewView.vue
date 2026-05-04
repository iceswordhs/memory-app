<template>
  <div class="review-view">
    <!-- 空闲状态 -->
    <div v-if="phase === 'idle'" class="center-content">
      <div class="idle-icon">&#x1F3B5;</div>
      <h1 class="idle-title">开始复习</h1>
      <p class="idle-subtitle">
        <template v-if="stats.due_cards > 0">
          今天有 <strong>{{ stats.due_cards }}</strong> 张卡片待复习
        </template>
        <template v-else>
          暂无待复习的卡片，去添加一些吧
        </template>
      </p>
      <button v-if="stats.due_cards > 0" class="btn-primary" @click="startReview">
        开始复习
      </button>
    </div>

    <!-- 加载中 -->
    <div v-else-if="phase === 'loading'" class="center-content">
      <div class="spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>

    <!-- 复习中：展示问题 -->
    <div v-else-if="phase === 'question'" class="review-card">
      <div class="card-progress">
        <div class="progress-dots">
          <span v-for="i in 3" :key="i"
                class="dot"
                :class="{ active: i === currentIndex + 1, done: i <= currentIndex }">
          </span>
        </div>
        <span class="progress-text">{{ currentIndex + 1 }} / 3</span>
      </div>

      <div class="card-content">
        <div class="card-label">问题</div>
        <div class="card-text" v-html="renderedQuestion"></div>

        <div class="answer-section">
          <textarea
            ref="answerInput"
            v-model="userAnswer"
            class="answer-input"
            placeholder="输入你的答案..."
            rows="3"
            @keydown.ctrl.enter="submitAnswer"
            @keydown.meta.enter="submitAnswer"
          ></textarea>
          <button class="btn-primary" @click="submitAnswer" :disabled="!userAnswer.trim()">
            确认
          </button>
        </div>
      </div>
    </div>

    <!-- 展示答案对比 -->
    <div v-else-if="phase === 'answer'" class="review-card">
      <div class="card-progress">
        <div class="progress-dots">
          <span v-for="i in 3" :key="i"
                class="dot"
                :class="{ active: i === currentIndex + 1, done: i <= currentIndex }">
          </span>
        </div>
        <span class="progress-text">{{ currentIndex + 1 }} / 3</span>
      </div>

      <div class="card-content compare">
        <div class="compare-col">
          <div class="card-label">你的答案</div>
          <div class="card-text user-answer" v-html="renderedUserAnswer"></div>
        </div>
        <div class="compare-divider"></div>
        <div class="compare-col">
          <div class="card-label correct-label">正确答案</div>
          <div class="card-text correct-answer" v-html="renderedAnswer"></div>
        </div>
      </div>

      <div class="rating-section">
        <p class="rating-hint">记得怎么样？</p>
        <div class="rating-buttons">
          <button class="btn-rating forgot" @click="rate('forgot')">
            忘记了
          </button>
          <button class="btn-rating unsure" @click="rate('unsure')">
            不熟悉
          </button>
          <button class="btn-rating familiar" @click="rate('familiar')">
            熟悉
          </button>
        </div>
      </div>
    </div>

    <!-- 一组完成 -->
    <div v-else-if="phase === 'group_done'" class="center-content">
      <div class="done-icon">&#x2705;</div>
      <h2 class="done-title">一组复习完成</h2>
      <p class="done-subtitle">{{ groupResult.familiar }} / 3 记住了</p>
      <div class="done-actions">
        <button v-if="hasMore" class="btn-primary" @click="nextGroup">
          继续下一组
        </button>
        <button class="btn-secondary" @click="goHome">
          {{ hasMore ? '休息一下' : '全部完成，返回' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { api } from '../api'
import { useRouter } from 'vue-router'

const router = useRouter()

const phase = ref('idle') // idle | loading | question | answer | group_done
const cards = ref([])
const currentIndex = ref(0)
const userAnswer = ref('')
const hasMore = ref(false)
const groupResult = ref({ familiar: 0, unsure: 0, forgot: 0 })
const stats = ref({ due_cards: 0 })
const answerInput = ref(null)
const savedUserAnswers = ref({})

function renderMd(text) {
  if (!text) return ''
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="inline-img">')
    .replace(/\[([^\]]*)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
  return html
}

const currentCard = computed(() => cards.value[currentIndex.value] || null)

const renderedQuestion = computed(() => {
  return currentCard.value ? renderMd(currentCard.value.question) : ''
})

const renderedAnswer = computed(() => {
  return currentCard.value ? renderMd(currentCard.value.answer) : ''
})

const renderedUserAnswer = computed(() => {
  const ans = savedUserAnswers.value[currentIndex.value] || ''
  return renderMd(ans)
})

async function fetchStats() {
  try {
    stats.value = await api.getStats()
  } catch {}
}

async function startReview() {
  phase.value = 'loading'
  try {
    const data = await api.getNextGroup()
    cards.value = data.cards
    hasMore.value = data.has_more
    currentIndex.value = 0
    userAnswer.value = ''
    savedUserAnswers.value = {}
    groupResult.value = { familiar: 0, unsure: 0, forgot: 0 }

    if (cards.value.length === 0) {
      phase.value = 'idle'
      await fetchStats()
      return
    }

    phase.value = 'question'
    await nextTick()
    answerInput.value?.focus()
  } catch {
    phase.value = 'idle'
  }
}

function submitAnswer() {
  if (!userAnswer.value.trim()) return
  savedUserAnswers.value[currentIndex.value] = userAnswer.value.trim()
  phase.value = 'answer'
}

async function rate(rating) {
  const card = currentCard.value
  if (!card) return

  // 先乐观更新统计
  groupResult.value[rating]++

  try {
    await api.submitReview(card.id, rating)
  } catch {}

  // 检查是否还有下一张
  if (currentIndex.value < cards.value.length - 1) {
    currentIndex.value++
    userAnswer.value = ''
    phase.value = 'question'
    await nextTick()
    answerInput.value?.focus()
  } else {
    phase.value = 'group_done'
    await fetchStats()
  }
}

async function nextGroup() {
  phase.value = 'loading'
  try {
    const data = await api.getNextGroup()
    cards.value = data.cards
    hasMore.value = data.has_more
    currentIndex.value = 0
    userAnswer.value = ''
    savedUserAnswers.value = {}
    groupResult.value = { familiar: 0, unsure: 0, forgot: 0 }

    if (cards.value.length === 0) {
      phase.value = 'idle'
      await fetchStats()
      return
    }

    phase.value = 'question'
    await nextTick()
    answerInput.value?.focus()
  } catch {
    phase.value = 'idle'
  }
}

function goHome() {
  phase.value = 'idle'
  fetchStats()
}

// 初始加载
fetchStats()
</script>

<style scoped>
.review-view {
  min-height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

/* 居中内容 */
.center-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 16px;
  padding: 40px 0;
}

.idle-icon {
  font-size: 3rem;
  opacity: 0.6;
  margin-bottom: 8px;
}

.idle-title {
  font-size: 2rem;
  font-weight: 300;
  color: #e8e8ff;
}

.idle-subtitle {
  font-size: 0.95rem;
  color: rgba(212, 212, 232, 0.5);
  margin-bottom: 12px;
}

.idle-subtitle strong {
  color: #f0a070;
  font-weight: 500;
}

/* 按钮 */
.btn-primary {
  padding: 12px 36px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  padding: 12px 36px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  background: transparent;
  color: rgba(212, 212, 232, 0.6);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-secondary:hover {
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(212, 212, 232, 0.8);
}

/* spinner */
.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(212, 212, 232, 0.4);
  font-size: 0.9rem;
}

/* 复习卡片 */
.review-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 24px;
}

.card-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.progress-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  transition: all 0.3s;
}

.dot.active {
  background: #6366f1;
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.4);
}

.dot.done {
  background: rgba(99, 102, 241, 0.4);
}

.progress-text {
  font-size: 0.8rem;
  color: rgba(212, 212, 232, 0.3);
}

.card-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(212, 212, 232, 0.3);
}

.card-text {
  font-size: 1.05rem;
  line-height: 1.7;
  color: #d4d4e8;
}

.card-text :deep(.inline-img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 8px 0;
}

.card-text :deep(pre) {
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  font-size: 0.9rem;
}

.card-text :deep(code) {
  background: rgba(0,0,0,0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}

.card-text :deep(a) {
  color: #818cf8;
  text-decoration: none;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.answer-input {
  width: 100%;
  padding: 14px 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.25);
  color: #e0e0f0;
  font-size: 0.95rem;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s;
  outline: none;
}

.answer-input:focus {
  border-color: rgba(99, 102, 241, 0.4);
}

.answer-input::placeholder {
  color: rgba(255, 255, 255, 0.15);
}

.answer-section .btn-primary {
  align-self: flex-end;
}

/* 对比模式 */
.compare {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  gap: 28px;
}

.compare-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.compare-divider {
  width: 1px;
  background: rgba(255, 255, 255, 0.06);
  align-self: stretch;
}

.correct-label {
  color: rgba(123, 207, 154, 0.6);
}

.user-answer {
  color: rgba(212, 212, 232, 0.6);
}

.correct-answer {
  color: #9bdfb0;
}

/* 评分 */
.rating-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding-bottom: 24px;
}

.rating-hint {
  font-size: 0.85rem;
  color: rgba(212, 212, 232, 0.3);
}

.rating-buttons {
  display: flex;
  gap: 12px;
}

.btn-rating {
  padding: 12px 28px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  color: rgba(212, 212, 232, 0.6);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-rating:hover {
  transform: translateY(-2px);
}

.btn-rating.forgot:hover {
  border-color: rgba(220, 80, 80, 0.4);
  background: rgba(220, 80, 80, 0.08);
  color: #e06060;
}

.btn-rating.unsure:hover {
  border-color: rgba(200, 160, 60, 0.4);
  background: rgba(200, 160, 60, 0.08);
  color: #d4a050;
}

.btn-rating.familiar:hover {
  border-color: rgba(80, 200, 120, 0.4);
  background: rgba(80, 200, 120, 0.08);
  color: #7bcf9a;
}

/* 完成 */
.done-icon {
  font-size: 2.5rem;
  margin-bottom: 4px;
}

.done-title {
  font-size: 1.4rem;
  font-weight: 400;
  color: #e8e8ff;
}

.done-subtitle {
  font-size: 0.9rem;
  color: rgba(212, 212, 232, 0.4);
  margin-bottom: 8px;
}

.done-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
</style>
