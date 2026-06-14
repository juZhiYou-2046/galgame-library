<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getGame, deleteGame, uploadCover } from '../api/games'
import { getReviews, createReview, deleteReview } from '../api/reviews'

const route = useRoute()
const router = useRouter()

const game = ref(null)
const loading = ref(false)
const uploadLoading = ref(false)
const fileInput = ref(null)

// 评价相关
const reviews = ref([])
const reviewForm = ref({ rating: 0, content: '', reviewer: '' })
const submittingReview = ref(false)
const showReviewForm = ref(false)

async function fetchGame() {
  loading.value = true
  try {
    game.value = await getGame(route.params.id)
  } catch (err) {
    ElMessage.error('获取游戏详情失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

function handleDelete() {
  ElMessageBox.confirm(`确定要删除《${game.value.title}》吗？此操作不可恢复。`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteGame(game.value.id)
      ElMessage.success('删除成功')
      router.push('/')
    } catch (err) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

function editGame() {
  router.push(`/games/${route.params.id}/edit`)
}

function goBack() {
  router.push('/')
}

function getCoverUrl(cover) {
  if (!cover) return ''
  if (cover.startsWith('http')) return cover
  return cover
}

function parseTags(tags) {
  return (tags || '').split(',').filter(Boolean).map(t => t.trim())
}

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    ElMessage.warning('图片大小不能超过 5MB')
    return
  }

  uploadLoading.value = true
  try {
    const updated = await uploadCover(game.value.id, file)
    game.value = updated
    ElMessage.success('封面上传成功')
  } catch (err) {
    ElMessage.error('封面上传失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    uploadLoading.value = false
    event.target.value = '' // 清空 input 以便重复选择同一文件
  }
}

// 评价功能
async function fetchReviews() {
  try {
    reviews.value = await getReviews(route.params.id)
  } catch {
    reviews.value = []
  }
}

async function submitReview() {
  if (reviewForm.value.rating === 0) {
    ElMessage.warning('请选择评分')
    return
  }
  submittingReview.value = true
  try {
    await createReview(route.params.id, reviewForm.value)
    ElMessage.success('评价提交成功')
    reviewForm.value = { rating: 0, content: '', reviewer: '' }
    showReviewForm.value = false
    await fetchReviews()
    await fetchGame() // 刷新平均分
  } catch (err) {
    ElMessage.error('评价提交失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    submittingReview.value = false
  }
}

async function handleDeleteReview(reviewId) {
  try {
    await deleteReview(route.params.id, reviewId)
    ElMessage.success('评价已删除')
    await fetchReviews()
    await fetchGame()
  } catch {
    ElMessage.error('删除评价失败')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchGame()
  fetchReviews()
})
</script>

<template>
  <div class="detail-page">
    <div v-loading="loading" class="detail-container">
      <div class="detail-header">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <div class="detail-actions" v-if="game">
          <el-button type="primary" @click="editGame">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" @click="handleDelete">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
      </div>

      <template v-if="game">
        <el-card shadow="never" class="detail-main">
          <div class="detail-content">
            <div class="cover-section">
              <div class="cover-wrapper" @click="triggerUpload">
                <img
                  v-if="game.cover"
                  :src="getCoverUrl(game.cover)"
                  class="cover-image"
                />
                <div v-else class="cover-placeholder">
                  <el-icon :size="48" color="#94a3b8"><Picture /></el-icon>
                  <span>暂无封面</span>
                </div>
                <div class="cover-overlay" v-if="!uploadLoading">
                  <el-icon :size="24"><Upload /></el-icon>
                  <span>{{ game.cover ? '更换封面' : '上传封面' }}</span>
                </div>
                <div class="cover-overlay" v-else>
                  <el-icon :size="24" class="is-loading"><Loading /></el-icon>
                  <span>上传中...</span>
                </div>
              </div>
              <input
                ref="fileInput"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                style="display: none"
                @change="handleFileChange"
              />
            </div>
            <div class="info-section">
              <h1 class="game-title">{{ game.title }}</h1>
              <p v-if="game.original_title" class="game-original-title">{{ game.original_title }}</p>

              <div class="info-grid">
                <div class="info-item" v-if="game.developer">
                  <span class="info-label">开发商</span>
                  <span class="info-value">{{ game.developer }}</span>
                </div>
                <div class="info-item" v-if="game.release_date">
                  <span class="info-label">发行日期</span>
                  <span class="info-value">{{ game.release_date }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">评分</span>
                  <span class="info-value">
                    <el-rate
                      v-model="game.rating"
                      disabled
                      show-score
                      score-template="{value} 分"
                      :max="10"
                    />
                  </span>
                </div>
                <div class="info-item" v-if="game.folder_path">
                  <span class="info-label">文件夹</span>
                  <span class="info-value folder-path">{{ game.folder_path }}</span>
                </div>
              </div>

              <div class="tags-section" v-if="parseTags(game.tags).length">
                <span class="info-label">标签</span>
                <div class="tags-list">
                  <el-tag
                    v-for="t in parseTags(game.tags)"
                    :key="t"
                    style="margin: 2px 4px 2px 0"
                  >
                    {{ t }}
                  </el-tag>
                </div>
              </div>

              <div class="description-section" v-if="game.description">
                <span class="info-label">简介</span>
                <p class="description-text">{{ game.description }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </template>
    </div>

    <!-- 评价区域 -->
    <template v-if="game">
      <el-card shadow="never" class="review-card">
        <div class="review-header">
          <h3 class="section-title">用户评价 ({{ reviews.length }})</h3>
          <el-button type="primary" size="small" @click="showReviewForm = !showReviewForm">
            {{ showReviewForm ? '取消' : '写评价' }}
          </el-button>
        </div>

        <!-- 写评价表单 -->
        <div v-if="showReviewForm" class="review-form">
          <el-form label-width="80px">
            <el-form-item label="评分">
              <el-rate v-model="reviewForm.rating" :max="10" show-score score-template="{value} 分" />
            </el-form-item>
            <el-form-item label="评论者">
              <el-input v-model="reviewForm.reviewer" placeholder="你的名字（选填）" style="width: 200px" />
            </el-form-item>
            <el-form-item label="评论内容">
              <el-input v-model="reviewForm.content" type="textarea" :rows="3" placeholder="写下你的评价..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submittingReview" @click="submitReview">提交评价</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 评价列表 -->
        <div v-if="reviews.length === 0 && !showReviewForm" class="no-reviews">
          暂无评价，来写第一个评价吧
        </div>
        <div v-else class="review-list">
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-meta">
              <el-rate v-model="review.rating" disabled :max="10" size="small" />
              <span class="reviewer-name">{{ review.reviewer || '匿名用户' }}</span>
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
              <el-button size="small" type="danger" text @click="handleDeleteReview(review.id)">删除</el-button>
            </div>
            <p v-if="review.content" class="review-content">{{ review.content }}</p>
          </div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.detail-page {
  max-width: 900px;
}

.detail-container {
  min-height: 400px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-actions {
  display: flex;
  gap: 8px;
}

.detail-main {
  overflow: visible;
}

.detail-content {
  display: flex;
  gap: 32px;
}

.cover-section {
  flex-shrink: 0;
}

.cover-wrapper {
  position: relative;
  width: 240px;
  height: 340px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-md);
  cursor: pointer;
}

.cover-wrapper:hover .cover-overlay {
  opacity: 1;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--text-light);
  font-size: 13px;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 13px;
  opacity: 0;
  transition: opacity 0.2s;
}

.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.info-section {
  flex: 1;
  min-width: 0;
}

.game-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.game-original-title {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
}

.folder-path {
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
}

.tags-section {
  margin-bottom: 20px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  margin-top: 8px;
}

.description-section {
  margin-top: 4px;
}

.description-text {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .detail-content {
    flex-direction: column;
    align-items: center;
  }

  .cover-wrapper {
    width: 180px;
    height: 260px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

.review-card {
  margin-top: 16px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.review-form {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 16px;
}

.no-reviews {
  text-align: center;
  color: var(--text-light);
  padding: 32px 0;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.review-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.reviewer-name {
  font-weight: 500;
  color: var(--text-primary);
}

.review-date {
  font-size: 12px;
  color: var(--text-light);
}

.review-content {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  white-space: pre-wrap;
}
</style>