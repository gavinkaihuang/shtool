#!/usr/bin/env python3
import os
import argparse
import sys

def get_args():
    parser = argparse.ArgumentParser(description="Recursively delete video files smaller than a specified size.")
    parser.add_argument("directory", help="The directory to scan.")
    parser.add_argument("--size", "-s", type=float, default=100, help="File size threshold in MB (default: 100). Files smaller than this will be deleted.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and list files without deleting them.")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation prompt before deleting.")
    return parser.parse_args()

def is_video_file(filename):
    video_extensions = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', 
        '.mpg', '.mpeg', '.3gp', '.ts', '.rmvb', '.vob'
    }
    return os.path.splitext(filename)[1].lower() in video_extensions

def main():
    args = get_args()
    target_dir = args.directory
    size_threshold_mb = args.size
    size_threshold_bytes = size_threshold_mb * 1024 * 1024

    if not os.path.isdir(target_dir):
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    files_to_delete = []

    print(f"Scanning '{target_dir}' for video files smaller than {size_threshold_mb} MB...")

    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if is_video_file(file):
                    file_size = os.path.getsize(file_path)
                    if file_size < size_threshold_bytes:
                        files_to_delete.append((file_path, file_size))
            except OSError as e:
                print(f"Error accessing file {file_path}: {e}")

    if not files_to_delete:
        print("No matching files found.")
        return

    print(f"\nFound {len(files_to_delete)} files to delete:")
    for path, size in files_to_delete:
        size_mb = size / (1024 * 1024)
        print(f"  {path} ({size_mb:.2f} MB)")

    if args.dry_run:
        print("\n[Dry Run] No files were deleted.")
        return

    if not args.no_confirm:
        confirm = input("\nAre you sure you want to delete these files? (y/N): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return

    print("\nDeleting files...")
    deleted_count = 0
    for path, _ in files_to_delete:
        try:
            os.remove(path)
            print(f"Deleted: {path}")
            deleted_count += 1
        except OSError as e:
            print(f"Failed to delete {path}: {e}")

    print(f"\nOperation complete. Deleted {deleted_count} files.")

if __name__ == "__main__":
    main()
