import os
import json
import argparse
import sys
from minio import Minio
from minio.error import S3Error

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误: 无法读取配置文件 {config_path}。{e}")
        sys.exit(1)

def upload_images(image_dir, config):
    """上传图片至 Minio"""
    # 初始化客户端
    client = Minio(
        config['endpoint'],
        access_key=config['access_key'],
        secret_key=config['secret_key'],
        secure=config.get('secure', False)
    )

    bucket_name = config['bucket_name']

    try:
        # 检查存储桶是否存在，不存在则创建
        if not client.bucket_exists(bucket_name):
            print(f"存储桶 '{bucket_name}' 不存在，正在创建...")
            client.make_bucket(bucket_name)
        else:
            print(f"已连接至存储桶: {bucket_name}")

        # 扫描目录下的图片文件
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.tiff')
        files_to_upload = [
            f for f in os.listdir(image_dir) 
            if f.lower().endswith(valid_extensions)
        ]

        if not files_to_upload:
            print(f"目录 {image_dir} 中未发现图片文件。")
            return

        print(f"共发现 {len(files_to_upload)} 张图片，开始上传...")

        for file_name in sorted(files_to_upload):
            file_path = os.path.join(image_dir, file_name)
            
            # 执行上传
            # object_name 可以保持原名，也可以根据需求增加前缀（如 book_v1/page_001.png）
            client.fput_object(
                bucket_name=bucket_name,
                object_name=file_name,
                file_path=file_path
            )
            print(f"成功上传: {file_name}")

    except S3Error as e:
        print(f"Minio S3 错误: {e}")
    except Exception as e:
        print(f"发生意外错误: {e}")

def main():
    parser = argparse.ArgumentParser(description="Minio 图片批量上传工具")
    parser.add_argument("-d", "--dir", required=True, help="图片所在的本地目录路径")
    parser.add_argument("-c", "--config", default="config.json", help="配置文件路径 (默认: config.json)")
    
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"错误: 路径 '{args.dir}' 不是有效的目录")
        sys.exit(1)

    config = load_config(args.config)
    upload_images(args.dir, config)

if __name__ == "__main__":
    main()