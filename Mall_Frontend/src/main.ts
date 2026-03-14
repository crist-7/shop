import { createApp } from 'vue';
import './styles/variables.css';
import './style.css';
import App from './App.vue';

// 引入刚刚配置好的 Router
import router from './router';

// 引入 Pinia 状态管理
import { createPinia } from 'pinia';

// 引入 Element Plus 及全局样式
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

// 引入图片懒加载指令
import { setupLazyLoad } from './directives/lazyload';

const app = createApp(App);
const pinia = createPinia();

// 挂载各种插件
app.use(router);
app.use(pinia);
app.use(ElementPlus);

// 注册全局懒加载指令
setupLazyLoad(app);

app.mount('#app');