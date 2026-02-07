<script setup lang="ts">
import { ref } from "vue";
import { invoke } from "@tauri-apps/api/core";
// 导入 Antdv 组件和图标 (只保留 App.vue 自身需要的)
import { theme, Input, Button, Alert, TypographyTitle } from "ant-design-vue";
import * as icon from "@ant-design/icons-vue"; // 获取主题
let open_library = ref<boolean>(false);

const handleOk = (e: MouseEvent) => {
  open_library.value = false;
};
</script>

<template>
  <a-flex vertical class="param-panel">
    <div class="commond-list">
      <a-form layout="vertical">
        <a-form-item label="选择脚本" :colon="false">
          <a-cascader placeholder="请选择脚本" />
        </a-form-item>
      </a-form>
    </div>

    <div class="param-list">
      <a-input placeholder="请输入参数" />
    </div>
    <a-flex class="param-btn" horizontal align="center" justify="space-between">
      <a-button type="primary" ghost>
        <template #icon><component :is="icon.InboxOutlined" /></template>依赖</a-button
      >
      <a-button type="primary">
        <template #icon><component :is="icon.ThunderboltFilled" /></template>
        运行</a-button
      >
    </a-flex>
  </a-flex>

  <a-modal
    v-model:open="open_library"
    wrapClassName="library-modal"
    :footer="null"
    title="脚本库管理"
    @ok="handleOk"
  >
    <p>Some contents...</p>
    <a-divider />
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
    <p>Some contents...</p>
  </a-modal>
</template>

<style setup>
.param-panel {
  height: 100%;
  gap: 1rem;

  & > div {
    padding: 1rem;
    background-color: var(--primary-15-color);
    backdrop-filter: blur(12px);
    border-radius: 0.5rem;
  }

  .param-list {
    flex: 1;
  }

  .param-btn {
    height: 10%;
    min-height: 80px;
    text-align: center;
  }
}

.library-modal {
  height: 100%;
  overflow: hidden !important;
  .ant-modal {
    height: 100%;
    width: 100% !important;
    max-width: none;
    transform-origin: center center !important;
    top: 0;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    & > div {
      width: 90%;
      height: 80%;
      overflow: hidden;
    }
    .ant-modal-content {
      height: 100% !important;
      padding: 0;
      .ant-modal-header {
        padding: 20px 24px 0 24px;
      }
      .ant-modal-body {
        padding: 0px 4px 20px 24px;
        margin-right: 20px;
        height: 100% !important;
        overflow: auto;
      }
    }
  }
}
.ant-form {
  .ant-form-item:last-child {
    margin-bottom: 0 !important;
  }
}
</style>
