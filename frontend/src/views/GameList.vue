<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getGames, deleteGame } from '../api/games'

const router = useRouter()

const games = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')
const developer = ref('')
const tag = ref('')
const page = ref(1)
const pageSize = ref(20)

async function fetchGames() {
  loading.value = true
  try {
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (search.value) params.search = search.value
    if (developer.value) params.developer = developer.value
    if (tag.value) params.tag = tag.value

    const data = await getGames(params)
    games.value = data.items
    total.value = data.total
  } catch (err) {
    ElMessage.error('获取游戏列表失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchGames()
}

function resetFilters() {
  search.value = ''
  developer.value = ''
  tag.value = ''
  page.value = 1
  fetchGames()
}

function handleDelete(id, title) {
  ElMessageBox.confirm(`确定要删除《${title}》吗？此操作不可恢复。`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteGame(id)
      ElMessage.success('删除成功')
      fetchGames()
    } catch (err) {
      ElMessage.error('删除失败: ' + (err.response?.data?.detail || err.message))
    }
  }).catch(() => {})
}

function viewDetail(id) {
  router.push(`/games/${id}`)
}

function editGame(id) {
  router.push(`/games/${id}/edit`)
}

function goToNew() {
  router.push('/games/new')
}

function goToScan() {
  router.push('/scan')
}

function getCoverUrl(cover) {
  if (!cover) return ''
  if (cover.startsWith('http')) return cover
  return cover
}

onMounted(() => {
  fetchGames()
})
</script>

<template>
  <div class="game-list-page">
    <div class="page-header">
      <h2 class="page-title">游戏列表</h2>
      <div class="header-actions">
        <el-button type="primary" @click="goToScan">
          <el-icon><Search /></el-icon>
          扫描目录
        </el-button>
        <el-button type="primary" @click="goToNew">
          <el-icon><Plus /></el-icon>
          添加游戏
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="search"
          placeholder="搜索游戏名称、开发商、简介..."
          clearable
          style="width: 320px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-input
          v-model="developer"
          placeholder="开发商筛选"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />
        <el-input
          v-model="tag"
          placeholder="标签筛选"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="table-card">
      <el-table
        :data="games"
        v-loading="loading"
        stripe
        style="width: 100%"
        @row-dblclick="(row) => viewDetail(row.id)"
      >
        <el-table-column label="封面" width="80" align="center">
          <template #default="{ row }">
            <div class="cover-thumb">
              <img
                v-if="row.cover"
                :src="getCoverUrl(row.cover)"
                class="cover-img"
              />
              <el-icon v-else :size="28" color="#94a3b8"><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="游戏名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="game-title-link" @click="viewDetail(row.id)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="original_title" label="日文原名" min-width="160" show-overflow-tooltip />
        <el-table-column prop="developer" label="开发商" width="150" show-overflow-tooltip />
        <el-table-column prop="tags" label="标签" width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag
              v-for="t in (row.tags || '').split(',').filter(Boolean)"
              :key="t"
              size="small"
              style="margin: 1px 2px"
            >
              {{ t.trim() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评分" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.rating > 0" class="rating">{{ row.rating.toFixed(1) }}</span>
            <span v-else class="no-rating">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row.id)">详情</el-button>
            <el-button size="small" @click="editGame(row.id)">编辑</el-button>
            <el-popconfirm
              title="确定删除？"
              @confirm="handleDelete(row.id, row.title)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @change="fetchGames"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.game-list-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.table-card {
  min-height: 400px;
}

.cover-thumb {
  width: 50px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.game-title-link {
  color: var(--accent);
  cursor: pointer;
  font-weight: 500;
}

.game-title-link:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

.rating {
  color: var(--warning);
  font-weight: 600;
}

.no-rating {
  color: var(--text-light);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
</style>