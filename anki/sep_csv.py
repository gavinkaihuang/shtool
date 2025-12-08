import pandas as pd
import os
import shutil
import re

# ================= 配置区 =================
# 输入的原始文件名 (请确保此文件在当前目录下)
INPUT_FILE = '及时雨高考英语词汇手册.csv'
# 输出目录
OUTPUT_DIR = 'output'
# 每个文件的单词数
CHUNK_SIZE = 30
# =========================================

def clean_and_format_data(input_file):
    """
    读取原始文件，清洗数据，并转换为 Anki 格式的 DataFrame
    """
    print(f"正在读取并处理原始文件: {input_file} ...")
    
    # 1. 读取原始 CSV，假设没有表头，强制命名为 Word 和 Definition
    # on_bad_lines='skip' 用于跳过可能存在的格式错误行
    df = pd.read_csv(input_file, header=None, names=['Word', 'Definition'], on_bad_lines='skip')

    # 2. 数据清洗
    # 确保是字符串并去空格
    df['Word'] = df['Word'].astype(str).str.strip()
    
    # 将空白字符串替换为 NaN，以便填充
    df['Word'] = df['Word'].replace(r'^\s*$', float('nan'), regex=True)
    
    # 填充缺失的单词（向下填充，处理多行释义的情况）
    df['Word'] = df['Word'].ffill()
    
    # 删除依然没有单词的行（通常是文件开头的空行）
    df = df.dropna(subset=['Word'])

    # 3. 合并释义
    # 按单词分组，将多行释义合并，用 " \n " 分隔
    df_anki = df.groupby('Word', sort=False)['Definition'].apply(
        lambda x: ' \n '.join(x.astype(str).str.strip())
    ).reset_index()

    # 4. 清理释义中的 NaN 文本
    df_anki['Definition'] = df_anki['Definition'].str.strip()
    df_anki['Definition'] = df_anki['Definition'].replace(r'^\s*nan\s*$', '待补充释义', regex=True)
    
    # 再次过滤掉空单词（以防万一）
    df_anki = df_anki[df_anki['Word'] != '']
    df_anki = df_anki[df_anki['Word'] != 'nan']

    # 5. 添加 Anki 所需的其他字段
    df_anki['Sentence'] = '待补充'
    df_anki['Mnemonic'] = '待补充'
    df_anki['Tag'] = '高考英语词汇'

    # 6. 重命名列以匹配拆分逻辑
    df_anki.columns = ['正面 (Word)', '背面释义 (Definition)', '例句 (Sentence)', '词根/助记 (Mnemonic)', '难度标签 (Tag)']
    
    print(f"预处理完成，有效单词数: {len(df_anki)}")
    return df_anki

def split_csv(df):
    """
    将 DataFrame 拆分并保存到 output 目录
    """
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    num_chunks = (len(df) // CHUNK_SIZE) + (1 if len(df) % CHUNK_SIZE != 0 else 0)
    print(f"开始拆分，将生成 {num_chunks} 个文件到 '{OUTPUT_DIR}' 目录...")

    for i in range(num_chunks):
        start_idx = i * CHUNK_SIZE
        end_idx = start_idx + CHUNK_SIZE
        chunk = df.iloc[start_idx:end_idx]
        
        if chunk.empty:
            continue
            
        # 获取首尾单词作为文件名的一部分
        first_word = str(chunk.iloc[0]['正面 (Word)'])
        last_word = str(chunk.iloc[-1]['正面 (Word)'])
        
        # 提取首字母 (过滤非法字符)
        f_initial = ''.join(filter(str.isalnum, first_word[0])) if first_word else 'X'
        l_initial = ''.join(filter(str.isalnum, last_word[0])) if last_word else 'X'
        
        # 生成文件名: batch_001_A_B.csv
        filename = f"batch_{i+1:03d}_{f_initial.upper()}_{l_initial.upper()}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        chunk.to_csv(filepath, index=False)
        
    print("所有文件拆分完毕！")

# ================= 主程序 =================
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"错误: 找不到文件 '{INPUT_FILE}'，请确认文件名正确。")
    else:
        try:
            # 1. 先清洗数据
            processed_df = clean_and_format_data(INPUT_FILE)
            # 2. 再拆分数据
            split_csv(processed_df)
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()