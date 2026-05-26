#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.zhswx.com/chapter/64237.html"
OUTPUT_FILE = Path("chapters.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )
}


def fetch_html(url: str) -> str:
    """请求目录页 HTML。"""
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def parse_chapters(html: str, base_url: str) -> list[dict[str, str]]:
    """解析章节列表，生成标准 JSON 结构。"""
    soup = BeautifulSoup(html, "html.parser")
    chapters: list[dict[str, str]] = []

    seen_urls: set[str] = set()
    chapter_links = soup.select("td.chapterlist a[href]")

    for index, link in enumerate(chapter_links, start=1):
        title = link.get_text(strip=True)
        href = link.get("href", "").strip()
        full_url = urljoin(base_url, href)

        if not title or not href or full_url in seen_urls:
            continue

        seen_urls.add(full_url)
        chapters.append(
            {
                "id": f"{index:03d}",
                "title": title,
                "url": full_url,
                "status": "pending",
            }
        )

    if not chapters:
        raise ValueError("未解析到任何章节链接，请检查页面结构是否变化。")

    return chapters


def save_chapters(chapters: list[dict[str, str]]) -> None:
    """写入章节清单文件。"""
    OUTPUT_FILE.write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取小说目录并保存为 chapters.json")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="目录页 URL")
    args = parser.parse_args()

    try:
        html = fetch_html(args.url)
        chapters = parse_chapters(html, args.url)
        save_chapters(chapters)
        print(f"已保存 {len(chapters)} 个章节到 {OUTPUT_FILE}")
    except Exception as exc:
        print(f"目录抓取失败: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()