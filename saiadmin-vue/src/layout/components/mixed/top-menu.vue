<template>
  <a-layout-content class="sys-menus">
    <a-menu ref="MaMenuRef" mode="horizontal" class="layout-banner-menu hidden lg:flex" :popup-max-height="360" :selected-keys="actives">
      <template v-for="menu in props.modelValue" :key="menu.id">
        <template v-if="!menu.meta.hidden">
        <a-menu-item :key="menu.name" @click="routerPush(menu)">
          <template #icon v-if="menu.meta.icon">
            <sa-icon :icon="menu.meta.icon" :size="18" />
          </template>
          {{ appStore.i18n ? ( $t(`menus.${menu.name}`).indexOf('.') > 0 ? menu.meta.title : $t(`menus.${menu.name}`) ) : menu.meta.title }}
        </a-menu-item>
      </template>
      </template>
    </a-menu>
  </a-layout-content>
</template>
<script setup>
import { ref, watch, onMounted } from 'vue'
import { useTagStore, useAppStore } from '@/store'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({ modelValue: Array, active: String })

const router = useRouter()
const emits = defineEmits(['go'])
const appStore = useAppStore()
const tagStore = useTagStore()
const route = useRoute()
const actives = ref([ props.active ?? '' ])

watch(() => props.active, value => actives.value = [value])

const routerPush = (menu) => {
  actives.value = [menu.name]
  emits('go', menu)
}

const updateActive = (active) => actives.value = [active]

defineExpose({ updateActive })
</script>
  
<style>
  .sys-menus .icon {
    width: 1em;
    height: 1em;
  }

  .arco-menu-selected .icon {
    fill: rgb(var(--primary-6));
  }
</style>