<template>
  <div class="tag-manage">
    <div class="page-header">
      <h1 class="page-title">标签管理</h1>
      <button class="btn-primary" @click="showForm = true">+ 新建标签</button>
    </div>

    <div v-if="tags.length === 0" class="empty">
      还没有标签
    </div>

    <div v-else class="tag-list">
      <div v-for="tag in tags" :key="tag.id" class="tag-item">
        <div class="tag-color-dot" :style="{ background: tag.color }"></div>
        <span class="tag-name">{{ tag.name }}</span>
        <button class="btn-icon danger" @click="deleteTag(tag.id)" title="删除">&#x2716;</button>
      </div>
    </div>

    <!-- 新建标签弹窗 -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <h2 class="modal-title">新建标签</h2>
        <div class="form-group">
          <input v-model="newName" class="form-input" placeholder="标签名称" @keydown.enter="addTag" autofocus>
        </div>
        <div class="color-group">
          <span v-for="c in colors" :key="c"
                class="color-option"
                :class="{ active: newColor === c }"
                :style="{ background: c }"
                @click="newColor = c"></span>
        </div>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showForm = false">取消</button>
          <button class="btn-primary" @click="addTag" :disabled="!newName.trim()">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const tags = ref([])
const showForm = ref(false)
const newName = ref('')
const newColor = ref('#6366f1')

const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6']

async function loadTags() {
  tags.value = await api.getTags()
}

async function addTag() {
  if (!newName.value.trim()) return
  await api.addTag({ name: newName.value.trim(), color: newColor.value })
  newName.value = ''
  newColor.value = '#6366f1'
  showForm.value = false
  loadTags()
}

async function deleteTag(id) {
  if (!confirm('确定删除这个标签？')) return
  await api.deleteTag(id)
  loadTags()
}

onMounted(loadTags)
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

.empty {
  text-align: center;
  padding: 60px 0;
  color: rgba(212, 212, 232, 0.3);
  font-size: 0.9rem;
}

.tag-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.tag-color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.tag-name {
  flex: 1;
  font-size: 0.95rem;
  color: #d4d4e8;
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

.btn-icon.danger:hover {
  color: #e06060;
  background: rgba(220, 80, 80, 0.08);
}

/* modal */
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
  width: 400px;
  max-width: 90vw;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 400;
  color: #e8e8ff;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.2);
  color: #d4d4e8;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
}

.form-input:focus {
  border-color: rgba(99, 102, 241, 0.3);
}

.color-group {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.color-option {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.color-option.active {
  border-color: #fff;
  transform: scale(1.15);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
