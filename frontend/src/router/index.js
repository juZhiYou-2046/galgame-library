import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'GameList',
    component: () => import('../views/GameList.vue'),
    meta: { title: '游戏列表' },
  },
  {
    path: '/games/new',
    name: 'GameCreate',
    component: () => import('../views/GameForm.vue'),
    meta: { title: '添加游戏' },
  },
  {
    path: '/games/:id',
    name: 'GameDetail',
    component: () => import('../views/GameDetail.vue'),
    meta: { title: '游戏详情' },
  },
  {
    path: '/games/:id/edit',
    name: 'GameEdit',
    component: () => import('../views/GameForm.vue'),
    meta: { title: '编辑游戏' },
  },
  {
    path: '/scan',
    name: 'Scanner',
    component: () => import('../views/ScannerView.vue'),
    meta: { title: '扫描目录' },
  },
  {
    path: '/tags',
    name: 'TagCloud',
    component: () => import('../views/TagCloud.vue'),
    meta: { title: '标签管理' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || 'Galgame Library'} - Galgame Library`
})

export default router