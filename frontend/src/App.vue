<template>
  <div class="app-container">
    <!-- 顶部居中导航 -->
    <header class="topbar">
      <div class="topbar-inner">
        <nav class="nav">
          <router-link to="/" class="nav-link" exact-active-class="active">
            <span class="nav-icon">&#x1F3B5;</span>
            <span>复习</span>
          </router-link>
          <router-link to="/cards" class="nav-link" active-class="active">
            <span class="nav-icon">&#x1F4DD;</span>
            <span>卡片</span>
          </router-link>
          <router-link to="/tags" class="nav-link" active-class="active">
            <span class="nav-icon">&#x1F3F7;</span>
            <span>标签</span>
          </router-link>
        </nav>
        <StatsPanel />
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import StatsPanel from './components/StatsPanel.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
  background: #0f0f1a;
  color: #d4d4e8;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

.app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
}

.topbar {
  position: sticky;
  top: 0;
  width: 100%;
  z-index: 100;
  background: rgba(15, 15, 26, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  padding: 16px 24px;
  display: flex;
  justify-content: center;
}

.topbar-inner {
  display: flex;
  align-items: center;
  gap: 48px;
  max-width: 860px;
  width: 100%;
}

.nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 10px;
  text-decoration: none;
  color: rgba(212, 212, 232, 0.4);
  font-size: 0.85rem;
  transition: all 0.2s;
}

.nav-link:hover {
  color: rgba(212, 212, 232, 0.7);
  background: rgba(255, 255, 255, 0.04);
}

.nav-link.active {
  color: #e8e8ff;
  background: rgba(99, 102, 241, 0.12);
}

.nav-icon {
  font-size: 1.1rem;
  line-height: 1;
}

.main {
  flex: 1;
  width: 100%;
  max-width: 740px;
  padding: 40px 32px 80px;
}

@media (max-width: 640px) {
  .topbar {
    padding: 12px 16px;
  }
  .topbar-inner {
    gap: 24px;
    justify-content: center;
  }
  .nav-link {
    padding: 6px 12px;
    font-size: 0.8rem;
  }
  .nav-link span:last-child {
    display: none;
  }
  .main {
    padding: 24px 16px 80px;
  }
}
</style>
