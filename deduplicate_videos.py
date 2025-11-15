#!/usr/bin/env python3
import os
import json
import argparse
from collections import defaultdict

def load_index(index_file):
    """加载索引文件"""
    if not os.path.exists(index_file):
        print(f"Error: 索引文件 {index_file} 不存在。请先运行扫描脚本生成索引。")
        return None
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_list = json.load(f)
    
    # 按MD5分组
    video_index = defaultdict(list)
    for item in index_list:
        md5 = item["md5"]
        video_index[md5].append(item)
    
    return video_index

def delete_duplicates(video_index, root_dir):
    """删除重复文件，只保留第一个"""
    deleted = 0
    for md5, items in video_index.items():
        if len(items) > 1:
            # 保留第一个，删除其余
            first_path = items[0]["path"]
            print(f"\nMD5: {md5[:8]}... (重复 {len(items)} 个文件)")
            print(f"  保留: {first_path}")
            
            for item in items[1:]:
                path = item["path"]
                try:
                    os.remove(path)
                    deleted += 1
                    print(f"  已删除: {path}")
                except OSError as e:
                    print(f"  删除失败: {path} - {e}")
    
    print(f"\n删除完成: 总共删除 {deleted} 个重复文件。")

def main_delete():
    parser = argparse.ArgumentParser(description="根据索引删除指定目录下的重复视频文件，只保留第一个")
    parser.add_argument("directory", help="指定目录路径（索引文件在该目录下）")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认，直接删除（谨慎使用！）")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: 目录 {root_dir} 不存在。")
        return
    
    index_file = os.path.join(root_dir, "video_md5_index.json")
    video_index = load_index(index_file)
    if not video_index:
        return
    
    # 统计重复组
    dup_count = sum(1 for items in video_index.values() if len(items) > 1)
    total_dups = sum(max(0, len(items) - 1) for items in video_index.values())
    
    print(f"在目录 {root_dir} 下找到 {dup_count} 个重复组，共 {total_dups} 个重复文件。")
    
    if total_dups == 0:
        print("无重复文件需要删除。")
        return
    
    # 确认删除
    if not args.no_confirm:
        confirm = input(f"\n确认删除 {total_dups} 个重复视频文件？(y/N): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            return
    
    delete_duplicates(video_index, root_dir)

if __name__ == "__main__":
    main_delete()