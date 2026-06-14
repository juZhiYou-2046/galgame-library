<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTags } from '../api/tags'

const router = useRouter()
const tags = ref([])
const loading = ref(false)

async function fetchTags() {
  loading.value = true
  try {
    tags.value = await getTags()
  } catch (err) {
    ElMessage.error('获取标签失败')
  } finally {
    loading.value = false
  }
}

function getTagSize(count) {
  // 根据标签出现次数计算字号
  if (count >= 10) return 'large'
  if (count >= 5) return 'default'
  return 'small'
}

function getTagColor(index) {
  // 根据索引分配稳定颜色
  const colors = ['', 'success', 'warning', 'info', 'danger']
  return colors[index % colors.length]
}

function filterByTag(tagName) {
  router.push({ path: '/', query: { tag: tagName } })
}

onMounted(fetchTags)
</script>

<template>
  <div class="tag-cloud-page">
    <div class="page-header">
      <h2 class="page-title">标签管理</h2>
      <span class="tag-count">共 {{ tags.length }} 个标签</span>
    </div>

    <el-card shadow="never" v-loading="loading">
      <div v-if="tags.length === 0 && !loading" class="empty-state">
        暂无标签，请先为游戏添加标签
      </div>
      <div v-else class="tag-cloud">
        <el-tag
          v-for="(tag, index) in tags"
          :key="tag.name"
          :size="getTagSize(tag.count)"
          :type="getTagColor(index)"
          class="cloud-tag"
          @click="filterByTag(tag.name)"
        >
          {{ tag.name }}
          <span class="tag-count-badge">{{ tag.count }}</span>
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.tag-cloud-page {
  max-width: 1000px;
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

.tag-count {
  color: var(--text-light);
  font-size: 14px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 8px 0;
}

.cloud-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.cloud-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-count-badge {
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.7;
}

.empty-state {
  text-align: center;
  color: var(--text-light);
  padding: 60px 0;
  font-size: 15px;
}
</style>
