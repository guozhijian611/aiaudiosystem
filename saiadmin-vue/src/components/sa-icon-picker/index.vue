<template>
    <div class="w-full">
      <a-input-group class="w-full">
        <a-input placeholder="请点击右侧按钮选择图标" v-if="props.preview" allow-clear v-model="currentIcon" />
        <div class="icon-container" v-if="props.preview">
          <sa-icon :icon="currentIcon" v-if="currentIcon" />
        </div>
        <a-button type="primary" @click="() => (visible = true)">选择图标</a-button>
      </a-input-group>
  
      <a-modal v-model:visible="visible" width="800px" draggable :footer="false">
        <template #title>选择图标</template>
        <a-tabs class="tabs">
          <a-tab-pane key="arco" title="Arco Design">
            <ul class="arco">
              <li v-for="icon in arcodesignIcons" :key="icon" @click="selectIcon(icon, 'arco')">
                <component :is="icon" />
              </li>
            </ul>
          </a-tab-pane>
          <a-tab-pane key="bi" title="Bootstrap Icons">
            <ul class="arco">
              <li v-for="icon in biData" :key="icon" @click="selectIcon(icon, 'iconify')">
                <Icon :icon="icon" />
              </li>
            </ul>
          </a-tab-pane>
        </a-tabs>
      </a-modal>
    </div>
  </template>
  
  <script setup>
  import { reactive, ref, computed } from 'vue'
  import * as arcoIcons from '@arco-design/web-vue/es/icon'
  import { Icon } from '@iconify/vue';
  import biData from "./iconify/bi.json";
  
  const arcodesignIcons = reactive([])
  const visible = ref(false)
  
  const props = defineProps({
    modelValue: { type: String },
    preview: { type: Boolean, default: true },
  })
  
  const emit = defineEmits(['update:modelValue'])
  
  const currentIcon = computed({
    get() {
      return props.modelValue
    },
    set(value) {
      // html标签名不能以数字开头
      if ((/^[^\d].*/.test(value) && value) || !value) {
        emit('update:modelValue', value)
      }
    },
  })
  
  for (let icon in arcoIcons) {
    arcodesignIcons.push(icon)
  }
  
  arcodesignIcons.pop()
  
  const selectIcon = (icon, className) => {
    currentIcon.value = icon
    visible.value = false
  }
  
  const handlerChange = (value) => {
    selectIcon(value, '')
  }
  </script>
  
  <style scoped lang="less">
  .icon-container {
    width: 50px;
    height: 32px;
    background-color: var(--color-fill-1);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .icon {
    width: 1em;
    fill: var(--color-text-1);
  }
  
  .tabs {
    ul {
      display: flex;
      flex-wrap: wrap;
      padding-left: 7px;
    }
  
    li {
      border: 2px solid var(--color-fill-4);
      margin-bottom: 10px;
      margin-right: 6px;
      padding: 5px;
      cursor: pointer;
    }
  
    li:hover,
    li.active {
      border: 2px solid rgb(var(--primary-6));
    }
  
    & li svg {
      width: 2.4em;
      height: 2.4em;
    }
  }
  :deep(.arco-select-option-content) {
    width: 100%;
  }
  </style>
  