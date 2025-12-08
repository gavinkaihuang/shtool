import google.generativeai as genai
import pandas as pd
import time
import sys
import os
from google.api_core import exceptions

# ================= 配置区域 =================
try:
    import config
    API_KEY = config.API_KEY
except ImportError:
    print("❌ 错误：未找到 'config.py' 文件。")
    sys.exit(1)

INPUT_FILE = "及时雨高考英语词汇手册.csv"
OUTPUT_FILE = "anki_output_complete.csv"

# 批处理大小 (建议保持在 10，太大会增加超时风险)
BATCH_SIZE = 10 
# ===========================================

# 配置 Gemini
genai.configure(api_key=API_KEY)

# 【重要修改】改回 gemini-2.0-flash，它的配额通常比 2.5 宽松
model = genai.GenerativeModel('gemini-2.0-flash')

def get_anki_content_with_retry(words_list, max_retries=5):
    """
    带自动重试功能的 API 调用函数
    """
    words_str = ", ".join(words_list)
    
    prompt = f"""
    你是一个专业的英语词汇老师。请为以下单词生成 Anki 卡片内容：
    单词列表: {words_str}

    请严格按照 CSV 格式输出，不要包含表头，不要使用代码块标记，每一行包含以下字段：
    Word|IPA|Sentence|Mnemonic

    要求：
    1. Word: 单词本身
    2. IPA: 单词的音标（如 /hæk/）
    3. Sentence: 一个简短、地道的英文例句，并在括号内附带中文翻译。
    4. Mnemonic: 词根词缀解析或谐音助记。
    5. 分隔符: 请务必使用竖线 '|' 作为字段分隔符，不要使用逗号。
    6. 如果单词有多个释义，不要在输出中包含释义，只需处理我要求的字段。
    """

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except exceptions.ResourceExhausted:
            # 遇到 429 配额超限错误
            wait_time = 60 * (attempt + 1) # 第一次等60秒，第二次等120秒...
            print(f"\n⚠️ 配额已满 (429 Error)，脚本将暂停 {wait_time} 秒后自动重试 ({attempt + 1}/{max_retries})...")
            time.sleep(wait_time)
            continue
            
        except Exception as e:
            print(f"\n❌ 其他 API 错误: {e}")
            # 如果是其他严重错误，稍微等一下再试
            time.sleep(5)
            continue
    
    print("\n❌ 重试多次失败，跳过此批次。")
    return None

def process_csv():
    # 1. 读取文件
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 错误：找不到文件 '{INPUT_FILE}'")
        return

    # 智能读取：先尝试无表头，若失败则尝试有表头
    try:
        df = pd.read_csv(INPUT_FILE, header=None, names=['Word', 'Definition'], on_bad_lines='skip')
        # 简单检查：如果第一行看起来像表头（比如 Word 这一列的值就是 "Word"），则重新读取
        if df.iloc[0]['Word'] == 'Word' or df.iloc[0]['Word'] == '正面 (Word)':
             df = pd.read_csv(INPUT_FILE)
             # 统一列名
             if '正面 (Word)' in df.columns:
                 df.rename(columns={'正面 (Word)': 'Word', '背面释义 (Definition)': 'Definition'}, inplace=True)
    except Exception:
        df = pd.read_csv(INPUT_FILE)

    # 2. 检查是否已有部分进度 (断点续传功能)
    # 如果输出文件已存在，我们读取它，看看处理了多少个
    processed_words = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df_existing = pd.read_csv(OUTPUT_FILE)
            if '正面 (Word)' in df_existing.columns:
                processed_words = set(df_existing['正面 (Word)'].astype(str).tolist())
            print(f"📂 检测到已存在输出文件，包含 {len(processed_words)} 个单词。脚本将自动跳过已处理的单词。")
        except:
            pass

    # 数据清洗
    df['Word'] = df['Word'].astype(str).str.strip()
    df = df.dropna(subset=['Word'])
    df = df[df['Word'] != 'nan']
    
    # 过滤掉已经处理过的单词
    df_to_process = df[~df['Word'].isin(processed_words)].copy()
    
    all_words = df_to_process['Word'].unique().tolist()
    total_words = len(all_words)
    
    if total_words == 0:
        print("✅ 所有单词都已处理完毕！")
        return

    print(f"🚀 开始处理剩余的 {total_words} 个单词（模型: gemini-2.0-flash）...")

    # 准备结果容器
    results = []
    
    # 分批处理
    for i in range(0, total_words, BATCH_SIZE):
        batch_words = all_words[i : i + BATCH_SIZE]
        print(f"正在处理: {batch_words[0]} ... ({i+1}/{total_words})")
        
        # 调用 API (带重试)
        api_output = get_anki_content_with_retry(batch_words)
        
        current_batch_results = []
        if api_output:
            lines = api_output.split('\n')
            for line in lines:
                parts = line.split('|')
                if len(parts) >= 4:
                    current_batch_results.append({
                        'Word': parts[0].strip(),
                        'IPA': parts[1].strip(),
                        'Sentence': parts[2].strip(),
                        'Mnemonic': parts[3].strip()
                    })
        
        # === 实时保存 (关键修改) ===
        # 每处理完一批，就立即保存到文件，防止程序中断数据丢失
        if current_batch_results:
            df_batch_res = pd.DataFrame(current_batch_results)
            # 找到原始 Definition
            df_batch_merged = pd.merge(df[df['Word'].isin(batch_words)], df_batch_res, on='Word', how='inner')
            
            # 格式化
            def format_row(row):
                definition = str(row['Definition']).replace('\n', '<br>').replace('\r', '')
                ipa = str(row['IPA']) if pd.notna(row['IPA']) else ""
                if ipa and ipa not in definition:
                    definition = f"[{ipa}]<br>{definition}"
                return pd.Series({
                    '正面 (Word)': row['Word'],
                    '背面释义 (Definition)': definition,
                    '例句 (Sentence)': row['Sentence'],
                    '词根/助记 (Mnemonic)': row['Mnemonic'],
                    '难度标签 (Tag)': '高考英语词汇'
                })

            final_batch_output = df_batch_merged.apply(format_row, axis=1)
            
            # 追加写入模式 (Append Mode)
            # 如果是第一次写（且文件不存在），写表头；否则不写表头
            header_needed = not os.path.exists(OUTPUT_FILE)
            final_batch_output.to_csv(OUTPUT_FILE, mode='a', index=False, header=header_needed)
            
        # 稍微休眠一下，给 API 喘息时间
        time.sleep(2) 

    print(f"\n✅ 全部完成！文件已更新至: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_csv()