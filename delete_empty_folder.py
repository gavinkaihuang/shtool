###
###基本用法：python3 empty_dir_cleaner.py /path/to/your/directory
###脚本会先列出所有空目录，然后询问确认（输入 y 确认删除）。

###跳过确认（危险！）：python3 empty_dir_cleaner.py /path/to/directory --no-confirm
###示例输出（部分）：text在目录 /home/user/docs 下找到 2 个空目录：
 ### - /home/user/docs/empty_folder1
 ### - /home/user/docs/sub/empty_sub

###确认删除所有以上空目录？(y/N): y

###开始删除...
###已删除空目录: /home/user/docs/sub/empty_sub
###已删除空目录: /home/user/docs/empty_folder1

###除完成: 2 个空目录成功删除。


###

#!/usr/bin/env python3
import os
import argparse

def find_empty_dirs(root_dir):
    """递归查找空目录"""
    empty_dirs = []
    for root, dirs, files in os.walk(root_dir, topdown=False):  # topdown=False 以从叶子开始
        if not dirs and not files:  # 如果没有子目录和文件，则为空
            empty_dirs.append(root)
    return empty_dirs

def delete_dirs(dirs_list):
    """删除目录列表，并打印删除结果"""
    deleted = []
    errors = []
    for dir_path in dirs_list:
        try:
            os.rmdir(dir_path)  # 只删除空目录
            deleted.append(dir_path)
            print(f"已删除空目录: {dir_path}")
        except OSError as e:
            errors.append((dir_path, str(e)))
            print(f"删除失败: {dir_path} - {e}")
    return deleted, errors

def main():
    parser = argparse.ArgumentParser(description="找出并删除指定目录下的所有空目录")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认，直接删除（谨慎使用！）")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: 目录 {root_dir} 不存在。")
        return
    
    empty_dirs = find_empty_dirs(root_dir)
    
    if not empty_dirs:
        print("未找到空目录。")
        return
    
    print(f"在目录 {root_dir} 下找到 {len(empty_dirs)} 个空目录：")
    for dir_path in sorted(empty_dirs):  # 排序以便阅读
        print(f"  - {dir_path}")
    
    # 确认删除
    if not args.no_confirm:
        confirm = input("\n确认删除所有以上空目录？(y/N): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            return
    
    print("\n开始删除...")
    deleted, errors = delete_dirs(empty_dirs)
    
    print(f"\n删除完成: {len(deleted)} 个空目录成功删除。")
    if errors:
        print("删除失败的目录:")
        for dir_path, err in errors:
            print(f"  - {dir_path}: {err}")

if __name__ == "__main__":
    main()