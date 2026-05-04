import { createRouter, createWebHistory } from 'vue-router'
import ReviewView from '../views/ReviewView.vue'
import CardManage from '../views/CardManage.vue'
import TagManage from '../views/TagManage.vue'

const routes = [
  { path: '/', name: 'review', component: ReviewView },
  { path: '/cards', name: 'cards', component: CardManage },
  { path: '/tags', name: 'tags', component: TagManage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
