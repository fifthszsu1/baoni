<template>
  <div class="dashboard">
    <el-header class="header">
      <div class="header-left">
        <h1>英文文本分析系统</h1>
      </div>
      <div class="header-right">
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
              <el-form-item>
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
              </el-form-item>
            </el-form>
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
              <el-step title="输入文本" description="在上方文本框中输入需要分析的英文文本，至少50个字符" />
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
import MindmapViewer from '@/components/MindmapViewer.vue'
import XMindViewer from '@/components/XMindViewer.vue'
import D3Mindmap from '@/components/D3Mindmap.vue'

const router = useRouter()
const authStore = useAuthStore()

const inputText = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref(null)
const activeTab = ref('mindmap') // 默认显示层级视图

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
</style> 