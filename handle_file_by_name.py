#!/usr/bin/env python3
import os
import shutil
from collections import defaultdict
import argparse
from datetime import datetime

def find_videos(root_dir, extensions):
    """递归查找视频文件"""
    videos = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                full_path = os.path.join(root, file)
                videos.append(full_path)
    return videos

def group_by_filename(videos):
    """按文件名分组视频文件"""
    groups = defaultdict(list)
    for path in videos:
        filename = os.path.basename(path)
        groups[filename].append(path)
    return groups

def create_dump_dir(parent_dir):
    """在上级目录创建 dump 目录"""
    dump_dir = os.path.join(parent_dir, "dump")
    os.makedirs(dump_dir, exist_ok=True)
    return dump_dir

def move_duplicate(dump_dir, path, timestamp):
    """移动文件到 dump 目录，并添加时间戳"""
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    new_path = os.path.join(dump_dir, new_filename)
    
    try:
        shutil.move(path, new_path)
        print(f"已移动: {path} -> {new_path}")
        return True
    except OSError as e:
        print(f"移动失败: {path} - {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="扫描指定目录，移动重复视频文件到上级 dump 目录")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认，直接移动（谨慎使用！）")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: 目录 {root_dir} 不存在。")
        return
    
    # 常见视频扩展名
    extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv')
    
    # 创建 dump 目录
    parent_dir = os.path.dirname(root_dir)
    dump_dir = create_dump_dir(parent_dir)
    print(f"Dump 目录: {dump_dir}")
    
    # 扫描视频
    print(f"扫描目录: {root_dir}")
    videos = find_videos(root_dir, extensions)
    if not videos:
        print("未找到视频文件。")
        return
    
    print(f"找到 {len(videos)} 个视频文件。")
    
    # 按文件名分组
    groups = group_by_filename(videos)
    
    # 统计重复
    duplicates = [(fname, paths) for fname, paths in groups.items() if len(paths) > 1]
    total_dups = sum(len(paths) - 1 for _, paths in duplicates)
    
    if total_dups == 0:
        print("未找到重复文件名。")
        return
    
    print(f"找到 {len(duplicates)} 个重复文件名组，共 {total_dups} 个重复文件。")
    
    # 列出重复文件
    for fname, paths in duplicates:
        print(f"\n文件名: {fname} (重复 {len(paths)} 个)")
        for path in paths:
            print(f"  - {path}")
    
    # 确认
    if not args.no_confirm:
        confirm = input(f"\n确认移动 {total_dups} 个重复视频文件到 dump 目录？(y/N): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            return
    
    # 执行移动
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    moved_count = 0
    for fname, paths in duplicates:
        # 保留第一个，移动其余
        for path in paths[1:]:
            if move_duplicate(dump_dir, path, timestamp):
                moved_count += 1
    
    print(f"\n移动完成: 总共移动 {moved_count} 个文件。")

if __name__ == "__main__":
    main()