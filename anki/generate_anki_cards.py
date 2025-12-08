import csv
import re
import random

# 简单助记规则库（可扩展）
MNEMONIC_RULES = {
    'ab': 'ab- 表示“离开、否定”，如 abandon（放弃）',
    'ad': 'ad- 表示“朝向”，常变为 a-, ac-, af- 等，如 accept（接受）',
    're': 're- 表示“再次”，如 review（复习）',
    'un': 'un- 表示“否定”，如 unhappy（不开心）',
    'pre': 'pre- 表示“在…之前”，如 preview（预览）',
    'trans': 'trans- 表示“跨越”，如 transport（运输）',
    'com/con': 'com-/con- 表示“共同”，如 connect（连接）',
    'bio': 'bio- 表示“生命”，如 biology（生物学）',
    'tele': 'tele- 表示“远”，如 telephone（电话）',
    'graph': '-graph 表示“写、记录”，如 photograph（照片）',
}

# 简单例句模板（按词性分类）
SENTENCE_TEMPLATES = {
    'n': [
        "The {word} is very important in daily life.",
        "She bought a new {word} yesterday.",
        "This {word} helps us understand the world better."
    ],
    'v': [
        "He always {word}s on weekends.",
        "They {word} together every morning.",
        "Don't {word} your time on useless things."
    ],
    'adj': [
        "It was a very {word} day.",
        "She felt {word} after the long journey.",
        "The movie was quite {word}."
    ],
    'adv': [
        "He spoke {word}.",
        "She finished her homework {word}.",
        "They worked {word} to meet the deadline."
    ]
}

def guess_pos(definition):
    """根据中文释义粗略判断词性"""
    if 'n.' in definition:
        return 'n'
    elif 'vt.' in definition or 'vi.' in definition:
        return 'v'
    elif 'adj.' in definition:
        return 'adj'
    elif 'adv.' in definition:
        return 'adv'
    else:
        return 'n'  # 默认名词

def generate_sentence(word, pos):
    templates = SENTENCE_TEMPLATES.get(pos, SENTENCE_TEMPLATES['n'])
    template = random.choice(templates)
    # 动词过去式简单处理（仅加-ed，不处理不规则）
    if pos == 'v':
        verb_form = word if 'every' in template or 'always' in template else word + 'ed'
        return template.format(word=verb_form)
    else:
        return template.format(word=word)

def generate_mnemonic(word):
    word_lower = word.lower()
    for prefix in ['ab', 'ad', 're', 'un', 'pre', 'trans', 'com', 'con', 'bio', 'tele']:
        if word_lower.startswith(prefix):
            key = prefix
            if prefix in ['com', 'con']:
                key = 'com/con'
            return MNEMONIC_RULES.get(key, f"词根提示：{prefix}- 开头")
    # 检查常见词根
    if 'graph' in word_lower:
        return MNEMONIC_RULES['graph']
    if 'bio' in word_lower:
        return MNEMONIC_RULES['bio']
    return "联想记忆：结合语境多读多用！"

def clean_definition(def_str):
    """清理释义，去掉词性标记，保留核心中文"""
    # 移除 vt. vi. n. adj. 等标记
    cleaned = re.sub(r'(?:^|\s)(?:[vn]\.?t?\.?|adj\.|adv\.|abbr\.|prep\.|conj\.|pron\.|int\.),?\s*', '', def_str)
    # 合并多个空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def main():
    input_file = 'input_vocab.csv'
    output_file = 'anki_gaokao_vocab.csv'

    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8', newline='') as f_out:

        # 读取原始CSV（假设无标题行，每行：word,"definition"）
        reader = csv.reader(f_in)
        writer = csv.writer(f_out, delimiter='|')

        # 写入标题行（Anki 可选）
        writer.writerow(['Word', 'Definition', 'Sentence', 'Mnemonic', 'Tag'])

        for row in reader:
            if not row:
                continue
            word = row[0].strip()
            raw_def = row[1].strip() if len(row) > 1 else ""

            definition = clean_definition(raw_def)
            pos = guess_pos(raw_def)
            sentence = generate_sentence(word, pos)
            mnemonic = generate_mnemonic(word)
            tag = "Gaokao-Core"  # 可根据词频或来源调整

            writer.writerow([word, definition, sentence, mnemonic, tag])

    print(f"✅ Anki 卡片已生成：{output_file}")
    print("📌 导入 Anki 时请选择分隔符：|")

if __name__ == '__main__':
    main()