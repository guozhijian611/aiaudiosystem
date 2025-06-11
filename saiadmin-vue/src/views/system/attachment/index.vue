<template>
  <div class="ma-content-block lg:flex justify-between">
    <div class="w-full p-4 pr-4 border-r border-gray-100 lg:w-2/12">
      <sa-tree-slider
        :data="sliderData"
        :border="false"
        search-placeholder="搜索资源类型"
        :field-names="{ title: 'label', key: 'value' }"
        @click="handlerClick"
        icon="icon-folder"
        v-model="defaultKey" />
    </div>

    <div class="lg:w-10/12 w-full">
      <!-- CRUD 组件 -->
      <sa-table ref="crudRef" :options="options" :columns="columns" :searchForm="searchForm">
        <!-- 搜索区 start -->
        <template #tableSearch>
          <a-col :sm="7" :xs="24">
            <a-form-item field="origin_name" label="原文件名">
              <a-input v-model="searchForm.origin_name" placeholder="请输入原文件名" allow-clear />
            </a-form-item>
          </a-col>
          <a-col :sm="7" :xs="24">
            <a-form-item field="storage_mode" label="存储模式">
              <sa-select v-model="searchForm.storage_mode" dict="upload_mode" placeholder="请选择存储模式" />
            </a-form-item>
          </a-col>
          <a-col :sm="10" :xs="24">
            <a-form-item field="create_time" label="上传时间">
              <a-range-picker v-model="searchForm.create_time" />
            </a-form-item>
          </a-col>
        </template>
        <!-- 搜索区 end -->
        <!-- 表格按钮后置扩展 -->
        <template #tableAfterButtons>
          <a-input-group v-if="mode === 'window'">
            <a-button @click="selectAll">
              <template #icon><icon-select-all /></template>全选
            </a-button>
            <a-button @click="flushAll">
              <template #icon><icon-eraser /></template>清除
            </a-button>
          </a-input-group>
        </template>
        <!-- 工具按钮扩展 -->
        <template #tools>
          <a-tooltip :content="mode === 'list' ? '切换橱窗模式' : '切换列表模式'">
            <a-button shape="circle" @click="switchMode"
              ><icon-apps v-if="mode === 'list'" /><icon-list v-else
            /></a-button>
          </a-tooltip>
        </template>
        <!-- 自定义内容 -->
        <template #crudContent="tableData">
          <a-checkbox-group v-if="mode === 'window'" v-model="selecteds" @change="handlerChange">
            <a-image-preview-group infinite>
              <a-space class="window-list">
                <template v-for="record in tableData.data" :key="record.id">
                  <div class="mb-2 image-content">
                    <a-checkbox :value="record.id" class="checkbox">
                      <template #checkbox="{ checked }">
                        <a-tag :checked="checked" color="arcoblue" checkable><icon-check /> 选择</a-tag>
                      </template>
                    </a-checkbox>
                    
                    <!-- 图片文件 -->
                    <a-image
                      v-if="isImage(record.mime_type)"
                      width="190"
                      height="190"
                      show-loader
                      :title="record.origin_name"
                      :description="`大小：${record.size_info}`"
                      :src="tool.attachUrl(record.url)">
                      <template #extra>
                        <div class="actions">
                          <a-tooltip content="下载此文件">
                            <span class="action" @click="download(record)"><icon-download /></span>
                          </a-tooltip>
                          <a-tooltip>
                            <span class="action"><icon-info-circle /></span>
                            <template #content>
                              <div>存储名称：{{ record.object_name }}</div>
                              <div>存储目录：{{ record.storage_path }}</div>
                              <div>上传时间：{{ record.create_time }}</div>
                              <div>存储模式：{{ tool.getLabel(record.storage_mode, dictList['upload_mode']) }}</div>
                            </template>
                          </a-tooltip>
                        </div>
                      </template>
                    </a-image>
                    
                    <!-- 视频文件 -->
                    <div v-else-if="isVideo(record.mime_type)" class="media-container">
                      <video
                        width="190"
                        height="190"
                        controls
                        preload="metadata"
                        :title="record.origin_name"
                        style="object-fit: contain; background-color: var(--color-fill-4); border-radius: 2px;">
                        <source :src="tool.attachUrl(record.url)" :type="record.mime_type">
                        您的浏览器不支持视频播放
                      </video>
                      <div class="media-info">
                        <div class="media-title">{{ record.origin_name }}</div>
                        <div class="media-size">大小：{{ record.size_info }}</div>
                      </div>
                      <div class="actions">
                        <a-tooltip content="播放视频">
                          <span class="action" @click="playMedia(record)"><icon-play-arrow /></span>
                        </a-tooltip>
                        <a-tooltip content="下载此文件">
                          <span class="action" @click="download(record)"><icon-download /></span>
                        </a-tooltip>
                        <a-tooltip>
                          <span class="action"><icon-info-circle /></span>
                          <template #content>
                            <div>存储名称：{{ record.object_name }}</div>
                            <div>存储目录：{{ record.storage_path }}</div>
                            <div>上传时间：{{ record.create_time }}</div>
                            <div>存储模式：{{ tool.getLabel(record.storage_mode, dictList['upload_mode']) }}</div>
                          </template>
                        </a-tooltip>
                      </div>
                    </div>
                    
                    <!-- 音频文件 -->
                    <div v-else-if="isAudio(record.mime_type)" class="media-container">
                      <div class="audio-preview">
                        <div class="audio-icon">
                          <icon-music style="font-size: 48px; color: var(--color-text-3)" />
                        </div>
                        <audio
                          controls
                          preload="metadata"
                          style="width: 170px; margin-top: 10px;"
                          :title="record.origin_name">
                          <source :src="tool.attachUrl(record.url)" :type="record.mime_type">
                          您的浏览器不支持音频播放
                        </audio>
                      </div>
                      <div class="media-info">
                        <div class="media-title">{{ record.origin_name }}</div>
                        <div class="media-size">大小：{{ record.size_info }}</div>
                      </div>
                      <div class="actions">
                        <a-tooltip content="播放音频">
                          <span class="action" @click="playMedia(record)"><icon-play-arrow /></span>
                        </a-tooltip>
                        <a-tooltip content="下载此文件">
                          <span class="action" @click="download(record)"><icon-download /></span>
                        </a-tooltip>
                        <a-tooltip>
                          <span class="action"><icon-info-circle /></span>
                          <template #content>
                            <div>存储名称：{{ record.object_name }}</div>
                            <div>存储目录：{{ record.storage_path }}</div>
                            <div>上传时间：{{ record.create_time }}</div>
                            <div>存储模式：{{ tool.getLabel(record.storage_mode, dictList['upload_mode']) }}</div>
                          </template>
                        </a-tooltip>
                      </div>
                    </div>
                    
                    <!-- 其他文件类型 -->
                    <div v-else class="file-container">
                      <div class="file-preview">
                        <a-avatar shape="square" style="width: 64px; height: 64px; font-size: 20px;">
                          {{ record.suffix || 'FILE' }}
                        </a-avatar>
                      </div>
                      <div class="media-info">
                        <div class="media-title">{{ record.origin_name }}</div>
                        <div class="media-size">大小：{{ record.size_info }}</div>
                      </div>
                      <div class="actions">
                        <a-tooltip content="下载此文件">
                          <span class="action" @click="download(record)"><icon-download /></span>
                        </a-tooltip>
                        <a-tooltip>
                          <span class="action"><icon-info-circle /></span>
                          <template #content>
                            <div>存储名称：{{ record.object_name }}</div>
                            <div>存储目录：{{ record.storage_path }}</div>
                            <div>上传时间：{{ record.create_time }}</div>
                            <div>存储模式：{{ tool.getLabel(record.storage_mode, dictList['upload_mode']) }}</div>
                          </template>
                        </a-tooltip>
                      </div>
                    </div>
                  </div>
                </template>
              </a-space>
            </a-image-preview-group>
          </a-checkbox-group>
        </template>
        <!-- 自定义table渲染 -->
        <template #url="{ record }">
          <!-- 图片文件 -->
          <a-image
            class="list-image"
            v-if="isImage(record.mime_type)"
            width="40px"
            height="40px"
            :src="tool.attachUrl(record.url)" />
          
          <!-- 视频文件 -->
          <div v-else-if="isVideo(record.mime_type)" class="list-video-container">
            <video
              width="40px"
              height="40px"
              :src="tool.attachUrl(record.url)"
              style="object-fit: cover; border-radius: 2px; cursor: pointer;"
              @click="$event.target.play()"
              @mouseenter="$event.target.controls = true"
              @mouseleave="$event.target.controls = false">
            </video>
          </div>
          
          <!-- 音频文件 -->
          <div v-else-if="isAudio(record.mime_type)" class="list-audio-container">
            <a-avatar shape="square" style="top: 0px; background-color: var(--color-primary-light-1);">
              <icon-music />
            </a-avatar>
          </div>
          
          <!-- 其他文件 -->
          <a-avatar v-else shape="square" style="top: 0px">{{ record.suffix }}</a-avatar>
        </template>
        <!-- 操作列前置扩展 -->
        <template #operationBeforeExtend="{ record }">
          <a-link v-if="isVideo(record.mime_type) || isAudio(record.mime_type)" @click="playMedia(record)">
            <icon-play-arrow /> 播放
          </a-link>
          <a-link @click="download(record)"><icon-download /> 下载</a-link>
        </template>
      </sa-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, nextTick, h } from 'vue'
import api from '@/api/system/attachment'
import commonApi from '@/api/common'
import { Message, Modal } from '@arco-design/web-vue'
import tool from '@/utils/tool'
import { useDictStore } from '@/store'

const dictList = useDictStore().data

const crudRef = ref()
const mode = ref('list')
const defaultKey = ref(['all'])
const sliderData = ref([])
const selecteds = ref([])

// 文件类型检测
const isImage = (mimeType) => /^image\//i.test(mimeType)
const isVideo = (mimeType) => /^video\//i.test(mimeType)
const isAudio = (mimeType) => /^audio\//i.test(mimeType)

// 分类搜索点击
const handlerClick = async (value) => {
  defaultKey.value = value
  const type = value[0] === 'all' ? undefined : value[0]
  searchForm.value.mime_type = type
  crudRef.value.refresh()
}

// 模式切换
const switchMode = () => {
  mode.value = mode.value === 'list' ? 'window' : 'list'
}

// 下载
const download = async (record) => {
  const response = await commonApi.downloadById(record.id)
  if (response) {
    tool.download(response, record.origin_name)
    Message.success('请求成功，文件开始下载')
  } else {
    Message.error('文件下载失败')
  }
}

// 选中事件
const handlerChange = (val) => {
  selecteds.value = val
  crudRef.value.setSelecteds(val)
}

// 全选
const selectAll = () => {
  crudRef.value.getTableData().map((item) => selecteds.value.push(item.id))
  crudRef.value.setSelecteds(selecteds.value)
}

// 清除选中
const flushAll = () => {
  selecteds.value = []
  crudRef.value.clearSelected()
}

// 播放媒体文件
const playMedia = (record) => {
  if (isVideo(record.mime_type)) {
    // 为视频创建播放弹窗
    Modal.info({
      title: '视频播放 - ' + record.origin_name,
      content: () => h('video', {
        src: tool.attachUrl(record.url),
        controls: true,
        autoplay: true,
        style: 'width: 100%; max-height: 400px;'
      }),
      width: 600,
      footer: false,
    })
  } else if (isAudio(record.mime_type)) {
    // 为音频创建播放弹窗
    Modal.info({
      title: '音频播放 - ' + record.origin_name,
      content: () => h('div', { style: 'text-align: center; padding: 20px;' }, [
        h('div', { style: 'margin-bottom: 20px;' }, [
          h('icon-music', { style: 'font-size: 64px; color: var(--color-primary);' })
        ]),
        h('audio', {
          src: tool.attachUrl(record.url),
          controls: true,
          autoplay: true,
          style: 'width: 100%;'
        })
      ]),
      width: 500,
      footer: false,
    })
  }
}

// 搜索表单
const searchForm = ref({
  origin_name: '',
  mime_type: '',
  storage_mode: '',
  create_time: [],
})

// SaTable 基础配置
const options = reactive({
  api: api.getPageList,
  rowSelection: { showCheckedAll: true },
  singleLine: true,
  delete: {
    show: true,
    auth: ['/core/attachment/destroy'],
    func: async (params) => {
      const resp = await api.destroy(params)
      if (resp.code === 200) {
        Message.success(`删除成功！`)
        crudRef.value?.refresh()
      }
    },
  },
})

// SaTable 列配置
const columns = reactive([
  { title: '预览', dataIndex: 'url', width: 80 },
  { title: '存储名称', dataIndex: 'object_name', width: 220 },
  { title: '原文件名', dataIndex: 'origin_name', width: 150 },
  { title: '存储模式', dataIndex: 'storage_mode', dict: 'upload_mode', width: 100 },
  { title: '资源类型', dataIndex: 'mime_type', width: 130 },
  { title: '存储目录', dataIndex: 'storage_path', width: 130 },
  { title: '文件大小', dataIndex: 'size_info', width: 130 },
  { title: '上传时间', dataIndex: 'create_time', width: 180 },
])

// 页面加载完成执行
onMounted(async () => {
  const treeData = dictList['attachment_type']
  sliderData.value = [{ label: '所有', value: 'all' }, ...treeData]
  crudRef.value?.refresh()
})
</script>

<script>
export default { name: 'system:attachment' }
</script>

<style scoped>
:deep(.arco-image-img) {
  object-fit: contain;
  background-color: var(--color-fill-4);
}
:deep(.arco-image-with-footer-inner .arco-image-footer) {
  padding: 9px;
}
:deep(.arco-image-footer-caption-title) {
  font-size: 14px;
}
:deep(.arco-image-footer-extra) {
  position: relative;
}
:deep(.arco-avatar-square) {
  top: -6px;
}
.window-list {
  display: flex;
  width: 100%;
  flex-wrap: wrap;
  flex-direction: row;
  align-content: center;
}
.image-content {
  position: relative;
}
.image-content .checkbox {
  position: absolute;
  z-index: 10;
  right: -16px;
  color: #fff;
}
:deep(.arco-tag-checkable) {
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
}
.actions {
  display: flex;
  align-items: center;
  position: absolute;
  right: 9px;
  bottom: -24px;
}
.action {
  padding: 5px 4px;
  font-size: 14px;
  margin-left: 6px;
  border-radius: 2px;
  line-height: 1;
  cursor: pointer;
}
.action:first-child {
  margin-left: 0;
}

.action:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 媒体容器样式 */
.media-container {
  position: relative;
  width: 190px;
  height: 190px;
  border-radius: 2px;
  overflow: hidden;
  background-color: var(--color-fill-4);
}

.media-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  color: white;
  font-size: 12px;
}

.media-title {
  font-weight: 500;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.media-size {
  opacity: 0.8;
}

/* 音频预览样式 */
.audio-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 150px;
  background-color: var(--color-fill-2);
}

.audio-icon {
  margin-bottom: 10px;
}

/* 文件容器样式 */
.file-container {
  position: relative;
  width: 190px;
  height: 190px;
  border-radius: 2px;
  overflow: hidden;
  background-color: var(--color-fill-4);
}

.file-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 150px;
  background-color: var(--color-fill-2);
}

/* 列表模式媒体样式 */
.list-video-container {
  position: relative;
  display: inline-block;
}

.list-video-container video {
  transition: all 0.2s ease;
}

.list-video-container:hover video {
  transform: scale(1.1);
}

.list-audio-container {
  display: inline-block;
}
</style>
