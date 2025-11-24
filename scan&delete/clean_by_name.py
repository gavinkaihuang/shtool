import json
import os
import argparse
import sys

class FilenameCleaner:
    def __init__(self, report_file, dry_run=True, strict_size=True):
        self.report_file = report_file
        self.dry_run = dry_run
        self.strict_size = strict_size # 如果为True，文件大小不同时不删除
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
            return

        print(f"{'[模拟运行]' if self.dry_run else '[正式执行]'} 开始清理...")
        if self.strict_size:
            print(">>> 安全模式已开启：如果同名文件大小不一致，将跳过处理。")
        print("-" * 60)

        for filename, file_list in data.items():
            # 1. 检查文件大小一致性 (安全措施)
            sizes = [f['size'] for f in file_list]
            # 如果集合长度大于1，说明有不同的大小
            if self.strict_size and len(set(sizes)) > 1:
                print(f"[跳过] 警告: '{filename}' 的副本大小不一致，疑似不同版本，建议人工检查。")
                for f in file_list:
                    print(f"      - {f['size']/1024/1024:.1f}MB: {f['path']}")
                print("-" * 60)
                continue

            # 2. 排序策略 (保留哪一个？)
            # 默认按路径排序。你可以修改 lambda 优先保留特定硬盘
            # 例如：优先保留 /mnt/u10t 下的文件
            file_list.sort(key=lambda x: 0 if '/mnt/u10t/' in x['path'] else 1)

            keep_item = file_list[0]
            delete_items = file_list[1:]

            print(f"处理: {filename}")
            print(f"  [保留] {keep_item['path']} ({keep_item['size']/1024/1024:.1f} MB)")

            for item in delete_items:
                f_path = item['path']
                if self.dry_run:
                    print(f"  [待删] {f_path}")
                else:
                    try:
                        os.remove(f_path)
                        print(f"  [已删] {f_path}")
                        self.deleted_count += 1
                    except OSError as e:
                        print(f"  [失败] {f_path} : {e}")
            
            print("-" * 60)

        if self.dry_run:
            print("\n>>> 模拟结束。使用 --execute 参数执行删除。")
        else:
            print(f"\n>>> 清理结束。共删除 {self.deleted_count} 个文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="基于文件名删除重复视频")
    parser.add_argument('--file', type=str, default='duplicate_names.json', help='JSON报告路径')
    parser.add_argument('--execute', action='store_true', help='确认执行删除')
    # 增加一个强制参数，允许删除大小不一样的同名文件
    parser.add_argument('--force-diff-size', action='store_true', help='危险：即使文件大小不同，也强制按文件名删除')
    
    args = parser.parse_args()

    # 如果用户加了 --force-diff-size，则 strict_size 为 False
    cleaner = FilenameCleaner(
        args.file, 
        dry_run=not args.execute,
        strict_size=not args.force_diff_size
    )
    cleaner.clean()