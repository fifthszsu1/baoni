<template>
  <div class="mindmap-viewer">
    <div class="mindmap-container">
      <!-- 根节点 -->
      <div class="root-node">
        <div class="node-content root">
          <h2>{{ data.title || '文章分析' }}</h2>
          <div v-if="articleStructure.type !== 'unknown'" class="article-type-badge">
            <span class="type-label">
              {{ getArticleTypeLabel(articleStructure) }}
            </span>
          </div>
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
      
      <el-button 
        @click="downloadImage" 
        type="primary" 
        size="small" 
        :loading="isExporting"
        :disabled="isExporting"
      >
        <el-icon v-if="!isExporting"><Download /></el-icon>
        {{ isExporting ? '导出中...' : '导出图片' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const zoomLevel = ref(1)

// 检测文体类型和结构
const articleStructure = computed(() => {
  if (!props.data || !props.data.children) return { type: 'unknown', structure: 'default' }
  
  const firstLevelTitles = props.data.children.map(child => child.title)
  
  // 检测7种新文体结构
  if (firstLevelTitles.some(title => title.includes('背景介绍') || title.includes('研究背景')) && 
      firstLevelTitles.some(title => title.includes('研究过程'))) {
    return { type: 'experimental-research', structure: 'research-report' }
  }
  
  if (firstLevelTitles.some(title => title.includes('提出论点')) && 
      firstLevelTitles.some(title => title.includes('进行论证')) &&
      firstLevelTitles.some(title => title.includes('得出结论'))) {
    return { type: 'theoretical-exposition', structure: 'argument-analysis' }
  }
  
  if (firstLevelTitles.some(title => title.includes('技术背景')) && 
      firstLevelTitles.some(title => title.includes('介绍技术')) &&
      firstLevelTitles.some(title => title.includes('发明前景'))) {
    return { type: 'technology-introduction', structure: 'tech-analysis' }
  }
  
  if (firstLevelTitles.some(title => title.includes('引出现象')) && 
      firstLevelTitles.some(title => title.includes('分析原因'))) {
    return { type: 'social-phenomenon', structure: 'phenomenon-analysis' }
  }
  
  if (firstLevelTitles.some(title => title.includes('提出问题')) && 
      firstLevelTitles.some(title => title.includes('解决措施'))) {
    return { type: 'problem-solution', structure: 'solution-analysis' }
  }
  
  if (firstLevelTitles.some(title => title.includes('现在发展历程')) && 
      firstLevelTitles.some(title => title.includes('过去发展历程'))) {
    return { type: 'social-development', structure: 'development-analysis' }
  }
  
  if (firstLevelTitles.some(title => title.includes('内容介绍')) && 
      firstLevelTitles.some(title => title.includes('图书评价')) &&
      firstLevelTitles.some(title => title.includes('发表观点'))) {
    return { type: 'book-review', structure: 'review-analysis' }
  }
  
  // 兼容旧格式 - 检测议论文结构
  if (firstLevelTitles.some(title => title.includes('论点')) && 
      firstLevelTitles.some(title => title.includes('论据')) && 
      firstLevelTitles.some(title => title.includes('总结'))) {
    return { type: 'argumentative', structure: 'argument' }
  }
  
  // 兼容旧格式 - 检测说明文结构
  if (firstLevelTitles.some(title => title.includes('概念') || title.includes('标准') || title.includes('特点'))) {
    return { type: 'expository', structure: 'classification' }
  }
  if (firstLevelTitles.some(title => title.includes('对象') || title.includes('角度') || title.includes('差异'))) {
    return { type: 'expository', structure: 'comparison' }
  }
  if (firstLevelTitles.some(title => title.includes('起始') || title.includes('步骤') || title.includes('结果'))) {
    return { type: 'expository', structure: 'process' }
  }
  if (firstLevelTitles.some(title => title.includes('现象') || title.includes('原因') || title.includes('影响'))) {
    return { type: 'expository', structure: 'causal' }
  }
  
  // 兼容旧格式
  if (firstLevelTitles.some(title => title.includes('What') || title.includes('Why') || title.includes('How'))) {
    return { type: 'legacy', structure: 'what-why-how' }
  }
  
  return { type: 'unknown', structure: 'default' }
})

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
  const structure = articleStructure.value
  
  // 根据文体类型选择不同的颜色方案
  if (structure.type === 'argumentative') {
    // 议论文：论点(红) - 论据(蓝) - 总结(绿)
    const argumentColors = ['red', 'blue', 'green']
    return `color-${argumentColors[index % argumentColors.length]} argumentative`
  } else if (structure.type === 'expository') {
    // 说明文：根据不同结构类型选择颜色
    if (structure.structure === 'classification') {
      // 分类说明：概念(紫) - 标准(橙) - 特点(青)
      const classificationColors = ['purple', 'orange', 'cyan']
      return `color-${classificationColors[index % classificationColors.length]} expository-classification`
    } else if (structure.structure === 'comparison') {
      // 对比说明：对象(红) - 角度(蓝) - 差异(绿)
      const comparisonColors = ['red', 'blue', 'green']
      return `color-${comparisonColors[index % comparisonColors.length]} expository-comparison`
    } else if (structure.structure === 'process') {
      // 流程说明：起始(绿) - 步骤(橙) - 结果(红)
      const processColors = ['green', 'orange', 'red']
      return `color-${processColors[index % processColors.length]} expository-process`
    } else if (structure.structure === 'causal') {
      // 因果说明：现象(蓝) - 原因(橙) - 影响(红)
      const causalColors = ['blue', 'orange', 'red']
      return `color-${causalColors[index % causalColors.length]} expository-causal`
    }
  } else if (structure.type === 'legacy') {
    // 兼容旧格式：What(蓝) - Why(橙) - How(绿)
    const legacyColors = ['blue', 'orange', 'green']
    return `color-${legacyColors[index % legacyColors.length]} legacy`
  }
  
  // 默认颜色方案
  const colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink']
  return `color-${colors[index % colors.length]}`
}

const getArticleTypeLabel = (structure) => {
  // 新的7种文体类型
  if (structure.type === 'experimental-research') {
    return '实验研究与报告'
  } else if (structure.type === 'theoretical-exposition') {
    return '事理阐释类论说文'
  } else if (structure.type === 'technology-introduction') {
    return '新兴技术介绍'
  } else if (structure.type === 'social-phenomenon') {
    return '社会发展新现象类'
  } else if (structure.type === 'problem-solution') {
    return '问题解决类说明文'
  } else if (structure.type === 'social-development') {
    return '社会发展与变迁类'
  } else if (structure.type === 'book-review') {
    return '书评'
  }
  // 兼容旧格式
  else if (structure.type === 'argumentative') {
    return '议论文结构'
  } else if (structure.type === 'expository') {
    const structureLabels = {
      'classification': '说明文 - 分类说明',
      'comparison': '说明文 - 对比说明', 
      'process': '说明文 - 流程说明',
      'causal': '说明文 - 因果说明'
    }
    return structureLabels[structure.structure] || '说明文'
  } else if (structure.type === 'legacy') {
    return '传统分析结构'
  }
  return '未知结构'
}

const isExporting = ref(false)

const downloadImage = async () => {
  if (isExporting.value) return
  
  try {
    isExporting.value = true
    ElMessage.info('正在生成图片，请稍候...')
    
    // 获取思维导图容器元素
    const mindmapContainer = document.querySelector('.mindmap-container')
    if (!mindmapContainer) {
      throw new Error('未找到思维导图容器')
    }
    
    // 临时重置缩放以确保完整导出
    const originalTransform = mindmapContainer.style.transform
    mindmapContainer.style.transform = 'scale(1)'
    
    // 等待DOM更新完成
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100)) // 额外等待确保样式应用
    
    // 使用html2canvas生成图片
    const canvas = await html2canvas(mindmapContainer, {
      backgroundColor: '#fafafa', // 设置背景色
      scale: 2, // 提高图片清晰度（2倍分辨率）
      useCORS: true, // 允许跨域图片
      allowTaint: true,
      width: mindmapContainer.scrollWidth,
      height: mindmapContainer.scrollHeight,
      scrollX: 0,
      scrollY: 0,
      // 确保捕获所有样式
      ignoreElements: (element) => {
        // 排除操作按钮区域
        return element.classList.contains('mindmap-actions')
      },
      // 优化渲染选项
      letterRendering: true,
      logging: false,
      imageTimeout: 15000,
      removeContainer: true
    })
    
    // 恢复原始缩放
    mindmapContainer.style.transform = originalTransform
    
    // 创建下载链接
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const filename = `思维导图_${(props.data.title || '文章分析').replace(/[<>:"/\\|?*]/g, '_')}_${timestamp}.png`
    link.download = filename
    link.href = canvas.toDataURL('image/png', 1.0)
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('图片导出成功！')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(`导出失败: ${error.message}`)
  } finally {
    isExporting.value = false
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

.article-type-badge {
  margin-top: 8px;
}

.type-label {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: normal;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.node-content.level-1 {
  min-width: 140px;
  max-width: 280px; /* 增加最大宽度以适应更长的内容 */
  width: auto; /* 根据内容自动调整宽度 */
}

.node-content.level-1 h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
}

.node-content.level-2 {
  min-width: 120px;
  max-width: 320px; /* 增加最大宽度 */
  width: auto; /* 根据内容自动调整 */
  background: #f8f9fa;
  word-wrap: break-word; /* 长单词自动换行 */
  hyphens: auto; /* 启用连字符换行 */
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
.node-content.color-cyan { border-left: 4px solid #38b2ac; }

/* 文体类型特殊样式 */
.node-content.argumentative {
  box-shadow: 0 2px 8px rgba(245, 101, 101, 0.15);
}

.node-content.expository-classification {
  box-shadow: 0 2px 8px rgba(159, 122, 234, 0.15);
}

.node-content.expository-comparison {
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.15);
}

.node-content.expository-process {
  box-shadow: 0 2px 8px rgba(72, 187, 120, 0.15);
}

.node-content.expository-causal {
  box-shadow: 0 2px 8px rgba(237, 137, 54, 0.15);
}

.node-content.legacy {
  opacity: 0.9;
  font-style: italic;
}

.branches {
  display: flex;
  justify-content: center;
  position: relative;
  margin-top: 20px;
}

.branches.level-1 {
  flex-wrap: nowrap; /* 确保不换行 */
  gap: 20px; /* 适当的间距 */
  width: 100%;
  max-width: 1400px; /* 增加最大宽度以适应更长的内容 */
  align-items: flex-start; /* 顶部对齐而不是强制底部对齐 */
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

.branches.level-1 > .branch {
  flex: 0 1 auto; /* 让每个分支根据内容自然调整大小 */
  min-width: 120px; /* 设置最小宽度避免过窄 */
  max-width: 300px; /* 设置最大宽度避免过宽 */
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
@media (max-width: 1024px) {
  .branches.level-1 {
    gap: 10px; /* 在中等屏幕上减少间距 */
  }
  
  .node-content.level-1 {
    min-width: 120px;
    max-width: 180px;
  }
}

@media (max-width: 768px) {
  .mindmap-container {
    padding: 20px;
  }
  
  .branches.level-1 {
    gap: 8px; /* 在小屏幕上进一步减少间距 */
  }
  
  .node-content.level-1 {
    min-width: 100px;
    max-width: 150px;
    font-size: 12px; /* 减小字体 */
  }
  
  .node-content.level-1 h3 {
    font-size: 12px;
  }
  
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

@media (max-width: 480px) {
  .branches.level-1 {
    gap: 5px;
  }
  
  .node-content.level-1 {
    min-width: 80px;
    max-width: 120px;
    padding: 8px 12px;
  }
  
  .node-content.level-1 h3 {
    font-size: 11px;
  }
}
</style> 