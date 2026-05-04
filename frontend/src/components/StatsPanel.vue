<template>
  <div class="stats-panel">
    <div class="stat-item">
      <span class="stat-value due">{{ stats.due_cards }}</span>
      <span class="stat-label">待复习</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-value">{{ stats.reviewed_today }}</span>
      <span class="stat-label">已完成</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-value" :class="{ good: stats.retention_rate >= 70, mid: stats.retention_rate >= 40 && stats.retention_rate < 70, low: stats.retention_rate < 40 }">
        {{ stats.retention_rate }}%
      </span>
      <span class="stat-label">正确率</span>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
      <span class="stat-value streak">{{ stats.streak_days }}</span>
      <span class="stat-label">连续天数</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../api'

const stats = ref({
  due_cards: 0,
  reviewed_today: 0,
  total_cards: 0,
  retention_rate: 0,
  streak_days: 0,
})

let timer

async function fetchStats() {
  try {
    stats.value = await api.getStats()
  } catch {
    // ignore
  }
}

onMounted(() => {
  fetchStats()
  timer = setInterval(fetchStats, 30000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.stats-panel {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-value {
  font-size: 1.05rem;
  font-weight: 400;
  color: #d4d4e8;
  font-variant-numeric: tabular-nums;
}

.stat-value.due {
  color: #f0a070;
}

.stat-value.streak {
  color: #70b8f0;
}

.stat-value.good { color: #7bcf9a; }
.stat-value.mid { color: #d4a050; }
.stat-value.low { color: #e06060; }

.stat-label {
  font-size: 0.7rem;
  color: rgba(212, 212, 232, 0.35);
}

.stat-divider {
  width: 1px;
  height: 16px;
  background: rgba(255, 255, 255, 0.06);
}

@media (max-width: 640px) {
  .stats-panel {
    gap: 12px;
  }
  .stat-label {
    display: none;
  }
  .stat-value {
    font-size: 0.9rem;
  }
}
</style>
