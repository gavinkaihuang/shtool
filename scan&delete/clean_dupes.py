import json
import os
import argparse
import sys

class DuplicateCleaner:
    def __init__(self, report_file, dry_run=True):
        self.report_file = report_file
        self.dry_run = dry_run
        self.deleted_size = 0
        self.deleted_count = 0

    def load_report(self):
        if not os.path.exists(self.report_file):
            print("错误: 找不到报告文件。")
            sys.exit(1)
        with open(self.report_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clean(self):
        data = self.load_report()
        
        if not data:
            print("报告中没有发现重复文件。")
            return

        print(f"{'[模拟运行]' if self.dry_run else '[正式执行]'} 开始清理...")
        print("-" * 60)

        for item in data:
            files = item['files']
            size = item['size']
            
            # --- 保留策略 ---
            # 目前策略：按字母顺序排序，保留第一个，删除其余所有。
            # 你可以在这里修改逻辑，例如优先保留 '/mnt/u10t' 下的文件。
            files.sort() 
            
            file_to_keep = files[0]
            files_to_delete = files[1:]

            print(f"保留: {file_to_keep}")
            
            for file_path in files_to_delete:
                if self.dry_run:
                    print(f"  [待删除] {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        print(f"  [已删除] {file_path}")
                        self.deleted_count += 1
                        self.deleted_size += size
                    except OSError as e:
                        print(f"  [删除失败] {file_path} : {e}")
            print("-" * 60)

        # 总结
        if self.dry_run:
            print("\n>>> 模拟运行结束。没有文件被删除。")
            print(">>> 请使用 --execute 参数再次运行以执行实际删除。")
        else:
            print("\n>>> 清理完成。")
            print(f">>> 共删除文件: {self.deleted_count} 个")
            print(f">>> 释放空间: {self.deleted_size / (1024*1024*1024):.2f} GB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="基于JSON报告删除重复视频文件")
    parser.add_argument('--file', type=str, default='duplicate_videos.json', help='输入的JSON报告文件路径')
    # 必须显式添加 --execute 才会真的删除，否则默认空跑
    parser.add_argument('--execute', action='store_true', help='确认执行删除操作（不可撤销）')
    
    args = parser.parse_args()

    # 如果没有传入 --execute，dry_run 为 True
    cleaner = DuplicateCleaner(args.file, dry_run=not args.execute)
    cleaner.clean()