<template>
  <a-modal v-model:visible="visible" @cancel="close" @before-ok="submit">
    <template #title>菜单权限</template>
    <a-form :model="form">
      <a-form-item label="角色名称" field="name">
        <a-input disabled v-model="form.name" />
      </a-form-item>
      <a-form-item label="角色标识" field="code">
        <a-input disabled v-model="form.code" />
      </a-form-item>
      <a-form-item label="菜单列表" field="menu_ids">
        <a-spin :loading="loading" tip="菜单加载中..." class="w-full">
          <div class="w-full">
            <a-space class="mt-1.5" size="large">
              <a-checkbox @change="handlerExpand">展开/折叠</a-checkbox>
              <a-checkbox @change="handlerSelect">全选/全不选</a-checkbox>
              <a-checkbox v-model="cancelLinkage" @change="handlerLinkage">关闭父子级联动</a-checkbox>
            </a-space>
            <div class="tree-container">
              <sa-tree-slider
                ref="tree"
                :data="menuList"
                checkable
                :fieldNames="{ title: 'label', key: 'id' }"
                searchPlaceholder="过滤菜单"
                v-model:checked-keys="selectKeys"
                :check-strictly="cancelLinkage"
                :virtual-list-props="{ height: 300 }"
                @click="handlerClick" />
            </div>
          </div>
        </a-spin>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref } from 'vue'
import role from '@/api/system/role'
import menu from '@/api/system/menu'
import { Message } from '@arco-design/web-vue'

const visible = ref(false)
const loading = ref(true)
const menuList = ref([])
const selectKeys = ref([])
const cancelLinkage = ref(false)
const tree = ref()
const form = ref({ name: undefined, code: undefined })

const emit = defineEmits(['success'])

// 打开弹窗
const open = async (row) => {
  visible.value = true
  form.value = { id: row.id, name: row.name, code: row.code }
  handlerExpand(false)
  handlerSelect(false)
  handlerLinkage(false)
  await setData(row.id)
}

// 展开/折叠
const handlerExpand = (value) => {
  tree.value.saTree.expandAll(value)
}

// 全选/取消全选
const handlerSelect = (value) => {
  tree.value.saTree.checkAll(value)
}

// 关联/取消关联
const handlerLinkage = (value) => {
  cancelLinkage.value = value
}

// 点击树节点
const handlerClick = (value) => {
  const t = tree.value.saTree
  const nodes = t.getExpandedNodes().map((item) => item.id)
  t.expandNode(value, nodes.includes(value[0]) ? false : true)
}

// 获取数据
const setData = async (roleId) => {
  loading.value = true
  const menuResponse = await menu.accessMenu({ tree: true })
  menuList.value = menuResponse.data
  const roleResponse = await role.getMenuByRole(roleId)
  selectKeys.value = roleResponse.data.menus.map((item) => item.id)
  selectKeys.value.length > 0 && handlerLinkage(true)
  loading.value = false
}

// 数据保存
const submit = async (done) => {
  const nodes = tree.value.saTree.getCheckedNodes()
  const ids = nodes.map((item) => item.id)
  const response = await role.updateMenuPermission(form.value.id, { menu_ids: ids })
  response.code === 200 && Message.success(response.message)
  emit('success')
  done(true)
}

const close = () => (visible.value = false)

defineExpose({ open })
</script>

<style scoped>
.tree-container {
  border: 1px solid var(--color-fill-2);
  max-height: 350px;
  padding-bottom: 8px;
  margin-top: 5px;
}
</style>
