#!/bin/bash

# 检查是否提供了两个参数
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <target_directory>"
    exit 1
fi

# 获取源目录和目标目录
source_dir="$1"
target_dir="$2"

# 检查源目录是否存在
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory '$source_dir' does not exist"
    exit 1
fi

# 检查目标目录是否存在，不存在则创建
if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
fi

# 遍历源目录下的第一层目录
find "$source_dir" -maxdepth 1 -type d | while read -r dir; do
    # 跳过源目录本身
    if [ "$dir" = "$source_dir" ]; then
        continue
    fi

    # 删除非mp4和非kmp文件（包括子目录）
    find "$dir" -type f ! -name "*.mp4" ! -name "*.kmp" -delete
    # 删除小于100M的mp4文件
    find "$dir" -type f -name "*.mp4" -size -100M -delete
    # 删除所有子目录
    find "$dir" -type d -maxdepth 1 ! -path "$dir" -exec rm -rf {} +

    # 移动处理后的目录到目标目录
    mv "$dir" "$target_dir/"
    echo "Processed and moved: $dir to $target_dir/"
done

echo "Operation completed successfully"