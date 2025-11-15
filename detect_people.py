import cv2
import telegram
import time
from datetime import datetime
import configparser
import os

# --- 从配置文件中加载配置 ---
config = configparser.ConfigParser()
config_file_path = 'config.ini'

if not os.path.exists(config_file_path):
    print(f"错误: 配置文件 '{config_file_path}' 不存在。")
    print("请创建一个包含 [telegram] bot_token 和 chat_id 的 config.ini 文件。")
    exit()

try:
    config.read(config_file_path)
    BOT_TOKEN = config['telegram']['bot_token']
    CHAT_ID = config['telegram']['chat_id']
    CAPTURE_INTERVAL = int(config['camera']['capture_interval_seconds'])
except KeyError as e:
    print(f"错误: 配置文件 '{config_file_path}' 缺少必要的配置项: {e}")
    exit()

# --- 初始化 Telegram 机器人 ---
bot = telegram.Bot(token=BOT_TOKEN)

# --- 初始化摄像头 ---
cap = cv2.VideoCapture(0)

# 设置截图频率
last_capture_time = time.time()

print("树莓派监控程序已启动，等待人脸检测...")
print(f"截图频率设置为每 {CAPTURE_INTERVAL} 秒一次。")

def send_telegram_notification(image_path):
    """发送 Telegram 通知和图片"""
    try:
        with open(image_path, 'rb') as photo:
            bot.send_photo(chat_id=CHAT_ID, photo=photo, caption='检测到有人，已自动截屏。')
        print(f"成功发送通知到 Telegram，图片: {image_path}")
    except telegram.error.TelegramError as e:
        print(f"发送 Telegram 消息失败: {e}")
    except FileNotFoundError:
        print(f"错误: 图片文件 {image_path} 不存在。")

def detect_and_capture():
    """检测人脸并根据频率截屏"""
    global last_capture_time

    # 加载人脸识别模型
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    ret, frame = cap.read()
    if not ret:
        print("无法从摄像头读取图像。请检查摄像头连接或权限。")
        return

    # 将图像转为灰度图，以提高处理速度
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 检测人脸
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # 如果检测到人脸
    if len(faces) > 0:
        print(f"检测到人脸，数量: {len(faces)}")
        current_time = time.time()

        # 检查是否到了截屏频率
        if current_time - last_capture_time >= CAPTURE_INTERVAL:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"capture_{timestamp}.jpg"
            cv2.imwrite(image_path, frame)
            print(f"检测到人，正在截屏并发送通知：{image_path}")
            send_telegram_notification(image_path)
            last_capture_time = current_time

try:
    while True:
        detect_and_capture()
        # 小幅延时，避免 CPU 过载
        time.sleep(1)

except KeyboardInterrupt:
    print("程序被用户终止。")
finally:
    # 释放摄像头资源
    cap.release()
    cv2.destroyAllWindows()
    print("摄像头资源已释放，程序退出。")