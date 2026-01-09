import csv
import json
import re

# 文件名（请确保和你的附件文件名完全一致，如果不同请修改）
csv_filename = "及时雨高考英语词汇手册.csv"
output_json = "timely_rain_vocab.json"

data = []

# 常见的词性标记，用于智能拆分
pos_pattern = r'(?=\b(?:n\.|vt\.|vi\.|adj\.|adv\.|prep\.|conj\.|pron\.|abbr\.|int\.|num\.|art\.|aux\.|v\.|abbr\.)\s)'

with open(csv_filename, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) < 2:
            continue
        word = row[0].strip()
        meaning = row[1].strip()
        
        if not word or not meaning:
            continue
        
        # 按词性拆分释义
        parts = re.split(pos_pattern, meaning)
        trans = []
        for part in parts:
            part = part.strip()
            if part:
                # 清理多余空格
                part = re.sub(r'\s+', ' ', part)
                trans.append(part)
        
        # 如果没拆开，就整个放进去
        if not trans:
            trans = [meaning]
        
        entry = {
            "word": word.lower(),  # qwerty-learner 通常小写
            "trans": trans
        }
        data.append(entry)

# 保存为 JSON（美化格式，方便查看）
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"转换完成！共处理 {len(data)} 个词汇")
print(f"已生成文件：{output_json}")
print("现在你可以打开 qwerty-learner → 词书 → 导入词书 → 选择这个 JSON 文件导入即可。")