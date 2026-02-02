#!/bin/bash

# 完全覆盖同步技能文件到 Claude skills 目录
SKILLS_DIR="$HOME/.claude/skills"

echo "正在完全覆盖同步到 $SKILLS_DIR/ ..."

# 确保目标目录存在
mkdir -p "$SKILLS_DIR"

# 清空目标目录（完全覆盖）
echo "清空现有技能目录..."
rm -rf "$SKILLS_DIR"/*

# 复制新的技能文件
echo "复制新的技能文件..."
cp -r skills/* "$SKILLS_DIR"/

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 同步成功！"
    echo ""
    echo "当前技能列表："
    ls -1 "$SKILLS_DIR" | grep -v "^\."
else
    echo ""
    echo "✗ 同步失败"
    exit 1
fi
