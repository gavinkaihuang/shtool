import os
import sys
import argparse

def delete_with_confirm(target_dir, keywords):
    # 1. 检查路径是否存在
    if not os.path.exists(target_dir):
        print(f"错误: 路径 '{target_dir}' 不存在！")
        return

    # 2. 预处理关键词并扫描
    lower_keywords = [k.lower() for k in keywords]
    matched_files = []

    print(f"🔍 正在扫描: {os.path.abspath(target_dir)}")
    
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if any(key in file.lower() for key in lower_keywords):
                matched_files.append(os.path.join(root, file))

    if not matched_files:
        print("✅ 未发现匹配关键词的文件。")
        return

    # 3. 打印待删除列表供确认
    print("\n" + "="*60)
    print(f"📝 待删除文件列表 (总计: {len(matched_files)} 个):")
    for path in matched_files:
        print(f"  [等待删除] {path}")
    print("="*60 + "\n")

    # 4. 交互确认
    confirm = input("⚠️  确定要永久删除以上所有文件吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("🚫 操作已取消。")
        return

    # 5. 执行删除并显示进度条
    print("\n🚀 开始清理...")
    total = len(matched_files)
    
    for i, file_path in enumerate(matched_files, 1):
        try:
            os.remove(file_path)
            # 进度条渲染
            percent = (i / total) * 100
            bar_length = 40
            filled_length = int(bar_length * i // total)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            sys.stdout.write(f'\r进度: |{bar}| {percent:.1f}% ({i}/{total})')
            sys.stdout.flush()
        except Exception as e:
            print(f"\n❌ 无法删除 {file_path}: {e}")

    print("\n\n✨ 任务完成！清理干净了。")

if __name__ == "__main__":
    # 配置命令行参数
    parser = argparse.ArgumentParser(description="根据关键词批量删除图片脚本 (不区分大小写)")
    parser.add_argument("path", help="指定要扫描的目标文件夹路径")
    
    args = parser.parse_args()

    # 关键词硬编码在脚本内（你也可以根据需要改为参数传入）
    delete_keywords = ['Xav', 'agav', '扫码', '4096', '論壇', '私房猛药']

    delete_with_confirm(args.path, delete_keywords)