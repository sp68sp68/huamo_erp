# 华膜进销存系统 - Android APK 构建指南

## 准备工作已完成

以下文件已经配置好，无需修改：
- ✅ main.py - 已添加 Android 平台兼容
- ✅ database.py - 已适配 Android 数据库路径
- ✅ buildozer.spec - 已配置 Android 构建参数
- ✅ assets/msyh.ttf - 已打包中文字体
- ✅ .github/workflows/build-android.yml - 云端构建配置
- ✅ build_android.sh - 本地构建脚本

---

## 方案 A：GitHub 云端构建（推荐，最简单）

### 第一步：注册 GitHub 账号（2分钟）
1. 打开浏览器，访问 https://github.com/signup
2. 输入邮箱、设置密码、选用户名
3. 去邮箱点击验证链接
4. 注册完成

### 第二步：创建仓库并上传代码
打开 PowerShell，依次执行：

```powershell
# 安装 GitHub CLI（如果还没安装）
winget install GitHub.cli

# 登录 GitHub（会打开浏览器）
gh auth login

# 进入项目目录
cd D:\huamo_erp

# 初始化 Git 仓库
git init
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库并推送（会自动触发构建）
gh repo create huamo_erp --public --source=. --push
```

### 第三步：等待构建完成（30-60分钟）
1. 打开 https://github.com/你的用户名/huamo_erp
2. 点击 "Actions" 标签
3. 等待 "Build Android APK" 运行完成（绿色勾）
4. 点击该次运行记录
5. 在页面底部 "Artifacts" 区域下载 `huamo-erp-apk.zip`
6. 解压得到 `.apk` 文件

### 第四步：安装到手机
1. 将 `.apk` 文件传到手机（微信/QQ/数据线）
2. 在手机上点击安装（需要允许"安装未知来源应用"）
3. 完成！

---

## 方案 B：WSL2 本地构建（需要开启虚拟化）

### 第一步：开启 BIOS 虚拟化
1. 重启电脑，开机时按 F2/Del/F10 进入 BIOS
2. 找到以下选项之一并设为 Enabled：
   - Intel VT-x / Intel Virtualization Technology
   - AMD-V / SVM Mode
3. 保存并退出 BIOS

### 第二步：安装 WSL2 和 Ubuntu
以管理员身份打开 PowerShell：

```powershell
# 安装 WSL 和 Ubuntu
wsl --install -d Ubuntu

# 重启电脑
# 重启后打开 Ubuntu，设置用户名和密码
```

### 第三步：在 WSL2 中构建 APK
打开 Ubuntu 终端：

```bash
# 进入项目目录
cd /mnt/d/huamo_erp

# 运行构建脚本
bash build_android.sh

# 等待 30-60 分钟
# 构建完成后，APK 在 bin/ 目录
ls bin/*.apk
```

### 第四步：安装到手机
同方案 A 的第四步

---

## 常见问题

### Q: 构建失败怎么办？
A: 检查 GitHub Actions 的日志，常见原因：
- 依赖版本不兼容
- 内存不足（GitHub 免费账户有限制）
- 网络问题（重试即可）

### Q: APK 安装失败？
A: 手机需要允许"安装未知来源应用"：
- 设置 → 安全 → 允许安装未知应用

### Q: 首次启动很慢？
A: 正常，首次启动需要初始化数据库，后续启动会快很多

### Q: 如何更新应用？
A: 修改代码后，推送到 GitHub 会自动重新构建：
```powershell
git add .
git commit -m "更新说明"
git push
```

---

## 技术支持

如果遇到问题，可以：
1. 查看 GitHub Actions 日志
2. 检查 buildozer.spec 配置
3. 搜索相关错误信息

祝你使用愉快！
