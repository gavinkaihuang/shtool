#!/usr/bin/env python3
import json
import os
from pathlib import Path


CHAPTERS_FILE = Path("chapters.json")
CONTENT_DIR = Path("content")
OUTPUT_DIR = Path(".")
BOOK_TITLE = "五仙门"
CHAPTERS_PER_VOLUME = 500


def load_chapters() -> list[dict[str, str]]:
    """读取章节索引文件。"""
    if not CHAPTERS_FILE.exists():
        raise FileNotFoundError(f"未找到 {CHAPTERS_FILE}，请先运行 list_spider.py")

    return json.loads(CHAPTERS_FILE.read_text(encoding="utf-8"))


def extract_chapter_number(title: str) -> int | None:
    """从中文标题中提取章节数值编号。返回 None 如果无法提取。"""
    import re
    match = re.search(r'第(.+?)章', title)
    if not match:
        return None
    
    num_str = match.group(1).strip()
    
    # 中文数字转换映射
    cn_to_num = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000, '万': 10000
    }
    
    # 尝试转换中文数字
    try:
        total = 0
        current = 0
        for char in num_str:
            if char in cn_to_num:
                val = cn_to_num[char]
                if val >= 10:
                    if val == 100 or val == 1000:
                        current *= val
                    else:
                        current = current * val if current else val
                    total += current
                    current = 0
                else:
                    current += val
            elif char == '（' or char == '(':
                # 遇到括号，返回目前的数字
                break
        total += current
        return total if total > 0 else None
    except:
        return None


def filter_and_sort_chapters(chapters: list[dict[str, str]]) -> list[dict[str, str]]:
    """过滤 success 状态的章节并按中文编号排序。"""
    success_chapters = [ch for ch in chapters if ch.get("status") == "success"]

    if not success_chapters:
        raise ValueError("未找到任何 success 状态的章节")

    # 按中文编号排序（如果无法提取则用 id 作为备选）
    def sort_key(ch):
        num = extract_chapter_number(ch["title"])
        return (num, int(ch["id"])) if num is not None else (999999, int(ch["id"]))
    
    success_chapters.sort(key=sort_key)

    return success_chapters


def read_chapter_content(chapter_id: str) -> str | None:
    """读取章节文件内容。如果文件不存在返回 None。"""
    content_file = CONTENT_DIR / f"{chapter_id}.txt"

    if not content_file.exists():
        return None

    return content_file.read_text(encoding="utf-8")


def bind_volume(
    chapters: list[dict[str, str]], volume_number: int
) -> tuple[int, int, int]:
    """
    合并单一分册。

    返回 (volume_number, start_id, end_id, success_count)
    """
    start_index = (volume_number - 1) * CHAPTERS_PER_VOLUME
    end_index = min(start_index + CHAPTERS_PER_VOLUME, len(chapters))

    volume_chapters = chapters[start_index:end_index]
    output_path = OUTPUT_DIR / f"{BOOK_TITLE}_第{volume_number}册.txt"

    success_count = 0
    lines: list[str] = []

    for chapter in volume_chapters:
        chapter_id = chapter["id"]
        title = chapter["title"]

        # 尝试读取章节内容
        content = read_chapter_content(chapter_id)
        if content is None:
            print(f"警告: 章节 {chapter_id} ({title}) 的内容文件丢失，已跳过")
            continue

        # 写入标题和正文
        lines.append(title)
        lines.append(content.rstrip())
        lines.append("")  # 章节间空行

        success_count += 1

    # 写入输出文件
    output_path.write_text("\n".join(lines), encoding="utf-8")

    # 获取实际包含的章节范围
    first_chapter = volume_chapters[0]
    last_chapter = volume_chapters[-1]

    return (
        volume_number,
        int(first_chapter["id"]),
        int(last_chapter["id"]),
        success_count,
    )


def main() -> None:
    # 加载并过滤章节
    print("读取章节索引...")
    chapters = load_chapters()
    success_chapters = filter_and_sort_chapters(chapters)

    if not success_chapters:
        print("没有需要合并的章节。")
        return

    total_chapters = len(success_chapters)
    total_volumes = (total_chapters + CHAPTERS_PER_VOLUME - 1) // CHAPTERS_PER_VOLUME

    print(f"总章节数: {total_chapters}，计划分为 {total_volumes} 册")
    print()

    # 分册合并
    for volume_num in range(1, total_volumes + 1):
        try:
            vol_num, start_id, end_id, success_cnt = bind_volume(
                success_chapters, volume_num
            )
            print(
                f"✓ 第 {vol_num} 册: 章节 {start_id:03d} ~ {end_id:03d} ({success_cnt} 章)"
            )
        except Exception as exc:
            print(f"✗ 第 {volume_num} 册合并失败: {exc}")

    print()
    print("所有分册合并完成！")


if __name__ == "__main__":
    main()
