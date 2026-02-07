<script setup>
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
import ParamPanda from "../components/ParamPanda.vue";

// 导入 Antdv 组件和图标 (只保留 App.vue 自身需要的)
import { theme, Input, Button, Alert, TypographyTitle } from "ant-design-vue";
import * as icon from "@ant-design/icons-vue";
// 获取主题
const { useToken } = theme;
const { token } = useToken();

// region 侧边栏拖拽逻辑
const sidebarWidth = ref(270);
const isDragging = ref(false);

function startResize(e) {
  isDragging.value = true;
  document.addEventListener("mousemove", onResize);
  document.addEventListener("mouseup", stopResize);
  // 防止拖拽时选中文本
  document.body.style.userSelect = "none";
}

function onResize(e) {
  if (!isDragging.value) return;
  // 减去右侧固定侧边栏宽度
  const sider = document.querySelector(".ant-layout-sider-children");
  const siderWidth = sider ? sider.offsetWidth : 0;
  // 限制最小宽度为 270px，最大宽度为窗口的一半 (可根据需要调整)
  const newWidth = e.clientX - siderWidth - 16; // 减去右侧固定侧边栏宽度及 1rem（16px）间距
  if (newWidth > 270 && newWidth < window.innerWidth * 0.5) {
    sidebarWidth.value = newWidth;
  }
}

function stopResize() {
  isDragging.value = false;
  document.removeEventListener("mousemove", onResize);
  document.removeEventListener("mouseup", stopResize);
  document.body.style.userSelect = "";
}
// endregion
</script>

<template>
  <a-flex horizontal align="center" class="run-content">
    <div
      class="app-param"
      :style="{ width: sidebarWidth + 'px', minWidth: '150px' }"
    ></div>

    <!-- 拖拽手柄 -->
    <div class="resize-handle" @mousedown="startResize">
      <a-button type="primary">
        <component :is="icon.HolderOutlined" />
      </a-button>
    </div>

    <div class="app-log">2</div>
  </a-flex>
</template>

<style scoped>
.run-content {
  height: 100%;
  gap: 1rem;
  & > div {
    height: 100%;
  }
}

.app-log {
  flex: 1;
  background-color: var(--primary-15-color);
  backdrop-filter: blur(12px);
  border-radius: 0.5rem;
  padding: 1rem;
}

.resize-handle {
  width: 0;
  cursor: col-resize;
  background-color: transparent;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 -0.5rem;
  z-index: 9;

  button {
    background: color-mix(in srgb, var(--primary-color) 50%, transparent);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 0;
    backdrop-filter: blur(12px);
    box-shadow: none;
  }
}
</style>
