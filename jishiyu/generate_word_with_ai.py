import pandas as pd
from openai import OpenAI
import time
import json
import os

# ================= 配置区域 =================
# 1. 填入你的 DeepSeek API Key
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 

# 2. 文件设置
INPUT_FILE = '及时雨高考英语词汇手册.csv'
OUTPUT_FILE = '及时雨单词书_DeepSeek补全版.csv'

# 3. 批量大小
# DeepSeek 处理长文本能力很强，一次处理 20 个既快又稳
BATCH_SIZE = 20  
# ===========================================

# 初始化客户端 (DeepSeek 兼容 OpenAI SDK)
client = OpenAI(
    api_key='sk-4ed1bc3715ed4b3d9c6dac47a65fee85',
    base_url="https://api.deepseek.com"
)

def get_batch_info_deepseek(batch_df):
    """
    使用 DeepSeek 获取单词详情
    """
    # 1. 构造输入文本
    words_list_str = ""
    for idx, row in batch_df.iterrows():
        # 简单清理定义中的换行
        safe_def = str(row['Definition']).replace('\n', ' ')[:60]
        words_list_str += f'{{"id": {idx}, "word": "{row["Word"]}", "definition": "{safe_def}"}},\n'

    # 2. 编写提示词 (System Prompt + User Prompt)
    system_prompt = """
    你是一位资深的高考英语教师。
    请接收一个包含单词ID、单词和定义的JSON列表。
    为每个单词补充以下信息，并以 JSON 格式返回：
    
    1. pronunciation: 国际音标 (如 /əˈbændən/)
    2. grammar: 1-4个高考常考短语搭配 (如 abandon oneself to)
    3. example: 1个简练的例句，包含中文翻译 (例句难度适配高考)
    
    必须严格返回如下 JSON 结构，不要包含 markdown 标记：
    {
        "words": [
            {"id": 123, "pronunciation": "...", "grammar": "...", "example": "..."},
            {"id": 124, "pronunciation": "...", "grammar": "...", "example": "..."}
        ]
    }
    """

    user_prompt = f"请处理以下单词列表：\n[\n{words_list_str}\n]"

    # 3. 发送请求 (带重试机制)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",  # 指定使用 DeepSeek V3
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={ "type": "json_object" }, # 强制 JSON 模式，极其稳定
                temperature=0.1, # 低温度保证答案准确
                max_tokens=4096
            )
            
            content = response.choices[0].message.content
            
            # 解析 JSON
            data = json.loads(content)
            
            # 兼容性处理：有时它返回列表，有时返回包含 key 的字典
            if "words" in data:
                return data["words"]
            elif isinstance(data, list):
                return data
            else:
                # 尝试找字典里是不是还有别的 key 存了列表
                for k, v in data.items():
                    if isinstance(v, list):
                        return v
                return []

        except Exception as e:
            print(f"  > [警告] 请求出错 (尝试 {attempt+1}/{max_retries}): {e}")
            if "rate limit" in str(e).lower() or "429" in str(e):
                time.sleep(5) # 稍微歇一下
            else:
                time.sleep(2)
    
    return []

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"找不到文件: {INPUT_FILE}")
        return

    print("正在读取文件...")
    # 读取原始 CSV
    df = pd.read_csv(INPUT_FILE, header=None, names=['Word', 'Definition'])

    # 断点续传逻辑
    if os.path.exists(OUTPUT_FILE):
        print("发现已有结果文件，正在加载以继续处理...")
        df_result = pd.read_csv(OUTPUT_FILE)
        # 补齐列名（防止旧文件没有这些列）
        for col in ['Pronunciation', 'Grammar', 'Example']:
            if col not in df_result.columns:
                df_result[col] = ''
    else:
        df_result = df.copy()
        df_result['Pronunciation'] = ''
        df_result['Grammar'] = ''
        df_result['Example'] = ''

    total_len = len(df_result)
    print(f"开始处理，共 {total_len} 个单词，预计耗时 10-20 分钟。")

    # 开始循环
    for i in range(0, total_len, BATCH_SIZE):
        batch_slice = df_result.iloc[i : i+BATCH_SIZE]
        
        # 检查跳过逻辑：如果这一批第一个词已经有音标了，就跳过
        first_idx = batch_slice.index[0]
        curr_pron = str(batch_slice.at[first_idx, 'Pronunciation'])
        if curr_pron and curr_pron != 'nan' and curr_pron.strip() != '':
            continue

        print(f"[{i}/{total_len}] 处理中: {batch_slice.iloc[0]['Word']} ...")

        # 调用 DeepSeek
        items = get_batch_info_deepseek(batch_slice)

        if items:
            success_count = 0
            for item in items:
                res_id = item.get('id')
                if res_id is not None:
                    try:
                        res_id = int(res_id)
                        if res_id in df_result.index:
                            df_result.at[res_id, 'Pronunciation'] = item.get('pronunciation', '')
                            df_result.at[res_id, 'Grammar'] = item.get('grammar', '')
                            df_result.at[res_id, 'Example'] = item.get('example', '')
                            success_count += 1
                    except:
                        pass
            print(f"  √ 成功写入 {success_count} 条数据")
        else:
            print("  x 本批次未获取到数据")

        # 实时保存
        df_result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        # DeepSeek 速率限制较宽松，不需要 sleep 很久，0.5秒即可
        time.sleep(0.5)

    print(f"\n全部完成！文件已保存至: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()