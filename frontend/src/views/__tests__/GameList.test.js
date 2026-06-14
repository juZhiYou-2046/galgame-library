import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

// 模拟 API 模块
vi.mock('../../api/games', () => ({
  getGames: vi.fn().mockResolvedValue({ total: 0, items: [] }),
  deleteGame: vi.fn().mockResolvedValue(undefined),
}))
vi.mock('../../api/importExport', () => ({
  getExportUrl: vi.fn().mockReturnValue('/api/games/export?format=json'),
  importGames: vi.fn().mockResolvedValue({ total: 0, created: 0, updated: 0, skipped: 0, errors: [] }),
}))

// 模拟 vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
  useRoute: () => ({
    query: {},
    path: '/',
  }),
}))

// 模拟 element-plus 消息
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn(), info: vi.fn() },
    ElMessageBox: { confirm: vi.fn() },
  }
})

import GameList from '../GameList.vue'

describe('GameList.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders page title', () => {
    const wrapper = mount(GameList)
    expect(wrapper.find('.page-title').text()).toBe('游戏列表')
  })

  it('has search input', () => {
    const wrapper = mount(GameList)
    const searchInput = wrapper.find('.filter-card')
    expect(searchInput.exists()).toBe(true)
  })

  it('has export and import buttons', () => {
    const wrapper = mount(GameList)
    const html = wrapper.html()
    expect(html).toContain('导出')
    expect(html).toContain('导入')
  })

  it('has advanced search toggle', () => {
    const wrapper = mount(GameList)
    const html = wrapper.html()
    expect(html).toContain('高级搜索')
  })
})
