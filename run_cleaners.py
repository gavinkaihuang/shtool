#!/usr/bin/env python3

/***
基本用法 (需要手动确认)
运行脚本并指定目标目录。脚本会依次执行三个清理任务，每个任务在删除前都会询问你。
bash
python3 run_cleaners.py /Users/yourname/Downloads/target_folder

自动确认 (无须人工干预)
如果你确定要删除且不想每次都输入 y 确认，可以加上 --no-confirm 参数。
bash
python3 run_cleaners.py /Users/yourname/Downloads/target_folder --no-confirm

脚本执行流程
删除小视频: 扫描并删除小于 100MB 的视频文件。
删除特定文件: 扫描并删除 .txt, .url, .html, .apk 等文件。
删除空目录: 最后扫描并清理剩下的空文件夹。

***/

import os
import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Run multiple cleanup scripts sequentially on a target directory.")
    parser.add_argument("directory", help="The directory to clean up.")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompts for all scripts.")
    
    args = parser.parse_args()
    target_dir = os.path.abspath(args.directory)

    if not os.path.exists(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    # scripts to run in order
    scripts = [
        "delete_small_videos.py",
        "find_and_delete_files.py",
        "delete_empty_folder.py"
    ]

    # Get the directory where this script is located
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    for script_name in scripts:
        script_path = os.path.join(current_script_dir, script_name)
        
        if not os.path.exists(script_path):
            print(f"Warning: Script '{script_name}' not found at {script_path}. Skipping.")
            continue

        print(f"\n{'='*20} Running {script_name} {'='*20}\n")
        
        cmd = [sys.executable, script_path, target_dir]
        
        if args.no_confirm:
            cmd.append("--no-confirm")

        try:
            # Run the script and wait for it to finish. 
            # stdin/stdout/stderr are inherited so user can interact if needed.
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\nError running {script_name}: {e}")
            # Decide whether to stop or continue. Usually one failing might affect others, 
            # but for cleanup, we might want to continue.
            # However, if the user Ctrl-Cs, we should probably stop.
            pass
        except KeyboardInterrupt:
            print("\nSequence interrupted by user.")
            sys.exit(130)

    print(f"\n{'='*20} All cleanup tasks finished {'='*20}")

if __name__ == "__main__":
    main()
