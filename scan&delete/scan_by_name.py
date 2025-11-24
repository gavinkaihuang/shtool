import os
import json
import argparse
from collections import defaultdict

class FilenameScanner:
    def __init__(self, search_paths, extensions=None):
        self.search_paths = search_paths
        # 常见视频格式
        self.extensions = extensions or {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.rmvb', '.ts', '.m4v', '.iso'
        }
        # 字典结构: { "文件名": [ {path: "...", size: 123}, ... ] }
        self.files_map = defaultdict(list)

    def _is_video_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.extensions

    def scan(self):
        print(">>> [阶段1] 正在遍历目录构建文件名索引...")
        count = 0
        
        for path in self.search_paths:
            if not os.path.exists(path):
                print(f"警告: 路径不存在 {path}")
                continue
                
            for root, _, files in os.walk(path):
                for name in files:
                    if self._is_video_file(name):
                        filepath = os.path.join(root, name)
                        try:
                            file_size = os.path.getsize(filepath)
                            self.files_map[name].append({
                                "path": filepath,
                                "size": file_size
                            })
                            count += 1
                        except OSError:
                            pass
                            
        print(f"    扫描完成。共索引了 {count} 个视频文件。")

    def get_duplicates(self):
        """过滤出出现次数大于1的文件"""
        dupes = {}
        for filename, file_info_list in self.files_map.items():
            if len(file_info_list) > 1:
                dupes[filename] = file_info_list
        return dupes

    def save_report(self, output_file):
        dupes = self.get_duplicates()
        if not dupes:
            print(">>> 未发现同名文件。")
            return

        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dupes, f, indent=4, ensure_ascii=False)
        
        print(f">>> 发现 {len(dupes)} 组同名文件。")
        print(f">>> 报告已保存至: {output_file}")

if __name__ == "__main__":
    TARGET_DIRS = ['/mnt/u10tdisk/movies', '/mnt/u12tdisk/movies']
    OUTPUT_JSON = 'duplicate_names.json'

    scanner = FilenameScanner(TARGET_DIRS)
    scanner.scan()
    scanner.save_report(OUTPUT_JSON)