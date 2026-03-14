<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon :color="'var(--primary-color)'" size="24"><Shop /></el-icon>
        <span v-show="!isCollapse" class="logo-text">星辰商城后台</span>
      </div>

      <el-menu
        active-text-color="var(--primary-color)"
        background-color="var(--bg-sidebar)"
        text-color="var(--text-primary)"
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        class="el-menu-vertical"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>

        <!-- 商品管理菜单 (里面包含3个子菜单) -->
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>商品管理</span>
          </template>
          <el-menu-item index="/goods">商品列表</el-menu-item>
          <el-menu-item index="/category">分类管理</el-menu-item>
          <el-menu-item index="/banner">轮播图管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="2">
          <template #title>
            <el-icon><List /></el-icon>
            <span>订单管理</span>
          </template>
          <el-menu-item index="/orders">订单列表</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ $route.meta.title || '控制台' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <!-- 使用本地 Icon 替代外部 CDN 头像 避免网络延迟 -->
              <el-avatar :size="30" class="avatar-icon">
                <el-icon :size="18"><User /></el-icon>
              </el-avatar>
              <span style="margin-left: 8px">Admin</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>

  <!-- ============================================================ -->
  <!-- 个人中心弹窗 -->
  <!-- ============================================================ -->
  <el-dialog
    v-model="profileDialogVisible"
    title="个人中心"
    width="500px"
    :close-on-click-modal="false"
  >
    <!-- 用户信息展示区 -->
    <div class="profile-info-section">
      <div class="profile-avatar">
        <el-avatar :size="80" class="avatar-large">
          <el-icon :size="40"><User /></el-icon>
        </el-avatar>
        <div class="profile-name">Admin</div>
      </div>
      <el-descriptions :column="1" border class="profile-descriptions">
        <el-descriptions-item label="用户名">Admin</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag type="danger" size="small">超级管理员</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">admin@startmall.com</el-descriptions-item>
        <el-descriptions-item label="注册时间">2024-01-01 10:00:00</el-descriptions-item>
        <el-descriptions-item label="最后登录">2026-03-15 09:30:00</el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 修改密码表单 -->
    <el-divider content-position="left">修改密码</el-divider>
    <el-form
      ref="passwordFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      label-width="100px"
      class="password-form"
    >
      <el-form-item label="原密码" prop="oldPassword">
        <el-input
          v-model="passwordForm.oldPassword"
          type="password"
          placeholder="请输入原密码"
          show-password
        />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input
          v-model="passwordForm.newPassword"
          type="password"
          placeholder="请输入新密码（至少6位）"
          show-password
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="passwordForm.confirmPassword"
          type="password"
          placeholder="请再次输入新密码"
          show-password
        />
      </el-form-item>
    </el-form>

    <!-- 底部按钮 -->
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handlePasswordSubmit">
          保存修改
        </el-button>
      </span>
    </template>
  </el-dialog>

  <!-- ============================================================ -->
  <!-- 系统设置抽屉 -->
  <!-- ============================================================ -->
  <el-drawer
    v-model="settingsDrawerVisible"
    title="系统设置"
    direction="rtl"
    size="350px"
  >
    <div class="settings-content">
      <!-- 暗黑模式开关 -->
      <div class="settings-item">
        <div class="settings-item-info">
          <el-icon :size="20"><Moon /></el-icon>
          <span class="settings-item-title">暗黑模式</span>
        </div>
        <el-switch
          v-model="settings.darkMode"
          active-text="开"
          inactive-text="关"
          @change="handleDarkModeChange"
        />
      </div>
      <p class="settings-item-desc">开启后界面将切换为暗色主题，保护眼睛</p>

      <!-- 紧凑模式开关 -->
      <div class="settings-item">
        <div class="settings-item-info">
          <el-icon :size="20"><Grid /></el-icon>
          <span class="settings-item-title">紧凑模式</span>
        </div>
        <el-switch
          v-model="settings.compactMode"
          active-text="开"
          inactive-text="关"
          @change="handleCompactModeChange"
        />
      </div>
      <p class="settings-item-desc">减少界面间距，显示更多内容</p>

      <!-- 分隔线 -->
      <el-divider />

      <!-- 其他设置预留 -->
      <div class="settings-item">
        <div class="settings-item-info">
          <el-icon :size="20"><Bell /></el-icon>
          <span class="settings-item-title">消息通知</span>
        </div>
        <el-switch
          v-model="settings.notification"
          active-text="开"
          inactive-text="关"
        />
      </div>
      <p class="settings-item-desc">接收系统消息和订单提醒</p>

      <div class="settings-item">
        <div class="settings-item-info">
          <el-icon :size="20"><RefreshRight /></el-icon>
          <span class="settings-item-title">自动刷新</span>
        </div>
        <el-switch
          v-model="settings.autoRefresh"
          active-text="开"
          inactive-text="关"
        />
      </div>
      <p class="settings-item-desc">订单列表每30秒自动刷新一次</p>
    </div>

    <!-- 抽屉底部按钮 -->
    <template #footer>
      <el-button @click="resetSettings">恢复默认</el-button>
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage, type FormInstance, type FormRules } from 'element-plus';
import {
  User,
  Setting,
  SwitchButton,
  Moon,
  Grid,
  Bell,
  RefreshRight
} from '@element-plus/icons-vue';

// ============================================================
// 侧边栏折叠状态
// ============================================================
const isCollapse = ref(false);
const router = useRouter();

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

// ============================================================
// 个人中心弹窗相关
// ============================================================
const profileDialogVisible = ref(false);
const passwordLoading = ref(false);
const passwordFormRef = ref<FormInstance>();

// 修改密码表单数据
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// 密码验证规则
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
};

// 提交修改密码
const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value) return;

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true;
      try {
        // 模拟异步请求
        await new Promise((resolve) => setTimeout(resolve, 1000));
        ElMessage.success('密码修改成功');
        profileDialogVisible.value = false;
        // 清空表单
        passwordForm.oldPassword = '';
        passwordForm.newPassword = '';
        passwordForm.confirmPassword = '';
      } catch (error) {
        ElMessage.error('密码修改失败');
      } finally {
        passwordLoading.value = false;
      }
    }
  });
};

// ============================================================
// 系统设置抽屉相关
// ============================================================
const settingsDrawerVisible = ref(false);

// 系统设置数据（响应式）
const settings = reactive({
  darkMode: false,
  compactMode: false,
  notification: true,
  autoRefresh: false,
});

// 暗黑模式切换处理
const handleDarkModeChange = (value: boolean) => {
  // 通过修改 HTML 标签的 class 来切换主题
  if (value) {
    document.documentElement.classList.add('dark');
    ElMessage.info('暗黑模式已开启');
  } else {
    document.documentElement.classList.remove('dark');
    ElMessage.info('暗黑模式已关闭');
  }
};

// 紧凑模式切换处理
const handleCompactModeChange = (value: boolean) => {
  if (value) {
    document.documentElement.classList.add('compact');
    ElMessage.info('紧凑模式已开启');
  } else {
    document.documentElement.classList.remove('compact');
    ElMessage.info('紧凑模式已关闭');
  }
};

// 恢复默认设置
const resetSettings = () => {
  settings.darkMode = false;
  settings.compactMode = false;
  settings.notification = true;
  settings.autoRefresh = false;
  // 同时移除相关 CSS 类
  document.documentElement.classList.remove('dark', 'compact');
  ElMessage.success('已恢复默认设置');
};

// 保存设置（可扩展为持久化到 localStorage 或后端）
const saveSettings = () => {
  // 持久化到 localStorage
  localStorage.setItem('admin_settings', JSON.stringify(settings));
  ElMessage.success('设置已保存');
};

// ============================================================
// 下拉菜单命令处理
// ============================================================
const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      profileDialogVisible.value = true;
      break;
    case 'settings':
      settingsDrawerVisible.value = true;
      break;
    case 'logout':
      handleLogout();
      break;
  }
};

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    localStorage.removeItem('token');
    ElMessage.success('已退出登录');
    router.push('/login');
  });
};
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: var(--bg-sidebar);
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  border-right: 1px solid var(--bg-tertiary);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  font-weight: bold;
  background-color: var(--bg-sidebar);
  white-space: nowrap;
  padding: 0 var(--space-lg);
  border-bottom: 1px solid var(--bg-tertiary);
}

.logo-text {
  margin-left: var(--space-sm);
  font-size: 16px;
}

.el-menu-vertical {
  border-right: none;
  background-color: transparent;
}

:deep(.el-menu) {
  background-color: transparent !important;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: var(--text-primary) !important;
  border-radius: var(--radius-md);
  margin: var(--space-xs) var(--space-sm);
  transition: all var(--transition-fast);
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: var(--bg-sidebar-hover) !important;
}

:deep(.el-menu-item.is-active) {
  background-color: var(--bg-sidebar-active) !important;
  color: var(--primary-color) !important;
  font-weight: 600;
  border-radius: var(--radius-md);
  margin: var(--space-xs) var(--space-sm);
}

.header {
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.collapse-btn:hover {
  color: var(--primary-color);
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: var(--text-primary);
  transition: color var(--transition-fast);
}

.user-info:hover {
  color: var(--primary-color);
}

.avatar-icon {
  background: linear-gradient(135deg, var(--primary-color), #6a8eff);
  color: white;
}

.main {
  background-color: var(--bg-secondary);
  padding: var(--space-2xl);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================================================ */
/* 个人中心弹窗样式 */
/* ============================================================ */
.profile-info-section {
  text-align: center;
}

.profile-avatar {
  margin-bottom: var(--space-xl);
}

.avatar-large {
  background: linear-gradient(135deg, var(--primary-color), #6a8eff);
  color: white;
}

.profile-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-top: var(--space-md);
}

.profile-descriptions {
  text-align: left;
  margin-top: var(--space-lg);
}

.password-form {
  margin-top: var(--space-lg);
}

/* ============================================================ */
/* 系统设置抽屉样式 */
/* ============================================================ */
.settings-content {
  padding: 0 var(--space-md);
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) 0;
}

.settings-item-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.settings-item-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.settings-item-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0 0 var(--space-md) calc(20px + var(--space-md));
}

/* ============================================================ */
/* 响应式调整 */
/* ============================================================ */
@media (max-width: 768px) {
  .aside {
    width: 64px !important;
  }

  .logo-text {
    display: none;
  }

  .header {
    padding: 0 var(--space-lg);
  }
}
</style>
