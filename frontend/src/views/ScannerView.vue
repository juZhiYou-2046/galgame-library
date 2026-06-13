<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { scanDirectory } from '../api/scanner'
import { createGame } from '../api/games'

const directory = ref('')
const maxDepth = ref(3)
const scanning = ref(false)
const scanResult = ref(null)
const addingGame = ref(false)
const addTargets = ref([])

async function handleScan() {
  if (!directory.value.trim()) {
    ElMessage.warning('请输入要扫描的目录路径')
    return
  }

  scanning.value = true
  scanResult.value = null
  addTargets.value = []

  try {
    const data = await scanDirectory(directory.value.trim(), maxDepth.value)
    scanResult.value = data
    if (data.files_found === 0) {
      ElMessage.info('未找到游戏文件')
    } else {
      ElMessage.success(`扫描完成，找到 ${data.files_found} 个文件`)
    }
  } catch (err) {
    ElMessage.error('扫描失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    scanning.value = false
  }
}

function toggleAddTarget(path) {
  const idx = addTargets.value.indexOf(path)
  if (idx >= 0) {
    addTargets.value.splice(idx, 1)
  } else {
    addTargets.value.push(path)
  }
}

function toggleAll() {
  if (!scanResult.value) return
  if (addTargets.value.length === scanResult.value.items.length) {
    addTargets.value = []
  } else {
    addTargets.value = scanResult.value.items.map(i => i.path)
  }
}

function guessTitleFromPath(path) {
  const parts = path.replace(/\\/g, '/').split('/')
  for (let i = parts.length - 2; i >= 0; i--) {
    const name = parts[i].trim()
    if (name && name !== '.' && name !== '..') return name
  }
  return parts[parts.length - 1]
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return size.toFixed(1) + ' ' + units[i]
}

async function addSelectedToLibrary() {
  if (addTargets.value.length === 0) {
    ElMessage.warning('请先选择要添加的文件')
    return
  }

  addingGame.value = true
  let successCount = 0
  let failCount = 0

  for (const filePath of addTargets.value) {
    try {
      const title = guessTitleFromPath(filePath)
      await createGame({
        title,
        folder_path: filePath,
        tags: '待整理',
      })
      successCount++
    } catch {
      failCount++
    }
  }

  addingGame.value = false
  ElMessage.success(`成功添加 ${successCount} 个游戏${failCount > 0 ? `，${failCount} 个失败` : ''}`)
  addTargets.value = []
  scanResult.value = null
  directory.value = ''
}

function getFileIcon(item) {
  const ext = (item.name || '').split('.').pop().toLowerCase()
  if (['exe'].includes(ext)) return 'Monitor'
  if (['iso', 'mdf', 'mds', 'ccd'].includes(ext)) return 'Disc'
  if (['cue', 'bin'].includes(ext)) return 'Folder'
  return 'Document'
}
</script>

<template>
  <div class="scan-page">
    <div class="page-header">
      <h2 class="page-title">扫描目录</h2>
    </div>

    <el-card shadow="never" class="scan-card">
      <div class="scan-form">
        <el-form label-width="100px">
          <el-form-item label="目录路径">
            <el-input
              v-model="directory"
              placeholder="输入要扫描的文件夹路径，如：/Users/username/Games"
              style="flex: 1"
            >
              <template #prefix>
                <el-icon><FolderOpened /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="扫描深度">
            <el-select v-model="maxDepth" style="width: 120px">
              <el-option :value="1" label="1级" />
              <el-option :value="2" label="2级" />
              <el-option :value="3" label="3级" />
              <el-option :value="5" label="5级" />
              <el-option :value="10" label="10级" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="scanning"
              @click="handleScan"
              size="large"
            >
              <el-icon><Search /></el-icon>
              开始扫描
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-card shadow="never" v-if="scanResult" class="result-card">
      <div class="result-header">
        <div class="result-info">
          <span class="result-dir">扫描目录: {{ scanResult.directory }}</span>
          <el-tag type="info">{{ scanResult.files_found }} 个文件</el-tag>
        </div>
        <div class="result-actions">
          <el-button size="small" @click="toggleAll">
            {{ addTargets.length === scanResult.items.length ? '取消全选' : '全选' }}
          </el-button>
          <el-button
            type="primary"
            size="small"
            :loading="addingGame"
            :disabled="addTargets.length === 0"
            @click="addSelectedToLibrary"
          >
            <el-icon><Plus /></el-icon>
            添加选中到库 ({{ addTargets.length }})
          </el-button>
        </div>
      </div>

      <el-table :data="scanResult.items" stripe style="width: 100%" max-height="480">
        <el-table-column width="44" align="center">
          <template #default="{ row }">
            <el-checkbox
              :checked="addTargets.includes(row.path)"
              @change="() => toggleAddTarget(row.path)"
            />
          </template>
        </el-table-column>
        <el-table-column label="文件名" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="file-name">
              <el-icon :size="16" color="#64748b" style="margin-right: 6px; flex-shrink: 0;">
                <component :is="getFileIcon(row)" />
              </el-icon>
              <span>{{ row.name || row.path.split('/').pop() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="路径" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="file-path">{{ row.path }}</span>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="100" align="right">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="!scanResult && !scanning" description="输入目录路径并点击扫描" :image-size="120" />
  </div>
</template>

<style scoped>
.scan-page {
  max-width: 960px;
}

.page-header {
  margin-bottom: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
}

.scan-card {
  margin-bottom: 16px;
}

.scan-form {
  padding: 8px 0;
}

.result-card {
  margin-bottom: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-dir {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: monospace;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.file-name {
  display: flex;
  align-items: center;
}

.file-path {
  font-family: monospace;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>