import google.generativeai as genai
import config  # 导入您的 config.py

genai.configure(api_key=config.API_KEY)

print("正在查询可用模型列表...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"查询出错: {e}")