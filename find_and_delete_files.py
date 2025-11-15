###

###基本用法 python3 file_deleter.py /path/to/your/directory
###脚本会先列出所有匹配文件，然后询问确认（输入 y 确认删除）。

###跳过确认（危险！）python3 file_deleter.py /path/to/directory --no-confirm
###示例输出（部分）：text在目录 /home/user/docs 下找到 3 个匹配文件：
###  - /home/user/docs/note.txt
###  - /home/user/docs/page.html
### - /home/user/docs/app.apk

###确认删除所有以上文件？(y/N): y

###开始删除...
###已删除: /home/user/docs/note.txt
###已删除: /home/user/docs/page.html
###已删除: /home/user/docs/app.apk

###删除完成: 3 个文件成功删除。

###


#!/usr/bin/env python3
import os
import argparse

def find_files(root_dir, extensions):
    """递归查找指定扩展名的文件"""
    matching_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(tuple(extensions)):
                full_path = os.path.join(root, file)
                matching_files.append(full_path)
    return matching_files

def delete_files(files):
    """删除文件列表，并打印删除结果"""
    deleted = []
    errors = []
    for file_path in files:
        try:
            os.remove(file_path)
            deleted.append(file_path)
            print(f"已删除: {file_path}")
        except OSError as e:
            errors.append((file_path, str(e)))
            print(f"删除失败: {file_path} - {e}")
    return deleted, errors

def main():
    parser = argparse.ArgumentParser(description="遍历、打印并删除指定文件夹下的txt、url、html、htm、mhtml、apk文件")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认，直接删除（谨慎使用！）")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: 目录 {root_dir} 不存在。")
        return
    
    extensions = ('.txt', '.url', '.html', '.htm', '.mhtml', '.apk')
    files = find_files(root_dir, extensions)
    
    if not files:
        print("未找到匹配的文件。")
        return
    
    print(f"在目录 {root_dir} 下找到 {len(files)} 个匹配文件：")
    for file_path in sorted(files):  # 排序以便阅读
        print(f"  - {file_path}")
    
    # 确认删除
    if not args.no_confirm:
        confirm = input("\n确认删除所有以上文件？(y/N): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            return
    
    print("\n开始删除...")
    deleted, errors = delete_files(files)
    
    print(f"\n删除完成: {len(deleted)} 个文件成功删除。")
    if errors:
        print("删除失败的文件:")
        for file_path, err in errors:
            print(f"  - {file_path}: {err}")

if __name__ == "__main__":
    main()