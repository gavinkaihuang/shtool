import os
import subprocess
import csv
import argparse
import sys

# 视频后缀名定义
VIDEO_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
# 报告输出路径
REPORT_FILE = "video_health_report.csv"

def check_video_health(file_path):
    """
    使用 ffprobe 检查视频状态
    返回值: (status, detail)
    """
    # 基础命令：检查是否能读取流信息
    cmd = [
        'ffprobe', '-v', 'error', 
        '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', 
        file_path
    ]
    
    try:
        # 1. 尝试获取时长（如果获取不到，文件头基本损坏）
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return "损坏", "无法读取文件头/索引"
        
        duration = result.stdout.strip()
        if not duration:
            return "异常", "时长信息缺失"

        # 2. 进一步尝试读取文件尾部（可选，防止下载中途截断）
        # 仅读取最后 5 秒数据，兼顾速度与准确性
        check_tail = [
            'ffmpeg', '-v', 'error', '-sseof', '-5', 
            '-i', file_path, '-f', 'null', '-'
        ]
        tail_result = subprocess.run(check_tail, capture_output=True, text=True, timeout=30)
        if tail_result.returncode != 0:
            return "不完整", "文件尾部损坏或未下载完"

        return "健康", f"时长: {float(duration):.2f}s"

    except subprocess.TimeoutExpired:
        return "超时", "扫描时间过长，可能存在严重逻辑坏道"
    except Exception as e:
        return "错误", str(e)

def main():
    parser = argparse.ArgumentParser(description="扫描目录中的视频文件并检查是否损坏")
    parser.add_argument("video_dir", nargs="?", help="要扫描的视频目录路径")
    args = parser.parse_args()

    video_dir = args.video_dir or input("请输入要扫描的视频目录路径: ").strip()
    if not video_dir:
        print("未提供目录路径，程序退出。")
        sys.exit(1)

    if not os.path.isdir(video_dir):
        print(f"目录不存在或不是有效目录: {video_dir}")
        sys.exit(1)

    results = []
    print(f"开始扫描目录: {video_dir} ...")
    
    for root, dirs, files in os.walk(video_dir):
        for file in files:
            if file.lower().endswith(VIDEO_EXTS):
                full_path = os.path.join(root, file)
                print(f"正在检查: {file}", end='\r')
                status, detail = check_video_health(full_path)
                results.append([file, status, detail, full_path])

    # 保存报告
    with open(REPORT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['文件名', '状态', '详情', '完整路径'])
        writer.writerows(results)

    print(f"\n扫描完成！报告已保存至: {REPORT_FILE}")
    
    # 统计简报
    broken = [r for r in results if r[1] != "健康"]
    if broken:
        print(f"发现 {len(broken)} 个问题文件，请查看 CSV 报告。")
    else:
        print("所有视频文件均表现正常。")

if __name__ == "__main__":
    main()