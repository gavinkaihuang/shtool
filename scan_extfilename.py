import os
import sys

# 获取命令行参数中的目录路径，如果没有提供则使用当前目录
if len(sys.argv) > 1:
    target_dir = sys.argv[1]
else:
    target_dir = '.'  # 默认扫描当前目录

# 用于存储唯一的后缀名
extensions = set()

# 递归遍历目录及其子目录
for root, dirs, files in os.walk(target_dir):
    for file in files:
        # 获取文件扩展名（包括点，如 .txt）
        ext = os.path.splitext(file)[1].lower()
        if ext:  # 忽略无扩展名的文件
            extensions.add(ext)

# 按字母顺序排序后写入 result.txt
with open('result.txt', 'w', encoding='utf-8') as f:
    for ext in sorted(extensions):
        f.write(ext + '\n')

print(f"扫描完成，共找到 {len(extensions)} 种唯一后缀名，结果已写入 result.txt")
