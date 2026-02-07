import { createApp } from 'vue';
import Antd from 'ant-design-vue';
import App from './App.vue';

createApp(App)
    .use(Antd) // 使用 .use(Antd) 注册所有组件
    .mount('#app');