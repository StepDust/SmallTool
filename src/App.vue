<script setup lang="ts">
import { watch, onMounted, onBeforeUnmount, h, ref, computed } from "vue";
import CliRun from "./views/cliRun.vue";
import LibraryManager from "./views/libraryManager.vue";
import * as icon from "@ant-design/icons-vue";
import { theme, MenuProps } from "ant-design-vue";
import Pickr from "@simonwep/pickr";
import "@simonwep/pickr/dist/themes/nano.min.css";

// ==================== 界面属性 ====================
let props = defineProps({
  title: { type: String, default: "SmallTool" },
  logo: { type: String, default: new URL("./assets/logo.svg", import.meta.url).href },
  topIcon: { type: [Object, Function, String], default: () => icon.PushpinFilled },
  minIcon: { type: [Object, Function, String], default: () => icon.MinusOutlined },
  maxIcon: { type: [Object, Function, String], default: () => icon.BorderOutlined },
  restoreIcon: {
    type: [Object, Function, String],
    default: () => icon.FullscreenExitOutlined,
  },
  closeIcon: { type: [Object, Function, String], default: () => icon.CloseOutlined },
});

// 图标处理
let logoSvg = ref("");
watch(
  () => props.logo,
  (url) => {
    if (!url) return;
    fetch(url)
      .then((res) => res.text())
      .then((svg) => {
        // 关键：确保 fill 使用 currentColor
        svg = svg
          .replace(/width="[^"]*"/, "")
          .replace(/height="[^"]*"/, "")
          .replace(/fill="[^"]*"/g, 'fill="currentColor"');

        logoSvg.value = svg;
      });
  },
  { immediate: true }
);

// ==================== 主题状态（持久化）===================

const STORAGE_KEY = "custom-theme";
// 获取主题
const { useToken } = theme;
const { token } = useToken();

let windowWidth = ref(1200),
  windowHeight = ref(800);

// 优先读取本地存储
let defaultDark = false;
let defaultColorStr = "#1677ff";
let defaultWindowWidth = windowWidth.value;
let defaultWindowHeight = windowHeight.value;

console.log("缓存的主题:", localStorage.getItem(STORAGE_KEY));
const saved = localStorage.getItem(STORAGE_KEY);
if (saved) {
  const { dark, color, showX, showY, windowWidth, windowHeight } = JSON.parse(saved);
  if (typeof dark === "boolean") defaultDark = dark;
  if (color) defaultColorStr = color;
  if (windowWidth) defaultWindowWidth = windowWidth;
  if (windowHeight) defaultWindowHeight = windowHeight;
}

const isDark = ref(defaultDark);
let primaryColor = ref(defaultColorStr);

// 主题和本地存储更新，严格保证只传string
let appTheme = ref({});
watch(
  [isDark, primaryColor, windowHeight, windowWidth],
  ([dark, color, windowHeight, windowWidth]) => {
    let safeColor = typeof color === "string" ? color : defaultColorStr;
    appTheme.value = {
      token: { colorPrimary: safeColor },
      algorithm: dark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    };
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        dark,
        color: safeColor,
        windowHeight,
        windowWidth,
      })
    );
  },
  { immediate: true }
);

// ==================== 窗口状态 ====================
const isMaximized = ref(false);
const isAlwaysOnTop = ref(false);

// 置顶功能
const toggleAlwaysOnTop = () => {
  isAlwaysOnTop.value = !isAlwaysOnTop.value;
  window.pywebview.api.set_on_top(isAlwaysOnTop.value);
};

// 最小化
const minimize = () => window.pywebview.api.minimize();
// 最大化/还原
let toggle = () => {
  if (isMaximized.value) {
    window.pywebview.api.restore();
  } else {
    window.pywebview.api.maximize();
  }
  isMaximized.value = !isMaximized.value;
};
// 关闭
const close = () => window.pywebview.api.close();

// 组件挂载后需要执行
onMounted(async () => {
  // 官方最推荐方式：监听 pywebviewready 事件，等待 pywebview.api 就绪
  await new Promise<void>((resolve) => {
    const tryInit = () => {
      if (window.pywebview?.api?.resize_window) {
        window.pywebview.api.resize_window(defaultWindowWidth, defaultWindowHeight);
        window.pywebview.api.center_window();
        resolve();
      }
    };

    // 大部分情况页面加载时已经 ready，直接执行
    if (tryInit()) return;

    // 没 ready 就等官方事件（一定能等到，且只触发一次）
    window.addEventListener("pywebviewready", tryInit, { once: true });
  });

  // ==================== 窗口拖拽 ====================
  const dragBar = document.getElementsByClassName("drag-region");
  let isDragging = false;
  let lastMoveTime = 0;
  let accumulatedDeltaX = 0;
  let accumulatedDeltaY = 0;

  const moveThreshold = 10; // 每10ms才处理一次移动事件
  let offsetX, offsetY;

  for (let i = 0; i < dragBar.length; i++) {
    dragBar[i].addEventListener("mousedown", (e) => {
      isDragging = true;
      offsetX = e.clientX;
      offsetY = e.clientY;
    });
    dragBar[i].addEventListener("dblclick", (e) => {
      toggle();
    });
  }

  document.addEventListener("mousemove", (e) => {
    if (isDragging) {
      const currentTime = Date.now();
      // 如果距离上次移动的时间超过阈值才更新位置
      if (currentTime - lastMoveTime > moveThreshold) {
        const deltaX = e.clientX - offsetX;
        const deltaY = e.clientY - offsetY;

        // 累积增量
        accumulatedDeltaX += deltaX;
        accumulatedDeltaY += deltaY;

        // 调用 Python 来移动窗口，使用累积的偏移量
        window.pywebview.api.drag_move(accumulatedDeltaX, accumulatedDeltaY);

        offsetX = e.clientX;
        offsetY = e.clientY;
        lastMoveTime = currentTime;
      }
    }
  });

  document.addEventListener("mouseup", () => {
    isDragging = false;
    // 重置累积的偏移量
    accumulatedDeltaX = 0;
    accumulatedDeltaY = 0;
  });

  // 完整代码：放到你的 Vue 组件的 mounted() 中
  let isResizing = false;
  let startX, startY, startWidth, startHeight;

  const corner = document.querySelector(".corner"); // 右下角拖拽图标元素
  corner.style.cursor = "se-resize"; // 固定东南方向拉伸光标

  // 鼠标按下：开始拖拽调整大小
  corner.addEventListener("mousedown", (e) => {
    // 关键：获取整个窗口（根元素）的尺寸，而不是 corner 本身
    const root = document.documentElement; // 或 document.getElementById('app') / document.body
    const rect = root.getBoundingClientRect();

    isResizing = true;
    startX = e.clientX;
    startY = e.clientY;
    startWidth = rect.width; // 当前窗口实际宽度
    startHeight = rect.height; // 当前窗口实际高度
    e.preventDefault(); // 防止选中文字等默认行为
  });

  // 鼠标移动：实时计算并调整窗口大小
  document.addEventListener("mousemove", (e) => {
    if (!isResizing) return;

    let newWidth = startWidth + (e.clientX - startX);
    let newHeight = startHeight + (e.clientY - startY);

    // 最小尺寸限制（可根据需要调整）
    windowWidth.value = Math.max(800, newWidth); // 最小宽度
    windowHeight.value = Math.max(600, newHeight); // 最小高度

    // 调用 Python API 调整窗口大小
    window.pywebview.api.resize_window(windowWidth.value, windowHeight.value);
  });

  // 鼠标松开：结束拖拽
  document.addEventListener("mouseup", () => {
    isResizing = false;
  });

  // ==================== 颜色选择器 ====================
  let pickr: Pickr | null = null;
  if (!pickr) {
    pickr = Pickr.create({
      el: "#color-picker",
      theme: "nano",
      default: primaryColor.value,
      swatches: [
        "#E60000", // 经典法拉利红    Hue ≈ 0°
        "#F55A0A", // 爱马仕橙        Hue ≈ 20°
        "#E85827", // 爱马仕橙深      Hue ≈ 25°
        "#FA7268", // Living Coral    Hue ≈ 35°
        "#D99A6C", // 星巴克拿铁棕    Hue ≈ 38°
        "#B05923", // 焦糖棕          Hue ≈ 45°
        "#FF5E98", // 香奈儿樱花粉    Hue ≈ 340°
        "#E0218A", // 芭比粉          Hue ≈ 330°
        "#C6B4FE", // 数字薰衣草      Hue ≈ 255°
        "#6667AB", // Very Peri       Hue ≈ 240°
        "#01847F", // 蒂芙尼深青      Hue ≈ 178°
        "#81D8CF", // 蒂芙尼蓝        Hue ≈ 175°
        "#40E0D0", // 经典绿松石      Hue ≈ 174°
        "#88B04B", // Greenery        Hue ≈ 90°
      ],
      components: {
        preview: true,
        opacity: false,
        hue: true,
        interaction: {
          hex: false,
          input: true,
          save: false,
          cancel: false,
          clear: false,
        },
      },
    });

    pickr.on("change", (c: Pickr.HSVaColor) => {
      const hex = c.toHEXA().toString();
      primaryColor.value = hex;
      // 同步触发 save 事件
      pickr?.applyColor();
    });
  }
});

// ==================== 左侧菜单 ====================
const selectedKeys = ref(["run"]);
const collapsed = ref(false);
const openKeys = ref<string[]>(["mail"]);

let nav_items = ref<MenuProps["items"]>([
  {
    key: "mail",
    icon: () => h(icon.RobotFilled),
    label: "脚本管理",
    children: [
      {
        key: "run",
        icon: () => h(icon.ThunderboltFilled),
        label: "运行脚本",
      },
      {
        key: "group",
        icon: () => h(icon.UnorderedListOutlined),
        label: "脚本列表",
      },
    ],
  },
]);

// 内容区切换
const activeKey = computed(() => selectedKeys.value?.[0] || "run");
const viewMap: Record<string, any> = {
  run: CliRun,
  group: LibraryManager,
};
const ActiveComp = computed(() => viewMap[activeKey.value] || CliRun);

// 菜单父级自动展开
function getParentKeys(
  targetKey: string,
  items: NonNullable<MenuProps["items"]>
): string[] {
  if (!items) return [];
  for (const item of items as any[]) {
    if (!item) continue;
    const children = item.children as any[] | undefined;
    if (children && children.some((c) => c && c.key === targetKey)) {
      return [item.key as string];
    }
    if (children && children.length) {
      const sub = getParentKeys(targetKey, children as any);
      if (sub.length) return [item.key as string, ...sub];
    }
  }
  return [];
}

watch(
  selectedKeys,
  (keys) => {
    const k = keys?.[0];
    if (!k) return;
    openKeys.value = getParentKeys(k, nav_items.value!);
  },
  { immediate: true }
);
</script>

<template>
  <a-configProvider :theme="appTheme">
    <a-layout class="app-content">
      <!-- 左侧菜单 -->
      <a-layout-sider
        class="drag-region"
        v-model:collapsed="collapsed"
        :trigger="null"
        collapsible
      >
        <a-typography-paragraph class="logo-content">
          <div v-if="logo" class="logo" v-html="logoSvg"></div>
          <span>{{ title }}</span>
        </a-typography-paragraph>
        <a-menu
          v-model:selectedKeys="selectedKeys"
          v-model:openKeys="openKeys"
          :inline-collapsed="collapsed"
          mode="inline"
          :items="nav_items"
        >
        </a-menu>
      </a-layout-sider>
      <a-layout class="app-main">
        <!-- 顶部标题栏 -->
        <a-layout-header class="drag-region">
          <a-flex justify="space-between" align="center">
            <a-typography-paragraph class="titlebar-icon">
              <svg
                v-if="!collapsed"
                @click="() => (collapsed = !collapsed)"
                xmlns="http://www.w3.org/2000/svg"
                width="1em"
                height="1em"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-panel-right-open-icon lucide-panel-right-open"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <path d="M15 3v18" />
                <path d="m10 15-3-3 3-3" />
              </svg>
              <svg
                v-if="collapsed"
                @click="() => (collapsed = !collapsed)"
                xmlns="http://www.w3.org/2000/svg"
                width="1em"
                height="1em"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="lucide lucide-panel-right-close-icon lucide-panel-right-close"
              >
                <rect width="18" height="18" x="3" y="3" rx="2" />
                <path d="M15 3v18" />
                <path d="m8 9 3 3-3 3" />
              </svg>
            </a-typography-paragraph>

            <!-- 右侧控制区 -->
            <a-flex horizontal gap="small" class="titlebar-controls" align="center">
              <!-- 主题切换 + 颜色选择器 -->
              <a-tooltip>
                <template #title>切换主题</template>
                <a-switch
                  checked-children="暗"
                  un-checked-children="亮"
                  v-model:checked="isDark"
                />
              </a-tooltip>

              <a-tooltip>
                <template #title>主题颜色</template>
                <div id="color-picker"></div>
              </a-tooltip>

              <!-- 置顶按钮（高亮表示已置顶） -->
              <a-tooltip>
                <template #title>窗口置顶</template>
                <a-button
                  type="text"
                  :class="{ active: isAlwaysOnTop }"
                  @click="toggleAlwaysOnTop"
                >
                  <svg
                    v-if="!isAlwaysOnTop"
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path
                      d="M20.9711 17.1715 19.5568 18.5858 16.0223 15.0513 15.9486 15.125 15.2415 18.6605 13.8273 20.0747 9.58466 15.8321 4.63492 20.7818 3.2207 19.3676 8.17045 14.4179 3.92781 10.1752 5.34202 8.76101 8.87756 8.0539 8.95127 7.98019 5.4147 4.44362 6.82892 3.02941 20.9711 17.1715ZM18.8508 12.2228 20.1913 10.8823 20.8984 11.5894 22.3126 10.1752 13.8273 1.68994 12.4131 3.10416 13.1202 3.81126 11.7797 5.15176 18.8508 12.2228Z"
                    ></path>
                  </svg>

                  <svg
                    v-if="isAlwaysOnTop"
                    width="1em"
                    height="1em"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path
                      d="M22.3126 10.1753L20.8984 11.5895L20.1913 10.8824L15.9486 15.125L15.2415 18.6606L13.8273 20.0748L9.58466 15.8321L4.63492 20.7819L3.2207 19.3677L8.17045 14.4179L3.92781 10.1753L5.34202 8.76107L8.87756 8.05396L13.1202 3.81132L12.4131 3.10422L13.8273 1.69L22.3126 10.1753Z"
                    ></path>
                  </svg>
                </a-button>
              </a-tooltip>
              <!-- 窗口控制按钮 -->
              <a-tooltip>
                <template #title>最小化</template>
                <a-button type="text" @click="minimize">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="lucide lucide-minus-icon lucide-minus"
                  >
                    <path d="M5 12h14" />
                  </svg>
                </a-button>
              </a-tooltip>
              <a-tooltip>
                <template #title>{{ isMaximized ? "还原" : "最大化" }}</template>
                <a-button type="text" @click="toggle()">
                  <svg
                    v-if="isMaximized"
                    width="1em"
                    height="1em"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="lucide lucide-copy-icon lucide-copy"
                    style="transform: scaleX(-1)"
                  >
                    <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
                  </svg>
                  <svg
                    v-if="!isMaximized"
                    width="1em"
                    height="1em"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="lucide lucide-square-icon lucide-square"
                  >
                    <rect width="18" height="18" x="3" y="3" rx="2" />
                  </svg>
                </a-button>
              </a-tooltip>
              <a-tooltip>
                <template #title>关闭</template>
                <a-button type="text" danger @click="close">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="1em"
                    height="1em"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="lucide lucide-plus-icon lucide-plus"
                    style="transform: rotate(45deg); font-size: 1.5em"
                  >
                    <path d="M5 12h14" />
                    <path d="M12 5v14" />
                  </svg>
                </a-button>
              </a-tooltip>
            </a-flex>
          </a-flex>
        </a-layout-header>
        <!-- 主内容区域 -->
        <a-layout-content>
          <KeepAlive>
            <component :is="ActiveComp" />
          </KeepAlive>
        </a-layout-content>
      </a-layout>

      <div class="corner">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="1em"
          height="1em"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="lucide lucide-grip-icon lucide-grip"
        >
          <circle cx="19" cy="5" r="1" />
          <circle cx="12" cy="12" r="1" />
          <circle cx="19" cy="12" r="1" />
          <circle cx="12" cy="19" r="1" />
          <circle cx="19" cy="19" r="1" />
          <circle cx="5" cy="19" r="1" />
        </svg>
      </div>
    </a-layout>
  </a-configProvider>
</template>

<style scoped>
:deep(.pickr) {
  button {
    border-radius: 100% !important;
    overflow: hidden !important;
  }
}

:global(.pcr-app) {
  border-radius: 0.2rem;
  overflow: hidden;
  background: transparent;
  box-shadow: 0 0 12px color-mix(in srgb, #fff 50%, #000);
}

:global(.pcr-color-chooser) {
  margin-top: 14px !important;
}

body {
  background-color: transparent;
}

.ant-btn {
  display: flex;
  align-items: center;
}

.app-content {
  --primary-color: v-bind(token.colorPrimary);
  --primary-15-color: color-mix(in srgb, var(--primary-color) 15%, transparent);
  --background-color: v-bind(token.colorBgContainer);
  --text-color: v-bind(token.colorText);

  --background-1-color: color-mix(
    in srgb,
    var(--background-color) 90%,
    color-mix(in srgb, var(--primary-color) 60%, transparent)
  );
  --background-2-color: color-mix(
    in srgb,
    var(--background-color) 90%,
    color-mix(in srgb, var(--primary-color) 40%, var(--text-color))
  );

  height: 100vh;
  overflow: hidden;

  .corner {
    position: fixed !important;
    z-index: 999;
    bottom: 0;
    right: 0;
    color: var(--text-color);
    svg {
      position: fixed;
      cursor: nwse-resize;
      bottom: 3px;
      right: 3px;
      font-size: 1rem;
      overflow: hidden;
    }
  }

  header {
    -webkit-app-region: drag;
    background: transparent;
    padding: 0 1rem;
    .ant-flex {
      height: 100%;
    }

    .titlebar-icon {
      -webkit-app-region: no-drag;
      font-size: 1.2rem;
      cursor: pointer;
      margin: 0;
    }

    /* 置顶高亮 */
    .titlebar-controls .ant-btn.active {
      color: var(--primary-color);
      background: color-mix(in srgb, var(--primary-color) 20%, var(--background-color));
    }
  }
  aside {
    -webkit-app-region: drag;
    background: color-mix(
      in srgb,
      color-mix(in srgb, var(--primary-color) 50%, var(--background-color)) 50%,
      transparent
    );
    &.ant-layout-sider-collapsed {
      .logo-content {
        justify-content: center;

        span {
          display: none;
          overflow: hidden;
        }
      }
    }
    .ant-menu {
      background: transparent;
      border: none;
    }
    .logo-content {
      height: 32px;
      margin: 16px;
      gap: 1rem;
      display: flex;
      align-items: center;
      font-size: 1.5rem;
      .logo {
        text-align: center;
        height: 100%;
        width: 32px;
      }
      span {
        transition: 0.3s;
        height: 100%;
        overflow: hidden;
      }
    }
  }
  main {
    padding: 1rem;
    border-radius: 0.5rem;
    background: var(--background-color);
  }
  .app-main {
    background: color-mix(
      in srgb,
      color-mix(in srgb, var(--primary-color) 50%, var(--background-color)) 50%,
      transparent
    );
  }
}
</style>
