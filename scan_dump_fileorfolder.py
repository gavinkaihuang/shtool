###

###列出指定目录下的重复文件和文件夹

###

#!/usr/bin/env python3
import os
import hashlib
from collections import defaultdict
import argparse

def file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def dir_fingerprint(dir_path):
    """计算目录的指纹：递归计算所有文件内容的哈希，并排序子目录结构"""
    fingerprint = hashlib.md5()
    files = []
    
    for root, dirs, filenames in os.walk(dir_path):
        # 排序目录和文件以确保一致性
        dirs.sort()
        filenames.sort()
        
        # 添加当前路径的相对路径
        rel_root = os.path.relpath(root, dir_path)
        if rel_root != '.':
            fingerprint.update(rel_root.encode('utf-8'))
            fingerprint.update(b'/')
        
        # 添加文件名
        for filename in filenames:
            file_path = os.path.join(root, filename)
            rel_file = os.path.relpath(file_path, dir_path)
            files.append(rel_file)
            files.append(file_hash(file_path))
    
    # 排序文件列表并更新哈希
    files.sort()
    for item in files:
        fingerprint.update(item.encode('utf-8'))
    
    return fingerprint.hexdigest()

def scan_duplicates(root_dir, min_duplicates=2):
    """扫描目录中的重复文件和重复目录"""
    file_dups = defaultdict(list)  # hash -> list of paths
    dir_dups = defaultdict(list)   # fingerprint -> list of dir paths
    
    # 扫描文件
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                h = file_hash(file_path)
                file_dups[h].append(file_path)
            except (IOError, OSError):
                print(f"Warning: Cannot read {file_path}")
    
    # 扫描目录（只检查有子内容的目录）
    for root, dirs, files in os.walk(root_dir):
        if dirs or files:  # 只检查非空目录
            try:
                fp = dir_fingerprint(root)
                dir_dups[fp].append(root)
            except (IOError, OSError):
                print(f"Warning: Cannot access {root}")
    
    # 过滤重复项（至少min_duplicates个）
    file_groups = {k: v for k, v in file_dups.items() if len(v) >= min_duplicates}
    dir_groups = {k: v for k, v in dir_dups.items() if len(v) >= min_duplicates}
    
    return file_groups, dir_groups

def print_tree(parent, children, label):
    """打印树状结构"""
    print(f"{label}: {parent}")
    for child in children:
        print(f"  └── {child}")

def main():
    parser = argparse.ArgumentParser(description="扫描目录中的重复文件和子目录")
    parser.add_argument("directory", help="要扫描的目录路径")
    parser.add_argument("--min-dups", type=int, default=2, help="最小重复数量 (默认: 2)")
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    if not os.path.exists(root_dir):
        print(f"Error: Directory {root_dir} does not exist.")
        return
    
    print(f"扫描目录: {root_dir}")
    file_groups, dir_groups = scan_duplicates(root_dir, args.min_duplicates)
    
    print("\n=== 重复文件 ===")
    for hash_key, paths in file_groups.items():
        parent = paths[0]
        children = paths[1:]
        print_tree(parent, children, f"文件组 (hash: {hash_key[:8]}...)")
    
    print("\n=== 重复子目录 ===")
    for fp_key, dirpaths in dir_groups.items():
        parent = dirpaths[0]
        children = dirpaths[1:]
        print_tree(parent, children, f"目录组 (fingerprint: {fp_key[:8]}...)")

if __name__ == "__main__":
    main()