import os
import sys
import argparse

def delete_images_only(target_dir, keywords):
    # 1. 检查路径
    if not os.path.exists(target_dir):
        print(f"❌ 错误: 路径 '{target_dir}' 不存在！")
        return

    # 2. 定义图片后缀名白名单 (不区分大小写)
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic'}
    
    lower_keywords = [k.lower() for k in keywords]
    matched_files = []

    print(f"🔍 正在扫描图片文件: {os.path.abspath(target_dir)}")
    
    # 3. 扫描阶段
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            # 获取文件后缀
            ext = os.path.splitext(file)[1].lower()
            
            # 同时满足：1. 是图片格式 2. 包含关键词
            if ext in IMAGE_EXTENSIONS:
                if any(key in file.lower() for key in lower_keywords):
                    matched_files.append(os.path.join(root, file))

    if not matched_files:
        print("✅ 未发现符合条件的匹配图片。")
        return

    # 4. 打印待删除列表供确认
    print("\n" + "="*60)
    print(f"🖼️  待删除【图片】列表 (总计: {len(matched_files)} 个):")
    for path in matched_files:
        print(f"  [图片] {path}")
    print("="*60 + "\n")

    # 5. 交互确认
    confirm = input("⚠️  警告：以上文件将被永久删除！确定继续吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("🚫 操作已取消。")
        return

    # 6. 执行删除并显示进度条
    print("\n🚀 正在清理图片...")
    total = len(matched_files)
    
    for i, file_path in enumerate(matched_files, 1):
        try:
            os.remove(file_path)
            # 进度条渲染
            percent = (i / total) * 100
            bar_length = 40
            filled = int(bar_length * i // total)
            bar = '█' * filled + '-' * (bar_length - filled)
            sys.stdout.write(f'\r进度: |{bar}| {percent:.1f}% ({i}/{total})')
            sys.stdout.flush()
        except Exception as e:
            print(f"\n❌ 无法删除 {file_path}: {e}")

    print("\n\n✨ 清理完成！非图片文件已安全跳过。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量删除包含指定关键词的图片文件")
    parser.add_argument("path", help="目标文件夹路径")
    
    args = parser.parse_args()
    
    # 关键词列表
    delete_keywords = ['Xav', 'agav', '扫码', '4096', '論壇', '私房猛药']

    delete_images_only(args.path, delete_keywords)