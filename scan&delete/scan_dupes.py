import os
import hashlib
import json
import argparse
from collections import defaultdict

class DuplicateScanner:
    def __init__(self, search_paths, extensions=None):
        self.search_paths = search_paths
        # 常见视频格式，如果为空则扫描所有文件
        self.extensions = extensions or {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.rmvb', '.ts', '.m4v'
        }
        self.size_map = defaultdict(list)
        self.dupes = []

    def _is_video_file(self, filename):
        """检查文件后缀"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.extensions

    def _get_file_hash(self, filepath, block_size=65536):
        """计算文件的MD5哈希，分块读取以节省内存"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for buf in iter(lambda: f.read(block_size), b''):
                    hasher.update(buf)
            return hasher.hexdigest()
        except OSError:
            # 处理权限问题或文件读取错误
            return None

    def scan(self):
        print(">>> [阶段1] 正在遍历目录构建文件大小映射...")
        
        # 1. 遍历目录，按大小分组
        file_count = 0
        for path in self.search_paths:
            if not os.path.exists(path):
                print(f"警告: 路径不存在 {path}")
                continue
                
            for root, _, files in os.walk(path):
                for name in files:
                    if self._is_video_file(name):
                        filepath = os.path.join(root, name)
                        try:
                            # 获取文件大小
                            size = os.path.getsize(filepath)
                            # 只有大于0字节的文件才有意义
                            if size > 0:
                                self.size_map[size].append(filepath)
                                file_count += 1
                        except OSError:
                            pass
        
        print(f"    扫描完成。找到 {file_count} 个视频文件。")
        print(">>> [阶段2] 正在计算哈希以确认重复内容...")

        # 2. 筛选大小相同的文件，并计算哈希
        # 只有当一个大小对应多个文件时，才需要计算哈希
        candidates_groups = [files for size, files in self.size_map.items() if len(files) > 1]
        
        total_groups = len(candidates_groups)
        processed_groups = 0
        
        for files_list in candidates_groups:
            processed_groups += 1
            if processed_groups % 10 == 0:
                print(f"    进度: 处理第 {processed_groups}/{total_groups} 组潜在重复...")

            # 按哈希值再分组
            hash_map = defaultdict(list)
            for filepath in files_list:
                file_hash = self._get_file_hash(filepath)
                if file_hash:
                    hash_map[file_hash].append(filepath)
            
            # 3. 收集真正的重复项
            for f_hash, paths in hash_map.items():
                if len(paths) > 1:
                    self.dupes.append({
                        "hash": f_hash,
                        "size": os.path.getsize(paths[0]),
                        "count": len(paths),
                        "files": paths
                    })

        print(f">>> 扫描结束。发现 {len(self.dupes)} 组重复视频。")

    def save_report(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.dupes, f, indent=4, ensure_ascii=False)
        print(f">>> 报告已保存至: {output_file}")

if __name__ == "__main__":
    # 定义需要扫描的目录
    TARGET_DIRS = ['/mnt/u10tdisk/movies', '/mnt/u12tdisk/movies']
    OUTPUT_JSON = 'duplicate_videos.json'

    scanner = DuplicateScanner(TARGET_DIRS)
    scanner.scan()
    scanner.save_report(OUTPUT_JSON)