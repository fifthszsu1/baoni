<template>
  <div class="dashboard">
    <el-header class="header">
      <div class="header-left">
        <h1>英文文本分析系统</h1>
      </div>
      <div class="header-right">
        <el-button @click="goToChat" type="success" plain>
          <el-icon><ChatDotRound /></el-icon>
          AI助手
        </el-button>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-main>
        <div class="container">
          <!-- 文本输入区域 -->
          <div class="card">
            <h2>文本分析</h2>
            
            <!-- 输入方式选择 -->
            <el-tabs v-model="inputMethod" type="card" class="input-tabs">
              <el-tab-pane label="手动输入" name="manual">
                <el-form @submit.prevent="analyzeText">
                  <el-form-item label="英文文本">
                    <el-input
                      v-model="inputText"
                      type="textarea"
                      :rows="8"
                      placeholder="请输入需要分析的英文文本（至少50个字符）..."
                      maxlength="10000"
                      show-word-limit
                      resize="vertical"
                    />
                  </el-form-item>
                </el-form>
              </el-tab-pane>
              
              <el-tab-pane label="图片识别" name="ocr">
                <div class="ocr-upload-area">
                  <el-upload
                    ref="uploadRef"
                    class="image-uploader"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleImageSelect"
                    accept="image/*"
                    drag
                  >
                    <div v-if="!selectedImage" class="upload-placeholder">
                      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                      <div class="el-upload__text">
                        将图片拖拽到此处，或<em>点击上传</em>
                      </div>
                      <div class="el-upload__tip">
                        支持 PNG、JPG、JPEG、GIF、BMP、WEBP 格式，文件大小不超过 15MB<br>
                        <small style="color: #909399;">大图片将自动压缩以提高识别速度</small>
                      </div>
                    </div>
                    <div v-else class="image-preview">
                      <img :src="imagePreviewUrl" alt="上传的图片" />
                      <div class="image-actions">
                        <el-button @click="removeImage" type="danger" size="small">
                          <el-icon><Delete /></el-icon>
                          重新选择
                        </el-button>
                      </div>
                    </div>
                  </el-upload>
                  
                  <div v-if="selectedImage" class="ocr-actions">
                    <el-button
                      :loading="isExtracting"
                      type="success"
                      size="large"
                      @click="extractTextFromImage"
                    >
                      <el-icon><Camera /></el-icon>
                      <span v-if="!isExtracting">识别图片文字</span>
                      <span v-else>识别中...</span>
                    </el-button>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
            
            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button
                :loading="isAnalyzing"
                type="primary"
                size="large"
                @click="analyzeText"
                :disabled="inputText.length < 50"
              >
                <el-icon><Search /></el-icon>
                <span v-if="!isAnalyzing">分析文本</span>
                <span v-else>分析中...</span>
              </el-button>
              <el-button @click="clearText" :disabled="!inputText">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>
          </div>

          <!-- 分析结果区域 -->
          <div v-if="analysisResult" class="card">
            <h2>分析结果</h2>
            
            <!-- 标签页 -->
            <el-tabs v-model="activeTab" type="card">
              <!-- 隐藏专业思维导图tab - 代码保留备用 -->
              <!-- <el-tab-pane label="专业思维导图" name="d3mindmap">
                <D3Mindmap 
                  v-if="analysisResult.mindmap_data" 
                  :data="analysisResult.mindmap_data"
                />
                <el-empty v-else description="暂无思维导图数据" />
              </el-tab-pane> -->
              
              <!-- 隐藏XMind思维导图tab - 代码保留备用 -->
              <!-- <el-tab-pane label="XMind思维导图" name="xmind">
                <XMindViewer 
                  v-if="analysisResult.mindmap_data" 
                  :data="analysisResult.mindmap_data"
                />
                <el-empty v-else description="暂无思维导图数据" />
              </el-tab-pane> -->
              
              <el-tab-pane label="层级视图" name="mindmap">
                <MindmapViewer 
                  v-if="analysisResult.mindmap_data" 
                  :data="analysisResult.mindmap_data"
                />
                <el-empty v-else description="暂无思维导图数据" />
              </el-tab-pane>
              
              <el-tab-pane label="文字分析" name="text">
                <div class="analysis-text">
                  <el-scrollbar height="600px">
                    <div v-html="formatMarkdown(analysisResult.analysis)"></div>
                  </el-scrollbar>
                </div>
              </el-tab-pane>
            </el-tabs>
            
            <!-- 统计信息 -->
            <div class="analysis-stats">
              <el-tag type="info">
                Token使用量: {{ analysisResult.tokens_used || 0 }}
              </el-tag>
              <el-tag type="success">
                分析完成时间: {{ new Date().toLocaleString() }}
              </el-tag>
            </div>
          </div>

          <!-- 使用说明 -->
          <div v-if="!analysisResult" class="card">
            <h2>使用说明</h2>
            <el-steps :active="0" direction="vertical">
              <el-step title="选择输入方式" description="可以手动输入文本，或上传包含英文文章的图片进行识别" />
              <el-step title="输入内容" description="手动输入至少50个字符的英文文本，或上传清晰的英文文章图片" />
              <el-step title="开始分析" description="点击分析文本按钮，系统将使用AI分析文本结构和内容" />
              <el-step title="查看结果" description="分析完成后，可以查看思维导图和详细的文字分析" />
            </el-steps>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { api } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Search, Delete, User, ArrowDown, SwitchButton, 
  UploadFilled, Camera, ChatDotRound 
} from '@element-plus/icons-vue'
import MindmapViewer from '@/components/MindmapViewer.vue'
import XMindViewer from '@/components/XMindViewer.vue'
import D3Mindmap from '@/components/D3Mindmap.vue'

const router = useRouter()
const authStore = useAuthStore()

const inputText = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref(null)
const activeTab = ref('mindmap') // 默认显示层级视图

// OCR相关状态
const inputMethod = ref('manual') // 输入方式：manual 或 ocr
const selectedImage = ref(null)
const imagePreviewUrl = ref('')
const isExtracting = ref(false)
const uploadRef = ref(null)

const analyzeText = async () => {
  if (inputText.value.length < 50) {
    ElMessage.warning('文本长度至少需要50个字符')
    return
  }

  try {
    isAnalyzing.value = true
    const result = await api.analysis.analyzeText(inputText.value)
    
    if (result.success) {
      analysisResult.value = result
      activeTab.value = 'mindmap'
      ElMessage.success('分析完成')
    } else {
      ElMessage.error(result.error || '分析失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请检查网络连接')
  } finally {
    isAnalyzing.value = false
  }
}

const clearText = () => {
  inputText.value = ''
  analysisResult.value = null
}

// OCR相关方法
const handleImageSelect = (file) => {
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp']
  
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('不支持的图片格式，请选择 PNG、JPG、JPEG、GIF、BMP 或 WEBP 格式的图片')
    return
  }
  
  if (file.raw.size > 15 * 1024 * 1024) {
    ElMessage.error('图片文件大小不能超过 15MB')
    return
  }
  
  selectedImage.value = file.raw
  
  // 创建预览URL
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreviewUrl.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const removeImage = () => {
  selectedImage.value = null
  imagePreviewUrl.value = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 图片压缩函数
const compressImage = (file, quality = 0.7, maxWidth = 2000, maxHeight = 2000) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      // 计算新的尺寸
      let { width, height } = img
      
      if (width > maxWidth || height > maxHeight) {
        const ratio = Math.min(maxWidth / width, maxHeight / height)
        width *= ratio
        height *= ratio
      }
      
      canvas.width = width
      canvas.height = height
      
      // 绘制并压缩
      ctx.drawImage(img, 0, 0, width, height)
      
      canvas.toBlob((blob) => {
        // 给压缩后的Blob添加原始文件名，确保后端能正确识别文件类型
        const compressedFile = new File([blob], file.name, {
          type: 'image/jpeg',
          lastModified: Date.now()
        })
        resolve(compressedFile)
      }, 'image/jpeg', quality)
    }
    
    img.src = URL.createObjectURL(file)
  })
}

const extractTextFromImage = async () => {
  if (!selectedImage.value) {
    ElMessage.warning('请先选择图片')
    return
  }
  
  try {
    isExtracting.value = true
    ElMessage.info('正在识别图片中的文字，请稍候...')
    
    // 添加调试信息
    console.log('选中的图片:', selectedImage.value)
    console.log('图片类型:', selectedImage.value.type)
    console.log('图片大小:', selectedImage.value.size)
    
    // 如果图片大于5MB，先压缩
    let imageToUpload = selectedImage.value
    if (selectedImage.value.size > 5 * 1024 * 1024) {
      ElMessage.info('图片较大，正在压缩以提高识别速度...')
      imageToUpload = await compressImage(selectedImage.value, 0.7) // 压缩到70%质量
      console.log('压缩后图片大小:', imageToUpload.size)
    }
    
    const result = await api.analysis.extractTextFromImage(imageToUpload)
    
    if (result.success && result.extracted_text) {
      inputText.value = result.extracted_text
      inputMethod.value = 'manual' // 切换到手动输入tab显示结果
      ElMessage.success(`文字识别完成！识别出 ${result.extracted_text.length} 个字符`)
      
      // 清理图片选择
      removeImage()
    } else {
      ElMessage.error(result.error || '图片识别失败，请确保图片清晰且包含英文文本')
    }
  } catch (error) {
    console.error('图片识别失败:', error)
    
    // 根据错误类型提供更具体的错误信息
    let errorMessage = '图片识别失败，请稍后重试'
    
    if (error.response) {
      const status = error.response.status
      if (status === 413) {
        errorMessage = '图片文件过大，请选择更小的图片或等待自动压缩完成'
      } else if (status === 400) {
        errorMessage = error.response.data?.error || '请求参数错误，请检查图片格式'
      } else if (status === 500) {
        errorMessage = '服务器处理错误，请稍后重试'
      } else if (status === 401) {
        errorMessage = '登录已过期，请重新登录'
      }
    } else if (error.code === 'NETWORK_ERROR') {
      errorMessage = '网络连接错误，请检查网络连接'
    } else if (error.code === 'TIMEOUT') {
      errorMessage = '请求超时，图片可能过大，请尝试更小的图片'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    isExtracting.value = false
  }
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
        type: 'warning'
      })
      
      await authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  }
}

const goToChat = () => {
  router.push('/chat')
}

const formatMarkdown = (text) => {
  if (!text) return ''
  
  return text
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

onMounted(() => {
  // 验证token有效性
  authStore.verifyToken()
})
</script>

<style scoped>
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left h1 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-right .user-info:hover {
  color: #409eff;
}

.header-right .user-info .el-icon {
  margin: 0 5px;
}

.el-main {
  background: #f5f5f5;
  padding: 0;
}

.analysis-text {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.analysis-text :deep(h1) {
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.analysis-text :deep(h2) {
  color: #606266;
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 8px;
  margin: 20px 0 15px 0;
}

.analysis-text :deep(h3) {
  color: #909399;
  margin: 15px 0 10px 0;
}

.analysis-text :deep(li) {
  margin: 5px 0;
  list-style: none;
  position: relative;
  padding-left: 20px;
}

.analysis-text :deep(li:before) {
  content: "•";
  color: #409eff;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.analysis-stats {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}

.analysis-stats .el-tag {
  margin-right: 10px;
}

:deep(.el-tabs__content) {
  padding-top: 20px;
}

:deep(.el-steps) {
  padding: 20px;
}

/* OCR相关样式 */
.input-tabs {
  margin-bottom: 20px;
}

.ocr-upload-area {
  padding: 20px;
}

.image-uploader {
  width: 100%;
}

.upload-placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.upload-placeholder .el-icon--upload {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-placeholder .el-upload__text {
  font-size: 16px;
  margin-bottom: 8px;
}

.upload-placeholder .el-upload__tip {
  font-size: 12px;
  color: #c0c4cc;
}

.image-preview {
  position: relative;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 6px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.image-actions {
  margin-top: 15px;
}

.ocr-actions {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.action-buttons {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style> 