<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getGame, createGame, updateGame } from '../api/games'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)
const submitting = ref(false)

const form = ref({
  title: '',
  original_title: '',
  developer: '',
  release_date: '',
  tags: '',
  description: '',
  rating: 0,
  folder_path: '',
})

const rules = {
  title: [
    { required: true, message: '请输入游戏名称', trigger: 'blur' },
    { min: 1, max: 255, message: '长度在 1 到 255 个字符', trigger: 'blur' },
  ],
  rating: [
    { type: 'number', min: 0, max: 10, message: '评分范围为 0-10', trigger: 'blur' },
  ],
}

const formRef = ref(null)

async function fetchGame() {
  if (!isEdit.value) return
  loading.value = true
  try {
    const game = await getGame(route.params.id)
    form.value = {
      title: game.title,
      original_title: game.original_title,
      developer: game.developer,
      release_date: game.release_date,
      tags: game.tags,
      description: game.description,
      rating: game.rating,
      folder_path: game.folder_path,
    }
  } catch (err) {
    ElMessage.error('获取游戏信息失败')
    router.push('/')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await updateGame(route.params.id, form.value)
      ElMessage.success('更新成功')
      router.push(`/games/${route.params.id}`)
    } else {
      const game = await createGame(form.value)
      ElMessage.success('添加成功')
      router.push(`/games/${game.id}`)
    }
  } catch (err) {
    ElMessage.error(isEdit.value ? '更新失败: ' : '添加失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  if (isEdit.value) {
    router.push(`/games/${route.params.id}`)
  } else {
    router.push('/')
  }
}

onMounted(fetchGame)
</script>

<template>
  <div class="form-page">
    <div class="page-header">
      <h2 class="page-title">{{ isEdit ? '编辑游戏' : '添加游戏' }}</h2>
    </div>

    <el-card shadow="never">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        v-loading="loading"
        style="max-width: 640px"
      >
        <el-form-item label="游戏名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入游戏名称" />
        </el-form-item>

        <el-form-item label="日文原名" prop="original_title">
          <el-input v-model="form.original_title" placeholder="游戏原名/日文名（选填）" />
        </el-form-item>

        <el-form-item label="开发商" prop="developer">
          <el-input v-model="form.developer" placeholder="开发商/品牌（选填）" />
        </el-form-item>

        <el-form-item label="发行日期" prop="release_date">
          <el-input v-model="form.release_date" placeholder="如：2024-01-15（选填）" />
        </el-form-item>

        <el-form-item label="评分" prop="rating">
          <el-rate
            v-model="form.rating"
            :max="10"
            show-score
            score-template="{value} 分"
            style="padding: 4px 0"
          />
        </el-form-item>

        <el-form-item label="标签" prop="tags">
          <el-input
            v-model="form.tags"
            placeholder="多个标签用逗号分隔，如：冒险,悬疑,催泪"
          />
        </el-form-item>

        <el-form-item label="文件夹路径" prop="folder_path">
          <el-input v-model="form.folder_path" placeholder="游戏文件所在文件夹路径（选填）" />
        </el-form-item>

        <el-form-item label="简介" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            placeholder="游戏简介（选填）"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button type="primary" :loading="submitting" @click="handleSubmit">
              {{ isEdit ? '保存修改' : '添加游戏' }}
            </el-button>
            <el-button @click="handleCancel">取消</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.form-page {
  max-width: 800px;
}

.page-header {
  margin-bottom: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}
</style>