<template>
  <div class="mindmap-viewer">
    <div class="mindmap-container">
      <!-- 根节点 -->
      <div class="root-node">
        <div class="node-content root">
          <h2>{{ data.title || '文章分析' }}</h2>
        </div>
        
        <!-- 第一级分支 -->
        <div v-if="data.children && data.children.length" class="branches level-1">
          <div
            v-for="(child, index) in data.children"
            :key="`level1-${index}`"
            class="branch"
          >
            <div class="branch-line"></div>
            <div class="node-content level-1" :class="getNodeClass(index, data.children.length)">
              <h3>{{ child.title }}</h3>
            </div>
            
            <!-- 第二级分支 -->
            <div v-if="child.children && child.children.length" class="branches level-2">
              <div
                v-for="(subChild, subIndex) in child.children"
                :key="`level2-${index}-${subIndex}`"
                class="branch"
              >
                <div class="branch-line small"></div>
                <div class="node-content level-2">
                  <p>{{ subChild.title }}</p>
                  
                  <!-- 第三级分支（叶子节点） -->
                  <div v-if="subChild.children && subChild.children.length" class="leaves">
                    <div
                      v-for="(leaf, leafIndex) in subChild.children"
                      :key="`level3-${index}-${subIndex}-${leafIndex}`"
                      class="leaf"
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
    
    <!-- 操作按钮 -->
    <div class="mindmap-actions">
      <el-button-group>
        <el-button @click="zoomIn" size="small" :disabled="zoomLevel >= 1.5">
          <el-icon><ZoomIn /></el-icon>
          放大
        </el-button>
        <el-button @click="zoomOut" size="small" :disabled="zoomLevel <= 0.5">
          <el-icon><ZoomOut /></el-icon>
          缩小
        </el-button>
        <el-button @click="resetZoom" size="small">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </el-button-group>
      
      <el-button @click="downloadImage" type="primary" size="small">
        <el-icon><Download /></el-icon>
        导出图片
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const zoomLevel = ref(1)

const zoomIn = () => {
  if (zoomLevel.value < 1.5) {
    zoomLevel.value = Math.min(1.5, zoomLevel.value + 0.1)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value = Math.max(0.5, zoomLevel.value - 0.1)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
}

const getNodeClass = (index, total) => {
  const colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink']
  return `color-${colors[index % colors.length]}`
}

const downloadImage = async () => {
  try {
    // 这里可以实现截图功能，使用html2canvas库
    ElMessage.info('图片导出功能开发中...')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const containerStyle = computed(() => ({
  transform: `scale(${zoomLevel.value})`,
  transformOrigin: 'center top'
}))
</script>

<style scoped>
.mindmap-viewer {
  width: 100%;
  max-height: 800px;
  overflow: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fafafa;
  position: relative;
}

.mindmap-container {
  padding: 40px;
  display: flex;
  justify-content: center;
  min-height: 600px;
  transform: v-bind('containerStyle.transform');
  transform-origin: v-bind('containerStyle.transformOrigin');
  transition: transform 0.3s ease;
}

.root-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.node-content {
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background: white;
  margin: 8px;
  text-align: center;
  position: relative;
  z-index: 2;
}

.node-content.root {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  font-weight: bold;
  min-width: 200px;
}

.node-content.root h2 {
  margin: 0;
  font-size: 20px;
}

.node-content.level-1 {
  min-width: 160px;
  max-width: 220px;
}

.node-content.level-1 h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
}

.node-content.level-2 {
  min-width: 140px;
  max-width: 280px;
  background: #f8f9fa;
}

.node-content.level-2 p {
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
  color: #495057;
}

/* 颜色主题 */
.node-content.color-red { border-left: 4px solid #f56565; }
.node-content.color-blue { border-left: 4px solid #4299e1; }
.node-content.color-green { border-left: 4px solid #48bb78; }
.node-content.color-orange { border-left: 4px solid #ed8936; }
.node-content.color-purple { border-left: 4px solid #9f7aea; }
.node-content.color-pink { border-left: 4px solid #ed64a6; }

.branches {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  position: relative;
  margin-top: 20px;
}

.branches.level-1 {
  gap: 20px;
}

.branches.level-2 {
  flex-direction: column;
  align-items: flex-start;
  margin-top: 15px;
  gap: 10px;
  margin-left: 20px;
}

.branch {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.branches.level-2 .branch {
  align-items: flex-start;
  flex-direction: row;
}

.branch-line {
  position: absolute;
  background: #cbd5e0;
  z-index: 1;
}

.branches.level-1 > .branch > .branch-line {
  width: 2px;
  height: 20px;
  top: -20px;
}

.branches.level-2 > .branch > .branch-line {
  width: 20px;
  height: 2px;
  left: -20px;
  top: 50%;
  transform: translateY(-50%);
}

.leaves {
  margin-top: 10px;
  padding-left: 15px;
}

.leaf {
  margin: 4px 0;
  padding: 4px 8px;
  background: #e2e8f0;
  border-radius: 12px;
  font-size: 12px;
  display: inline-block;
  margin-right: 6px;
  margin-bottom: 6px;
  color: #4a5568;
  border: 1px solid #cbd5e0;
}

.mindmap-actions {
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

/* 连接线增强 */
.branches.level-1::before {
  content: '';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 2px;
  background: #cbd5e0;
  z-index: 0;
}

.branches.level-1 > .branch:first-child::after,
.branches.level-1 > .branch:last-child::after {
  content: '';
  position: absolute;
  top: -20px;
  width: 50%;
  height: 2px;
  background: #cbd5e0;
  z-index: 0;
}

.branches.level-1 > .branch:first-child::after {
  right: 0;
}

.branches.level-1 > .branch:last-child::after {
  left: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mindmap-container {
    padding: 20px;
  }
  
  .branches.level-1 {
    flex-direction: column;
    align-items: center;
  }
  
  .node-content.level-1,
  .node-content.level-2 {
    min-width: auto;
    max-width: 200px;
  }
  
  .mindmap-actions {
    position: relative;
    top: auto;
    right: auto;
    margin-top: 20px;
    justify-content: center;
  }
}
</style> 