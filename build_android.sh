#!/bin/bash
# ============================================================
# 华膜进销存系统 - Android APK 构建脚本
# 在 Linux 或 WSL2 环境中运行此脚本
# ============================================================

set -e

echo "=========================================="
echo "  华膜进销存系统 - Android APK 构建"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo -e "${GREEN}项目目录: $PROJECT_DIR${NC}"

# ── 1. 安装系统依赖 ──
echo ""
echo -e "${YELLOW}[1/6] 安装系统依赖...${NC}"
sudo apt update
sudo apt install -y \
    python3 python3-pip python3-venv \
    build-essential git zip unzip \
    openjdk-17-jdk \
    libffi-dev \
    ccache \
    wget \
    2>/dev/null || {
    echo -e "${RED}apt 安装失败，尝试不使用 sudo...${NC}"
    apt update
    apt install -y \
        python3 python3-pip python3-venv \
        build-essential git zip unzip \
        openjdk-17-jdk \
        libffi-dev \
        ccache \
        wget
}

# ── 2. 设置 Java ──
echo ""
echo -e "${YELLOW}[2/6] 配置 Java 环境...${NC}"
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH="$JAVA_HOME/bin:$PATH"
echo "JAVA_HOME=$JAVA_HOME"
java -version

# ── 3. 安装 Buildozer ──
echo ""
echo -e "${YELLOW}[3/6] 安装 Buildozer...${NC}"
pip3 install --user --upgrade buildozer cython==0.29.33
export PATH="$HOME/.local/bin:$PATH"
buildozer --version

# ── 4. 清理旧的构建缓存 ──
echo ""
echo -e "${YELLOW}[4/6] 清理旧构建缓存...${NC}"
rm -rf .buildozer/android/platform/build-*/dist/ 2>/dev/null || true

# ── 5. 构建 APK ──
echo ""
echo -e "${YELLOW}[5/6] 开始构建 APK（首次构建需要 30-60 分钟）...${NC}"
buildozer android debug

# ── 6. 输出结果 ──
echo ""
echo -e "${YELLOW}[6/6] 构建完成！${NC}"
APK_FILE=$(find bin -name "*.apk" -type f | head -1)
if [ -n "$APK_FILE" ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "  APK 构建成功！"
    echo "  文件: $APK_FILE"
    echo "  大小: $(du -h "$APK_FILE" | cut -f1)"
    echo -e "==========================================${NC}"
    echo ""
    echo "将 APK 文件传输到手机即可安装"
else
    echo -e "${RED}未找到 APK 文件，构建可能失败${NC}"
    echo "请检查上方的错误信息"
    exit 1
fi
