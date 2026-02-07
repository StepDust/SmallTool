// vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 确保你已经安装了 Vue 插件： npm install @vitejs/plugin-vue

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],

    // ⭐ 关键更改：强制 Vite 运行在指定的端口
    server: {
        port: 1420,
        strictPort: true,
    }
})