<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { path: '/', name: 'GameList', label: '游戏列表', icon: 'IceCream' },
  { path: '/games/new', name: 'GameCreate', label: '添加游戏', icon: 'Plus' },
  { path: '/scan', name: 'Scanner', label: '扫描目录', icon: 'Search' },
]

function navigate(path) {
  router.push(path)
}

function isActive(path) {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <el-icon :size="28" color="#3b82f6"><Monitor /></el-icon>
          <span class="logo-text">Galgame Library</span>
        </div>
      </div>
      <nav class="nav-menu">
        <div
          v-for="item in navItems"
          :key="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="navigate(item.path)"
        >
          <el-icon :size="18">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.label }}</span>
        </div>
      </nav>
      <div class="sidebar-footer">
        <div class="version">v1.0.0</div>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: var(--bg-primary);
}

.sidebar {
  width: 220px;
  background-color: var(--bg-nav);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  font-size: 17px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 0.3px;
}

.nav-menu {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: #94a3b8;
  font-size: 14px;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.nav-item.active {
  background-color: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.version {
  font-size: 12px;
  color: #64748b;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: var(--bg-primary);
}
</style>