# 五仙门小说爬虫系统

一个完整的网络小说抓取、下载和分册合并系统。用于从 zhswx.com 自动抓取小说内容，生成分册电子书。

## 系统架构

```
list_spider.py  →  chapters.json
                        ↓
              content_spider.py  →  content/{id}.txt
                        ↓
                book_binder.py  →  五仙门_第1册.txt
                                   五仙门_第2册.txt
                                   ...
```

## 文件说明

### 1. list_spider.py - 目录解析脚本

**功能**：解析小说目录页面，提取所有章节的元数据。

**使用方法**：
```bash
python3 list_spider.py
```

**输出**：`chapters.json`
- 格式：JSON 数组，每个元素为一个章节
- 内容：
  ```json
  [
    {
      "id": "001",
      "title": "第一章 山村",
      "url": "https://zhswx.com/...",
      "status": "pending"
    },
    ...
  ]
  ```

**配置**：可在脚本中修改 `NOVEL_URL` 变量指向其他小说

---

### 2. content_spider.py - 内容下载脚本

**功能**：增量下载章节内容，支持断点续跑和错误恢复。

**使用方法**：
```bash
python3 content_spider.py
```

**工作流程**：
1. 读取 `chapters.json`
2. 过滤 `status="pending"` 或 `status="error"` 的章节
3. 逐章下载并提取正文
4. 将内容保存到 `content/{id}.txt`
5. 实时更新 `chapters.json` 中的 status（success/error）

**核心特性**：
- **多层解析策略**：
  1. 优先匹配样式特征（CSS 中包含 `line-height:30px`）
  2. 次选文本密度匹配（噪声少的区域）
  3. 最后手段：从标题标签后提取到推荐/导航区
  
- **自动清理**：
  - 移除广告标签（#ad_1, #ad_2, #ad_3）
  - 移除脚本和样式标签
  - 移除推荐小说、导航等噪声
  
- **错误处理**：
  - 单章失败不影响其他章节
  - 自动重试机制
  - 缺失内容文件可跳过

**配置**：可在脚本中修改以下参数
- `REQUEST_TIMEOUT`：请求超时时间
- `AD_KEYWORDS`：广告关键词列表（用于清理）
- `MAX_RETRIES`：重试次数

---

### 3. book_binder.py - 分册合并脚本

**功能**：将单章文件合并成分册电子书。

**使用方法**：
```bash
python3 book_binder.py
```

**工作流程**：
1. 读取 `chapters.json`
2. 过滤所有 `status="success"` 的章节
3. 按中文编号排序
4. 每 500 个中文编号为一册
5. 输出为 `五仙门_第N册.txt`

**输出文件格式**：
```
第一章 山村
[章节正文内容...]

第二章 远行
[章节正文内容...]

...
```

**特点**：
- 按中文编号（而非 ID）排序，确保顺序准确
- 自动处理缺失的章节文件（跳过并报警）
- 每章之间用空行分隔
- UTF-8 编码，完整支持中文

**配置**：可在脚本中修改以下参数
- `CHAPTERS_PER_VOLUME`：每册包含的章节数（默认 500）
- `BOOK_TITLE`：电子书书名

---

## 完整使用流程

### 第 1 步：解析目录
```bash
python3 list_spider.py
```
输出：`chapters.json`（包含 2883 个章节的元数据）

### 第 2 步：下载内容
```bash
python3 content_spider.py
```
输出：`content/` 目录下 2883 个 `{id}.txt` 文件

支持断点续跑：
```bash
# 可多次运行，自动跳过已完成的章节，重试失败的章节
python3 content_spider.py
```

### 第 3 步：合并分册
```bash
python3 book_binder.py
```
输出：`五仙门_第1册.txt` ~ `五仙门_第6册.txt`

---

## 进度检查

### 查看下载进度
```bash
python3 -c "
import json
chapters = json.load(open('chapters.json', encoding='utf-8'))
success = sum(1 for ch in chapters if ch.get('status') == 'success')
print(f'已完成: {success}/{len(chapters)}')
"
```

### 检查内容文件
```bash
ls -lh content/ | wc -l  # 查看已下载的文件数
```

### 查看分册统计
```bash
ls -lh 五仙门_第*.txt  # 查看所有分册文件大小
```

---

## 依赖安装

```bash
pip install requests beautifulsoup4
```

或通过 requirements.txt：
```bash
pip install -r requirements.txt
```

---

## 常见问题

**Q: 脚本如何处理网络错误？**  
A: 所有网络请求都有 try-except 包裹。单个章节失败会记录日志，继续处理下一个。可多次运行脚本重试。

**Q: 如何修改目标网站？**  
A: 修改 `list_spider.py` 和 `content_spider.py` 中的 URL 和 CSS 选择器，适配新网站的 HTML 结构。

**Q: 中间断开后如何续跑？**  
A: 直接运行脚本，会自动读取 `chapters.json` 中的状态，跳过已完成的章节。

**Q: 如何调整每册章节数？**  
A: 修改 `book_binder.py` 中的 `CHAPTERS_PER_VOLUME` 常量。

---

## 项目结构

```
crawbook/
├── list_spider.py          # 目录解析脚本
├── content_spider.py       # 内容下载脚本
├── book_binder.py          # 分册合并脚本
├── chapters.json           # 章节元数据（自动生成）
├── content/                # 单章文件目录（自动生成）
│   ├── 001.txt
│   ├── 002.txt
│   └── ...
├── 五仙门_第1册.txt       # 分册电子书（自动生成）
├── 五仙门_第2册.txt
└── ...
```

---

## 许可证

MIT License
