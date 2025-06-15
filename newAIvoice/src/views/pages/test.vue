<template>
  <div class="test-container">
    <h2>JSON数据转换示例</h2>
    
    <!-- 数据展示区域 -->
    <div class="data-display">
      <h3>原始JSON数据：</h3>
      <pre>{{ jsonData }}</pre>
    </div>

    <!-- 转换后的文本预览 -->
    <div class="preview-section">
      <h3>转换后的文本预览：</h3>
      <div class="preview-content">
        <div v-for="(item, index) in formattedData" :key="index" class="preview-item">
          <h4>{{ item.title }}</h4>
          <p>{{ item.content }}</p>
          <p>作者：{{ item.author }}</p>
          <p>日期：{{ item.date }}</p>
          <hr>
        </div>
      </div>
    </div>

    <!-- 下载按钮区域 -->
    <div class="download-section">
      <el-button type="primary" @click="downloadTxt">
        <el-icon><Document /></el-icon>
        下载TXT文件
      </el-button>
      <el-button type="success" @click="downloadWord">
        <el-icon><Document /></el-icon>
        下载Word文件
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 示例JSON数据
const jsonData = ref({
  title: "示例文档",
  items: [
    {
      title: "第一章",
      content: "这是第一章的内容，包含了一些重要的信息。",
      author: "张三",
      date: "2024-03-20"
    },
    {
      title: "第二章",
      content: "这是第二章的内容，继续讲述更多细节。",
      author: "李四",
      date: "2024-03-21"
    },
    {
      title: "第三章",
      content: "这是最后一章的内容，总结全文要点。",
      author: "王五",
      date: "2024-03-22"
    }
  ]
})

// 格式化后的数据
const formattedData = ref(jsonData.value.items)

// 下载TXT文件
const downloadTxt = () => {
  try {
    // 构建文本内容
    let content = `${jsonData.value.title}\n\n`
    formattedData.value.forEach(item => {
      content += `${item.title}\n`
      content += `${item.content}\n`
      content += `作者：${item.author}\n`
      content += `日期：${item.date}\n`
      content += '-------------------\n\n'
    })

    // 创建Blob对象
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '文档.txt'
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('TXT文件下载成功')
  } catch (error) {
    console.error('下载TXT文件失败：', error)
    ElMessage.error('下载失败，请重试')
  }
}

// 下载Word文件
const downloadWord = () => {
  try {
    // 构建HTML内容
    let content = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" 
            xmlns:w="urn:schemas-microsoft-com:office:word" 
            xmlns="http://www.w3.org/TR/REC-html40">
      <head>
        <meta charset="utf-8">
        <title>${jsonData.value.title}</title>
      </head>
      <body>
        <h1>${jsonData.value.title}</h1>
    `

    formattedData.value.forEach(item => {
      content += `
        <h2>${item.title}</h2>
        <p>${item.content}</p>
        <p>作者：${item.author}</p>
        <p>日期：${item.date}</p>
        <hr>
      `
    })

    content += '</body></html>'

    // 创建Blob对象
    const blob = new Blob([content], { type: 'application/msword' })
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '文档.doc'
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('Word文件下载成功')
  } catch (error) {
    console.error('下载Word文件失败：', error)
    ElMessage.error('下载失败，请重试')
  }
}
</script>

<style scoped>
.test-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.data-display {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.data-display pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.preview-section {
  margin-bottom: 20px;
}

.preview-content {
  background-color: #fff;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.preview-item {
  margin-bottom: 15px;
}

.preview-item h4 {
  color: #409EFF;
  margin-bottom: 10px;
}

.preview-item p {
  margin: 5px 0;
  color: #606266;
}

.download-section {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

hr {
  border: none;
  border-top: 1px solid #dcdfe6;
  margin: 15px 0;
}
</style>