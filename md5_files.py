#!/usr/bin/env python3
import os
import hashlib
import json
from collections import defaultdict
import argparse

def file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except (IOError, OSError):
        print(f"Warning: Cannot read {file_path}")
        return None
    return hash_md5.hexdigest()

def scan_videos(root_dir, extensions):
    """扫描视频文件，计算MD5，并分组"""
    video_index = defaultdict(list)  # md5 -> list of {"filename": , "path": }
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                full_path = os.path.join(root, file)
                h = file_hash(full_path)
                if h:
                    video_index[h].append({
                        "filename": file,
                        "path": full_path
                    })
    
    return video_index

def save_index(video_index, index_file):
    """保存索引到JSON文件"""
    # 转换为列表格式，便于排序和保存
    index_list = []
    for md5, items in video_index.items():
        for item in items:
            item_copy = item.copy()
            item_copy["md5"] = md5
            index_list.append(item_copy)
    
    # 按路径排序
    index_list.sort(key=lambda x: x["path"])
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_list, f, ensure_ascii=False, indent=2)
    
    print(f"索引已保存到: {index_file}")
    print(f"总视频文件数: {len(index_list)}")

def main_scan():
    parser = argparse.ArgumentParser(description="扫描指定目录下的视频文件，生成MD5索引文件")
    parser.add_argument("directory", help="要扫描的目录路径")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: 目录 {root_dir} 不存在。")
        return
    
    # 常见视频扩展名（可扩展）
    extensions = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv')
    
    print(f"扫描目录: {root_dir}")
    video_index = scan_videos(root_dir, extensions)
    index_file = os.path.join(root_dir, "video_md5_index.json")
    
    save_index(video_index, index_file)

if __name__ == "__main__":
    main_scan()