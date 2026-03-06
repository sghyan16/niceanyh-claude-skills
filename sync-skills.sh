#!/bin/bash

# 脚本用于同步skills文件夹到~/.claude/skills
# 保持与当前项目中的skills文件夹一致

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.claude/skills"

echo -e "${BLUE}开始同步skills文件夹...${NC}"
echo -e "源目录: ${GREEN}$SOURCE_DIR${NC}"
echo -e "目标目录: ${GREEN}$TARGET_DIR${NC}"
echo ""

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}错误: 源目录不存在: $SOURCE_DIR${NC}"
    exit 1
fi

# 创建目标目录（如果不存在）
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${BLUE}创建目标目录: $TARGET_DIR${NC}"
    mkdir -p "$TARGET_DIR"
fi

# 使用rsync同步文件
# -a: 归档模式，保留权限、时间戳等
# -v: 详细模式，显示正在同步的文件
# --delete: 删除目标目录中源目录没有的文件
# --exclude: 排除不需要同步的文件
echo -e "${BLUE}正在同步文件...${NC}"
rsync -av --delete \
    --exclude='.DS_Store' \
    --exclude='*.swp' \
    --exclude='*~' \
    --exclude='.git' \
    "$SOURCE_DIR/" "$TARGET_DIR/"

# 检查rsync是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 同步完成！${NC}"
    echo -e "${BLUE}Skills已更新到: $TARGET_DIR${NC}"
else
    echo ""
    echo -e "${RED}✗ 同步失败${NC}"
    exit 1
fi
