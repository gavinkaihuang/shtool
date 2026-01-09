import json
import argparse
from pathlib import Path

def convert_to_qwerty_format(input_file, output_file, name, description, author):
    # 读取原始词书
    with open(input_file, "r", encoding="utf-8") as f:
        raw_words = json.load(f)

    # Qwerty Learner 支持的格式
    qwerty_pack = {
        "name": name,
        "description": description,
        "author": author,
        "homepage": "",
        "words": []
    }

    # 转换单词格式
    for item in raw_words:
        word = item.get("word")
        trans = item.get("trans", [])

        # trans 要合并成单个字符串（Qwerty Learner 支持 string 或 array）
        trans_str = "；".join(trans) if isinstance(trans, list) else str(trans)

        qwerty_pack["words"].append({
            "word": word,
            "trans": trans_str
        })

    # 写入输出文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(qwerty_pack, f, ensure_ascii=False, indent=2)

    print(f"转换完成：{output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert vocab list to Qwerty Learner format")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("output", help="Output JSON file")
    parser.add_argument("--name", default="My Vocabulary", help="Word pack name")
    parser.add_argument("--description", default="Custom vocabulary pack", help="Description")
    parser.add_argument("--author", default="Gavin", help="Author name")

    args = parser.parse_args()

    convert_to_qwerty_format(
        args.input, args.output, args.name, args.description, args.author
    )
