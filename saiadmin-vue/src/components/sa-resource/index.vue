<template>
  <div class="w-full resource-container h-full lg:flex lg:justify-between rounded-sm">
    <a-modal v-model:visible="openNetworkModal" ok-text="保存" :on-before-ok="saveNetworkImg" draggable>
      <template #title>保存网络图片</template>
      <a-input v-model="networkImg" class="mb-3" placeholder="请粘贴网络图片地址" allow-clear />
      <a-image :src="networkImg" width="100%" style="min-height: 150px" />
    </a-modal>
    <div class="w-full lg:mt-2 flex flex-col">
      <div class="lg:flex lg:justify-between">
        <div class="flex">
          <sa-upload-file v-model="uploadFile" multiple :show-list="false" />
          <a-button class="ml-3" @click="openNetworkModal = true"> <icon-image /> 保存网络图片 </a-button>
          <a-radio-group type="button" v-model="defaultKey" @change="handlerClick" class="ml-4">
            <a-radio v-for="(item, index) in sliderData" :key="index" :value="item.value">{{ item.label }}</a-radio>
          </a-radio-group>
        </div>
        <a-input v-model="filename" class="input-search lg:mt-0 mt-2" placeholder="文件名搜索" @press-enter="searchFile" />
      </div>
      <a-spin :loading="resourceLoading" tip="资源加载中" class="h-full">
        <div class="resource-list mt-2" ref="rl" v-if="attachmentList && attachmentList.length > 0">
          <div class="item rounded-sm" v-for="(item, index) in attachmentList" :key="item.hash" @click="selectFile(item, index)">
            <img :src="!/^(http|https)/g.test(item.url) ? $tool.attachUrl(item.url) : item.url" v-if="item.mime_type.indexOf('image') !== -1" />
            <div v-else class="text-3xl w-full h-full flex items-center justify-center">
              {{ `.${item.suffix}` }}
            </div>
            <a-tooltip position="bottom">
              <div class="file-name">
                {{ item.origin_name }}
              </div>
              <template #content>
                <div>存储名称：{{ item.object_name }}</div>
                <div>存储目录：{{ item.storage_path }}</div>
                <div>上传时间：{{ item.create_time }}</div>
                <div>文件大小：{{ item.size_info }}</div>
                <div>存储模式：{{ tool.getLabel(item.storage_mode, dictList['upload_mode']) }}</div>
              </template>
            </a-tooltip>
          </div>
        </div>
        <a-empty v-else class="mt-10" />
      </a-spin>
      <div class="lg:flex lg:justify-between">
        <a-pagination :total="pageInfo.total" v-model:current="pageInfo.currentPage" v-model:page-size="pageSize" @change="changePage" />
        <a-button type="primary" @click="selectComplete" class="mt-3 lg:mt-0">确定</a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import commonApi from '@/api/common'
import tool from '@/utils/tool'
import { Message } from '@arco-design/web-vue'
import { useDictStore } from '@/store'

const dictList = useDictStore().data

const sliderData = ref([])
const defaultKey = ref('all')
const uploadFile = ref()
const attachmentList = ref([])
const openNetworkModal = ref(false)
const networkImg = ref()
const pageInfo = ref({
  total: 1,
  currentPage: 1,
})
const resourceLoading = ref(true)
const pageSize = ref(21)
const filename = ref()
const selecteds = ref()
const rl = ref()

const emit = defineEmits(['update:modelValue'])

const props = defineProps({
  modelValue: { type: [String, Array] },
  multiple: { type: Boolean, default: true },
  onlyData: { type: Boolean, default: true },
  returnType: { type: String, default: 'url' },
})

onMounted(async () => {
  const treeData = dictList['attachment_type']
  sliderData.value = [{ label: '所有', value: 'all' }, ...treeData]
  await getAttachmentList({ page: 1 })

  if (props.multiple) {
    selecteds.value = []
  }
})

const getAttachmentList = async (params = {}) => {
  const requestParams = Object.assign(params, { limit: pageSize.value })
  resourceLoading.value = true
  const response = await commonApi.getResourceList(requestParams)
  pageInfo.value = {
    total: response?.data?.total ?? 0,
    currentPage: response?.data?.current_page ?? 21,
  }
  attachmentList.value = response?.data?.data
  resourceLoading.value = false
}

const handlerClick = async (val) => {
  defaultKey.value = val
  const type = val === 'all' ? undefined : val
  await getAttachmentList({ mime_type: type })
}

const searchFile = async () => {
  await getAttachmentList({ origin_name: filename.value })
}

const selectFile = (item, index) => {
  const children = rl.value.children
  const className = 'item rounded-sm'

  if (!/^(http|https)/g.test(item.url)) {
    item.url = tool.attachUrl(item.url)
  }
  if (children[index].className.indexOf('active') !== -1) {
    children[index].className = className
    if (props.multiple) {
      selecteds.value.map((file, idx) => {
        selecteds.value.splice(idx, 1)
      })
    } else {
      selecteds.value = ''
    }
  } else {
    if (props.multiple) {
      children[index].className = className + ' active'
      selecteds.value.push(props.onlyData ? item[props.returnType] : item)
    } else {
      if (document.querySelectorAll('.item.active').length < 1) {
        children[index].className = className + ' active'
        selecteds.value = props.onlyData ? item[props.returnType] : item
      }
    }
  }
}

const clearSelecteds = () => {
  if (rl.value && rl.value.children) {
    const children = rl.value.children
    for (let i = 0; i < children.length; i++) {
      children[i].className = 'item rounded-sm'
    }
  }
  if (props.multiple) {
    selecteds.value = []
  } else {
    selecteds.value = undefined
  }
}

const selectComplete = () => {
  const files = props.multiple ? Object.assign([], selecteds.value) : selecteds.value
  emit('update:modelValue', files)
}

const changePage = async (page) => {
  await getAttachmentList({ page })
}

const saveNetworkImg = async (done) => {
  if (!networkImg.value) {
    Message.error('输入地址不能为空')
    done(false)
    return
  }
  const response = await commonApi.saveNetWorkImage({ url: networkImg.value })
  if (response.code === 200) {
    Message.success(response.message)
    await getAttachmentList()
    networkImg.value = undefined
    done(true)
  } else {
    Message.error(response.message)
    done(false)
  }
}

watch(
  () => uploadFile,
  async () => await getAttachmentList(),
  { deep: true }
)

defineExpose({ clearSelecteds })
</script>

<style scoped lang="less">
.resource-container {
  min-height: 560px;
}
.input-search {
  width: 250px;
}
.resource-list {
  display: flex;
  width: 100%;
  flex-wrap: wrap;
  flex-direction: row;
  align-content: center;
  .item {
    width: 138px;
    height: 138px;
    border: 2px solid var(--color-fill-1);
    margin-right: 10px;
    margin-bottom: 20px;
    background-color: var(--color-fill-1);
    cursor: pointer;
    position: relative;
    .file-name {
      position: absolute;
      bottom: 0px;
      height: 23px;
      width: 100%;
      background: rgba(100, 100, 100, 0.3);
      line-height: 23px;
      font-size: 12px;
      overflow: hidden;
      padding: 0 10px;
      text-align: center;
      text-overflow: ellipsis;
      color: #fff;
    }
    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
  }
  .item:hover {
    border: 2px solid rgb(var(--primary-6));
  }
  .item.active {
    border: 2px solid rgb(var(--primary-6));
  }
  .item.active::after {
    content: '';
    position: absolute;
    width: 134px;
    height: 134px;
    z-index: 2;
    top: 0;
    background: rgba(var(--primary-5), 0.2);
  }
}
</style>
