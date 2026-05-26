#!/usr/bin/env python3
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag


CHAPTERS_FILE = Path("chapters.json")
CONTENT_DIR = Path("content")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )
}
AD_KEYWORDS = [
    "最新网址",
    "手机用户请浏览",
    "请收藏本站",
    "广告",
    "宙斯小说网",
    "版权",
]
STOP_KEYWORDS = ["推荐小说", "上一章", "下一章", "五仙门目录", "版权快捷申诉"]
META_KEYWORDS = ["更新时间", "作者:", "分类:", "当前位置:"]


def load_chapters() -> list[dict[str, str]]:
    """读取章节清单。"""
    if not CHAPTERS_FILE.exists():
        raise FileNotFoundError("未找到 chapters.json，请先运行 list_spider.py")

    return json.loads(CHAPTERS_FILE.read_text(encoding="utf-8"))


def save_chapters(chapters: list[dict[str, str]]) -> None:
    """每处理一章立即保存，便于断点续抓。"""
    CHAPTERS_FILE.write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def fetch_html(url: str) -> str:
    """请求章节正文页 HTML。"""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def is_body_container(tag: Tag) -> bool:
    """根据站点样式特征识别正文容器。"""
    if tag.name != "div":
        return False

    style = (tag.get("style") or "").replace(" ", "").lower()
    text = tag.get_text("\n", strip=True)
    link_count = len(tag.find_all("a"))

    return (
        ("fontsize:20px" in style or "width:740px" in style)
        and "line-height:30px" in style
        and len(text) > 100
        and link_count <= 2
        and not is_noise_text(text)
    )


def is_noise_text(text: str) -> bool:
    """识别元信息、导航和推荐等无关文本。"""
    return any(keyword in text for keyword in META_KEYWORDS + STOP_KEYWORDS)


def find_body_container(soup: BeautifulSoup) -> Tag | None:
    """优先按样式识别，失败时按文本密度回退。"""
    body_container = soup.find(is_body_container)
    if body_container is not None:
        return body_container

    candidates: list[tuple[int, Tag]] = []
    for tag in soup.find_all(["div", "td"]):
        text = tag.get_text("\n", strip=True)
        if len(text) < 200:
            continue
        if is_noise_text(text):
            continue
        if len(tag.find_all("a")) > 2:
            continue
        candidates.append((len(text), tag))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def extract_from_heading(soup: BeautifulSoup) -> str:
    """兜底策略：以标题为锚点，顺序提取标题后的正文文本。"""
    heading = soup.find("h1")
    if heading is None:
        raise ValueError("页面中未找到章节标题")

    lines: list[str] = []
    seen_non_meta = False
    for text_node in heading.next_strings:
        line = re.sub(r"\s+", " ", text_node.replace("\xa0", " ")).strip()
        if not line:
            continue
        if any(keyword in line for keyword in STOP_KEYWORDS):
            break
        if any(keyword in line for keyword in META_KEYWORDS):
            continue
        if line == heading.get_text(strip=True):
            continue
        seen_non_meta = True
        lines.append(line)

    if not seen_non_meta:
        raise ValueError("未能从标题后提取到正文")

    return clean_text("\n".join(lines))


def clean_text(text: str) -> str:
    """清理多余广告和空白。"""
    lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip().replace("\xa0", " ")
        line = re.sub(r"\s+", " ", line)
        if not line:
            continue
        if any(keyword in line for keyword in AD_KEYWORDS):
            continue
        lines.append(line)

    if not lines:
        raise ValueError("正文清洗后为空")

    return "\n\n".join(lines)


def parse_content(html: str) -> str:
    """提取并清洗章节正文。"""
    soup = BeautifulSoup(html, "html.parser")

    for selector in ("#ad_1", "#ad_2", "#ad_3", "script", "style"):
        for node in soup.select(selector):
            node.decompose()

    body_container = find_body_container(soup)
    if body_container is not None:
        return clean_text(body_container.get_text("\n", strip=True))

    return extract_from_heading(soup)


def save_content(chapter_id: str, content: str) -> None:
    """保存章节到本地文本文件。"""
    CONTENT_DIR.mkdir(exist_ok=True)
    output_path = CONTENT_DIR / f"{chapter_id}.txt"
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    chapters = load_chapters()
    targets = [item for item in chapters if item.get("status") in {"pending", "error"}]

    if not targets:
        print("没有需要抓取的章节。")
        return

    for chapter in chapters:
        if chapter.get("status") not in {"pending", "error"}:
            continue

        try:
            html = fetch_html(chapter["url"])
            content = parse_content(html)
            save_content(chapter["id"], content)
            chapter["status"] = "success"
            print(f"抓取成功: {chapter['id']} {chapter['title']}")
        except Exception as exc:
            chapter["status"] = "error"
            print(f"抓取失败: {chapter['id']} {chapter['title']} -> {exc}")
        finally:
            save_chapters(chapters)


if __name__ == "__main__":
    main()