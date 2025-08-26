<template>
  <div class="d3-mindmap">
    <div class="toolbar">
      <el-button-group>
        <el-button @click="zoomIn" size="small">
          <el-icon><ZoomIn /></el-icon>
          放大
        </el-button>
        <el-button @click="zoomOut" size="small">
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
    
    <div ref="mindmapContainer" class="mindmap-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const mindmapContainer = ref(null)
let svg = null
let g = null
let zoom = null
let simulation = null

// 转换数据格式为D3树形结构
const transformData = (data) => {
  const transform = (node, depth = 0) => {
    const result = {
      id: Math.random().toString(36).substr(2, 9),
      name: node.title || '未命名',
      children: [],
      depth: depth,
      original: node
    }
    
    if (node.children && node.children.length > 0) {
      result.children = node.children.map(child => transform(child, depth + 1))
    }
    
    return result
  }
  
  return transform(data)
}

// 初始化思维导图
const initMindmap = () => {
  if (!mindmapContainer.value) return
  
  // 清除现有内容
  d3.select(mindmapContainer.value).selectAll('*').remove()
  
  const container = mindmapContainer.value
  const width = container.clientWidth
  const height = container.clientHeight
  
  // 创建SVG
  svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('background', 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)')
  
  // 创建缩放功能
  zoom = d3.zoom()
    .scaleExtent([0.1, 3])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })
  
  svg.call(zoom)
  
  // 创建主组
  g = svg.append('g')
  
  // 转换数据
  const treeData = transformData(props.data)
  
  // 创建树形布局
  const tree = d3.tree()
    .size([height - 100, width - 100])
    .separation((a, b) => (a.parent === b.parent ? 1 : 1.2))
  
  const root = d3.hierarchy(treeData)
  tree(root)
  
  // 创建连接线
  const links = g.selectAll('.link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal()
      .x(d => d.y)
      .y(d => d.x))
    .style('fill', 'none')
    .style('stroke', '#667eea')
    .style('stroke-width', 2)
    .style('opacity', 0.6)
  
  // 创建节点组
  const nodes = g.selectAll('.node')
    .data(root.descendants())
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.y},${d.x})`)
  
  // 创建节点圆圈
  nodes.append('circle')
    .attr('r', d => d.data.depth === 0 ? 8 : 6)
    .style('fill', d => {
      if (d.data.depth === 0) return '#667eea'
      if (d.data.depth === 1) return '#48bb78'
      if (d.data.depth === 2) return '#ed8936'
      return '#e2e8f0'
    })
    .style('stroke', '#fff')
    .style('stroke-width', 2)
  
  // 创建节点文本
  nodes.append('text')
    .attr('dy', d => d.data.depth === 0 ? '0.35em' : '0.35em')
    .attr('x', d => d.children ? -12 : 12)
    .style('text-anchor', d => d.children ? 'end' : 'start')
    .style('font-size', d => d.data.depth === 0 ? '14px' : '12px')
    .style('font-weight', d => d.data.depth === 0 ? 'bold' : 'normal')
    .style('fill', '#2d3748')
    .text(d => {
      const text = d.data.name
      return text.length > 20 ? text.substring(0, 20) + '...' : text
    })
    .append('title')
    .text(d => d.data.name)
  
  // 添加节点悬停效果
  nodes.on('mouseover', function(event, d) {
    d3.select(this).select('circle')
      .transition()
      .duration(200)
      .attr('r', d.data.depth === 0 ? 10 : 8)
      .style('stroke-width', 3)
  })
  .on('mouseout', function(event, d) {
    d3.select(this).select('circle')
      .transition()
      .duration(200)
      .attr('r', d.data.depth === 0 ? 8 : 6)
      .style('stroke-width', 2)
  })
  
  // 居中视图
  centerView()
}

// 缩放功能
const zoomIn = () => {
  svg.transition().duration(300).call(
    zoom.scaleBy, 1.3
  )
}

const zoomOut = () => {
  svg.transition().duration(300).call(
    zoom.scaleBy, 1 / 1.3
  )
}

const resetZoom = () => {
  svg.transition().duration(300).call(
    zoom.transform,
    d3.zoomIdentity
  )
}

const centerView = () => {
  if (!mindmapContainer.value) return
  
  const container = mindmapContainer.value
  const width = container.clientWidth
  const height = container.clientHeight
  
  const transform = d3.zoomIdentity
    .translate(width / 2, height / 2)
    .scale(0.8)
  
  svg.transition().duration(300).call(
    zoom.transform,
    transform
  )
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    initMindmap()
  })
}, { deep: true })

// 监听窗口大小变化
const handleResize = () => {
  nextTick(() => {
    initMindmap()
  })
}

onMounted(() => {
  initMindmap()
  window.addEventListener('resize', handleResize)
})

// 清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.d3-mindmap {
  width: 100%;
  height: 800px;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
}

.toolbar {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  gap: 10px;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mindmap-container {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.mindmap-container:active {
  cursor: grabbing;
}

/* D3样式 */
:deep(.link) {
  transition: stroke-opacity 0.3s ease;
}

:deep(.link:hover) {
  stroke-opacity: 1;
  stroke-width: 3;
}

:deep(.node text) {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  pointer-events: none;
}

:deep(.node circle) {
  transition: all 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .d3-mindmap {
    height: 600px;
  }
  
  .toolbar {
    top: 5px;
    right: 5px;
    padding: 6px;
  }
}
</style> 