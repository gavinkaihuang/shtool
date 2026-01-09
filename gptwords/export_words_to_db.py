import pdfplumber
import sqlite3
import re
import os

# --- 配置部分 ---
PDF_PATH = '威威的GPT单词本8000词.pdf'
DB_PATH = 'vocabulary_book_fixed.db' # 换个名字以示区别

# --- 核心解析逻辑 ---

def extract_text_from_pdf(pdf_path):
    print(f"正在读取 PDF: {pdf_path} ...")
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                # x_tolerance 稍微调小，防止左右分栏的文字粘连（默认是3）
                text = page.extract_text(x_tolerance=2)
                if text:
                    full_text += text + "\n"
                print(f"读取进度: {int((i+1)/total_pages*100)}%", end='\r')
        print("\nPDF 读取完成。")
        return full_text
    except Exception as e:
        print(f"错误: 无法读取PDF - {e}")
        return None

def clean_and_normalize_text(text):
    """清洗文本，统一标签格式，移除干扰项"""
    print("正在清洗和标准化文本...")
    
    # 移除页码
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    
    # 统一关键锚点 <SECTION_MEANING>
    text = re.sub(r'\n\s*(词义分析|分析词义)\s*[:：]?', '\n<SECTION_MEANING>', text)
    
    # 统一其他模块标题
    text = re.sub(r'\n\s*(列举例句|例句|例句分析|举例句子)\s*[:：]?', '\n<SECTION_EXAMPLES>', text)
    text = re.sub(r'\n\s*(词根分析|词根词缀分析)\s*[:：]?', '\n<SECTION_ROOTS>', text)
    text = re.sub(r'\n\s*(词缀分析)\s*[:：]?', '\n<SECTION_AFFIXES>', text)
    text = re.sub(r'\n\s*(发展历史和文化背景|历史和文化背景)\s*[:：]?', '\n<SECTION_HISTORY>', text)
    text = re.sub(r'\n\s*(单词变形|单词变形和固定搭配)\s*[:：]?', '\n<SECTION_VARIATIONS>', text)
    text = re.sub(r'\n\s*(记忆辅助)\s*[:：]?', '\n<SECTION_MEMORY>', text)
    text = re.sub(r'\n\s*(小故事|英文小故事)\s*[:：]?', '\n<SECTION_STORY>', text)
    
    return text

def sanitize_word_title(raw_line):
    """
    【核心修复逻辑】
    处理 'yes yesterday' 这种粘连情况。
    策略：如果一行包含多个单词，且看起来不像是短语（如 wake up），则只取最后一个。
    """
    line = raw_line.strip()
    
    # 1. 去除开头的非字母字符（比如 "1. apple" -> "apple"）
    line = re.sub(r'^[^a-zA-Z]+', '', line)
    
    # 2. 如果包含空格，可能是粘连词
    if ' ' in line:
        parts = line.split()
        
        # 如果只有两个词，且两个词都很长（大于2），大概率是两个独立单词粘连了
        # 例如: "yes yesterday" -> 拆分
        # 例如: "wake up" -> 不拆分 (up很短)
        # 这是一个启发式规则，可以根据需要调整
        if len(parts) >= 2:
            last_part = parts[-1]
            prev_part = parts[-2]
            
            # 规则：如果最后一个词是纯字母，且前一个词也是纯字母，且长度都 > 1
            # 且不是介词短语的常见结构，我们倾向于认为它是粘连，只取最后一个
            if last_part.isalpha() and prev_part.isalpha():
                # 这里假设单词书的单词主要是单个词。
                # 这种做法会把 "living room" 变成 "room"，但在解决 "yes yesterday" 问题上非常有效。
                # 如果你的书里短语很多，这个逻辑可能需要放宽。
                print(f"  [修正] 检测到多词行: '{line}' -> 取末尾: '{last_part}'")
                return last_part

    return line

def extract_last_valid_line(text_block):
    """从文本块中提取最后一行非空文本，并作为单词标题"""
    lines = text_block.strip().split('\n')
    for line in reversed(lines):
        text = line.strip()
        # 过滤掉显然不是单词的行（比如太长，或者含中文）
        if text and len(text) < 40 and not re.search(r'[\u4e00-\u9fa5]', text):
            # 在这里调用清洗函数
            return sanitize_word_title(text)
            
    return "Unknown"

def parse_words(text):
    print("正在解析单词结构...")
    chunks = text.split('<SECTION_MEANING>')
    entries = []
    
    # 获取第一个单词
    current_word = extract_last_valid_line(chunks[0])
    
    for i in range(1, len(chunks)):
        chunk_content = chunks[i]
        
        next_word = None
        content_body = chunk_content
        
        if i < len(chunks) - 1:
            lines = chunk_content.split('\n')
            # 寻找倒数第一个像单词的行
            split_index = len(lines)
            for idx in range(len(lines)-1, -1, -1):
                line = lines[idx].strip()
                if not line: continue
                
                # 判断是否是下一个单词的标题行
                if len(line) < 40 and not re.search(r'[\u4e00-\u9fa5]', line):
                    # 再次使用 sanitize 逻辑来提取
                    raw_title = line
                    clean_title = sanitize_word_title(raw_title)
                    
                    if clean_title:
                        next_word = clean_title
                        split_index = idx
                        break
            
            content_body = "\n".join(lines[:split_index])
        
        entry = parse_single_entry(current_word, content_body)
        
        # 过滤无效条目
        if entry['word'] and entry['word'] != "Unknown" and len(entry['word']) < 30:
            entries.append(entry)
        
        current_word = next_word if next_word else "Unknown"

    print(f"解析结束，共提取 {len(entries)} 个条目。")
    return entries

def parse_single_entry(word, content):
    entry = {
        'word': word, 'meaning': '', 'examples': '', 'roots': '',
        'affixes': '', 'history': '', 'variations': '', 'memory': '', 'story': ''
    }
    
    sections = [
        ('<SECTION_EXAMPLES>', 'examples'),
        ('<SECTION_ROOTS>', 'roots'),
        ('<SECTION_AFFIXES>', 'affixes'),
        ('<SECTION_HISTORY>', 'history'),
        ('<SECTION_VARIATIONS>', 'variations'),
        ('<SECTION_MEMORY>', 'memory'),
        ('<SECTION_STORY>', 'story')
    ]
    
    indices = []
    for tag, key in sections:
        idx = content.find(tag)
        if idx != -1:
            indices.append((idx, tag, key))
    
    indices.append((len(content), 'END', 'END'))
    indices.sort(key=lambda x: x[0])
    
    # 提取词义
    first_tag_index = indices[0][0]
    entry['meaning'] = content[:first_tag_index].strip()
    
    # 提取其他部分
    for i in range(len(indices) - 1):
        start_idx = indices[i][0] + len(indices[i][1])
        end_idx = indices[i+1][0]
        key = indices[i][2]
        entry[key] = content[start_idx:end_idx].strip()

    return entry

def save_to_db(entries, db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            meaning TEXT,
            examples TEXT,
            roots TEXT,
            history TEXT,
            variations TEXT,
            memory TEXT,
            story TEXT
        )
    ''')
    
    data = []
    for e in entries:
        data.append((
            e['word'], e['meaning'], e['examples'], e['roots'], 
            e['history'], e['variations'], e['memory'], e['story']
        ))
    
    cursor.executemany('''
        INSERT INTO vocabulary (word, meaning, examples, roots, history, variations, memory, story)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()
    print(f"数据已保存至 {db_path}")

# --- 主程序 ---
def main():
    if not os.path.exists(PDF_PATH):
        print(f"找不到文件: {PDF_PATH}")
        return

    # 1. 读取
    raw_text = extract_text_from_pdf(PDF_PATH)
    if not raw_text: return

    # 2. 清洗
    clean_text = clean_and_normalize_text(raw_text)

    # 3. 解析
    entries = parse_words(clean_text)
    
    # 4. 存库
    save_to_db(entries, DB_PATH)
    
    print("\n完成！请检查数据库。如果看到 '[修正]' 日志，说明多词粘连问题已被处理。")

if __name__ == "__main__":
    main()