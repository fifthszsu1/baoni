<template>
  <div class="xmind-viewer">
    <div class="mindmap-container" :style="containerStyle">
      <!-- 中心主题 -->
      <div class="central-topic">
        <div class="topic-content central">
          <h2>{{ data.title || '文章分析' }}</h2>
        </div>
        
        <!-- 主要分支 -->
        <div v-if="data.children && data.children.length" class="main-branches">
          <div
            v-for="(branch, index) in data.children"
            :key="`branch-${index}`"
            class="main-branch"
            :style="getBranchStyle(index, data.children.length)"
          >
            <!-- 分支线 -->
            <div class="branch-line"></div>
            
            <!-- 分支主题 -->
            <div class="topic-content branch" :class="getTopicClass(index)">
              <h3>{{ branch.title }}</h3>
            </div>
            
            <!-- 子分支 -->
            <div v-if="branch.children && branch.children.length" class="sub-branches">
              <div
                v-for="(subBranch, subIndex) in branch.children"
                :key="`sub-${index}-${subIndex}`"
                class="sub-branch"
              >
                <div class="sub-branch-line"></div>
                <div class="topic-content sub-topic">
                  <p>{{ subBranch.title }}</p>
                  
                  <!-- 叶子节点 -->
                  <div v-if="subBranch.children && subBranch.children.length" class="leaf-topics">
                    <div
                      v-for="(leaf, leafIndex) in subBranch.children"
                      :key="`leaf-${index}-${subIndex}-${leafIndex}`"
                      class="leaf-topic"
                    >
                      <span>{{ leaf.title }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <el-button-group>
        <el-button @click="zoomIn" size="small" :disabled="zoomLevel >= 2">
          <el-icon><ZoomIn /></el-icon>
          放大
        </el-button>
        <el-button @click="zoomOut" size="small" :disabled="zoomLevel <= 0.3">
          <el-icon><ZoomOut /></el-icon>
          缩小
        </el-button>
        <el-button @click="resetZoom" size="small">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </el-button-group>
      
      <el-button @click="centerView" type="primary" size="small">
        <el-icon><Aim /></el-icon>
        居中
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const zoomLevel = ref(1)
const offsetX = ref(0)
const offsetY = ref(0)

const zoomIn = () => {
  if (zoomLevel.value < 2) {
    zoomLevel.value = Math.min(2, zoomLevel.value + 0.1)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.3) {
    zoomLevel.value = Math.max(0.3, zoomLevel.value - 0.1)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
  offsetX.value = 0
  offsetY.value = 0
}

const centerView = () => {
  offsetX.value = 0
  offsetY.value = 0
}

const getTopicClass = (index) => {
  const colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink']
  return `topic-${colors[index % colors.length]}`
}

const getBranchStyle = (index, total) => {
  const angle = (360 / total) * index
  return {
    transform: `rotate(${angle}deg)`
  }
}

const containerStyle = computed(() => ({
  transform: `scale(${zoomLevel.value}) translate(${offsetX.value}px, ${offsetY.value}px)`,
  transformOrigin: 'center center'
}))
</script>

<style scoped>
.xmind-viewer {
  width: 100%;
  height: 800px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
}

.mindmap-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease;
}

.central-topic {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.topic-content {
  padding: 12px 20px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  text-align: center;
  position: relative;
  z-index: 2;
  margin: 8px;
  min-width: 120px;
  max-width: 300px;
}

.topic-content.central {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  font-weight: bold;
  min-width: 200px;
}

.topic-content.central h2 {
  margin: 0;
  font-size: 20px;
}

.topic-content.branch {
  background: white;
  border: 3px solid;
  font-weight: 600;
}

.topic-content.sub-topic {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  font-size: 14px;
}

.topic-content.sub-topic p {
  margin: 0;
  line-height: 1.4;
}

/* 主题颜色 */
.topic-red { border-color: #f56565; }
.topic-blue { border-color: #4299e1; }
.topic-green { border-color: #48bb78; }
.topic-orange { border-color: #ed8936; }
.topic-purple { border-color: #9f7aea; }
.topic-pink { border-color: #ed64a6; }

.main-branches {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
}

.main-branch {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-origin: center;
  width: 200px;
  height: 200px;
}

.branch-line {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: translateY(-50%);
  z-index: 1;
}

.sub-branches {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.sub-branch {
  position: relative;
  display: flex;
  align-items: center;
}

.sub-branch-line {
  width: 20px;
  height: 2px;
  background: #cbd5e0;
  margin-right: 10px;
}

.leaf-topics {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.leaf-topic {
  padding: 4px 8px;
  background: #e2e8f0;
  border-radius: 12px;
  font-size: 12px;
  color: #4a5568;
  border: 1px solid #cbd5e0;
  white-space: nowrap;
}

.control-panel {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-branches {
    width: 400px;
    height: 400px;
  }
  
  .main-branch {
    width: 150px;
    height: 150px;
  }
  
  .topic-content {
    min-width: 100px;
    max-width: 200px;
    font-size: 12px;
  }
}
</style> 