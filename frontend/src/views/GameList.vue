<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getGames, deleteGame } from '../api/games'
import { getExportUrl, importGames } from '../api/importExport'

const router = useRouter()
const route = useRoute()

const games = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')
const developer = ref('')
const tag = ref('')
const page = ref(1)
const pageSize = ref(20)

// 高级搜索
const showAdvanced = ref(false)
const sortBy = ref('updated_at')
const sortOrder = ref('desc')
const ratingRange = ref([0, 10])
const dateRange = ref(null)

async function fetchGames() {
  loading.value = true
  try {
    const params = {
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
    }
    if (search.value) params.search = search.value
    if (developer.value) params.developer = developer.value
    if (tag.value) params.tag = tag.value
    if (ratingRange.value[0] > 0) params.min_rating = ratingRange.value[0]
    if (ratingRange.value[1] < 10) params.max_rating = ratingRange.value[1]
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = formatDateParam(dateRange.value[0])
      params.end_date = formatDateParam(dateRange.value[1])
    }

    const data = await getGames(params)
    games.value = data.items
    total.value = data.total
  } catch (err) {
    ElMessage.error('获取游戏列表失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    loading.value = false
  }
}

function formatDateParam(date) {
  if (!date) return ''
  const d = new Date(date)
  return d.toISOString().split('T')[0]
}

function handleSearch() {
  page.value = 1
  fetchGames()
}

function resetFilters() {
  search.value = ''
  developer.value = ''
  tag.value = ''
  sortBy.value = 'updated_at'
  sortOrder.value = 'desc'
  ratingRange.value = [0, 10]
  dateRange.value = null
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

function filterByTag(tagName) {
  tag.value = tagName
  page.value = 1
  fetchGames()
}

// 导入导出相关
const showImportDialog = ref(false)
const importFile = ref(null)
const conflictStrategy = ref('skip')
const importing = ref(false)
const importResult = ref(null)

function handleExport(format) {
  window.open(getExportUrl(format), '_blank')
}

function handleImportFileChange(event) {
  importFile.value = event.target.files?.[0] || null
}

function openImportDialog() {
  importFile.value = null
  conflictStrategy.value = 'skip'
  importResult.value = null
  showImportDialog.value = true
}

async function handleImport() {
  if (!importFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  importing.value = true
  importResult.value = null
  try {
    importResult.value = await importGames(importFile.value, conflictStrategy.value)
    ElMessage.success(`导入完成: 新增 ${importResult.value.created}，更新 ${importResult.value.updated}，跳过 ${importResult.value.skipped}`)
    fetchGames()
  } catch (err) {
    ElMessage.error('导入失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    importing.value = false
  }
}

function getCoverUrl(cover) {
  if (!cover) return ''
  if (cover.startsWith('http')) return cover
  return cover
}

onMounted(() => {
  // 从 URL query 读取标签筛选参数（标签云跳转时使用）
  if (route.query.tag) {
    tag.value = route.query.tag
  }
  fetchGames()
})

// 监听 query 变化（从标签云页面跳转回来时）
watch(() => route.query.tag, (newTag) => {
  tag.value = newTag || ''
  page.value = 1
  fetchGames()
})
</script>

<template>
  <div class="game-list-page">
    <div class="page-header">
      <h2 class="page-title">游戏列表</h2>
      <div class="header-actions">
        <el-dropdown @command="handleExport" style="margin-right: 8px">
          <el-button>
            导出 <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="json">导出 JSON</el-dropdown-item>
              <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="openImportDialog">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
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
        <el-button text @click="showAdvanced = !showAdvanced">
          {{ showAdvanced ? '收起' : '高级搜索' }}
          <el-icon><ArrowDown v-if="!showAdvanced" /><ArrowUp v-else /></el-icon>
        </el-button>
      </div>

      <!-- 高级搜索面板 -->
      <div v-show="showAdvanced" class="advanced-filters">
        <div class="advanced-row">
          <span class="filter-label">排序:</span>
          <el-select v-model="sortBy" style="width: 130px" @change="handleSearch">
            <el-option value="updated_at" label="更新时间" />
            <el-option value="created_at" label="创建时间" />
            <el-option value="rating" label="评分" />
            <el-option value="title" label="标题" />
          </el-select>
          <el-select v-model="sortOrder" style="width: 90px" @change="handleSearch">
            <el-option value="desc" label="降序" />
            <el-option value="asc" label="升序" />
          </el-select>
        </div>
        <div class="advanced-row">
          <span class="filter-label">评分范围:</span>
          <el-slider
            v-model="ratingRange"
            range
            :min="0"
            :max="10"
            :step="0.5"
            style="width: 200px"
            @change="handleSearch"
          />
          <span class="range-text">{{ ratingRange[0] }} - {{ ratingRange[1] }}</span>
        </div>
        <div class="advanced-row">
          <span class="filter-label">发行日期:</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px"
            @change="handleSearch"
          />
        </div>
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
              style="margin: 1px 2px; cursor: pointer"
              @click.stop="filterByTag(t.trim())"
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

    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入游戏数据" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择文件">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept=".json,.csv"
            @change="handleImportFileChange"
          >
            <el-button>
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
          </el-upload>
          <span v-if="importFile" class="import-file-name">{{ importFile.name }}</span>
        </el-form-item>
        <el-form-item label="冲突策略">
          <el-radio-group v-model="conflictStrategy">
            <el-radio value="skip">跳过已存在的</el-radio>
            <el-radio value="update">覆盖更新</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <div v-if="importResult" class="import-result">
        <el-alert
          :title="`导入完成: 共 ${importResult.total} 条`"
          :type="importResult.errors.length ? 'warning' : 'success'"
          show-icon
          :closable="false"
        >
          <div>新增: {{ importResult.created }} | 更新: {{ importResult.updated }} | 跳过: {{ importResult.skipped }}</div>
          <div v-if="importResult.errors.length" style="margin-top: 4px">
            错误: {{ importResult.errors.join('; ') }}
          </div>
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="showImportDialog = false">关闭</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importFile" @click="handleImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>
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

.advanced-filters {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.advanced-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 60px;
}

.range-text {
  font-size: 13px;
  color: var(--text-secondary);
  min-width: 50px;
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

.import-file-name {
  margin-left: 8px;
  color: var(--text-secondary);
  font-size: 13px;
}

.import-result {
  margin-top: 16px;
}
</style>