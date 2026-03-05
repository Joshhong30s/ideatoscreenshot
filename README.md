# 🎨 Design Scout

全自動設計靈感搜集工具 — 輸入關鍵字，輸出 Top 設計截圖 + AI 評分

## Features

- **Multi-source Search**: 搜尋真實營運網站（非設計 mockup）
  - DuckDuckGo 網頁搜尋
  - Awwwards 得獎網站
  - SiteInspire 精選設計
  - Lapa.ninja Landing Pages
  - Landingfolio Landing Pages
  - OnePageLove 單頁網站
- **Dual Screenshots**: Desktop (1440px) + Mobile (390px) with Retina support
- **AI Scoring**: GPT-4o or Claude Vision rates designs 0-100
- **Beautiful Reports**: HTML gallery + JSON data

## Installation

```bash
# Clone the repo
git clone https://github.com/Joshhong30s/ideatoscreenshot.git design-scout
cd design-scout

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

## Usage

### Basic Usage

```bash
# Search and generate report
design-scout "fintech dashboard"

# More results
design-scout "saas landing page" --count 10

# Custom output directory
design-scout "portfolio website" --output ./my-results

# Skip AI scoring (faster, no API key needed)
design-scout "e-commerce design" --no-score
```

### API Keys (for AI Scoring)

Set one of these environment variables:

```bash
# OpenAI (GPT-4o Vision)
export OPENAI_API_KEY="sk-..."

# Or Anthropic (Claude Vision)
export ANTHROPIC_API_KEY="sk-ant-..."
```

Without an API key, scoring will use mock values.

## How It Works

1. **搜尋**: 同時從 6 個來源搜尋關鍵字相關的網站
2. **去重**: 移除重複 domain，標準化 URLs
3. **截圖**: 用 Playwright 截取桌面版和手機版截圖
4. **評分**: 用 AI Vision 模型評分（視覺、佈局、現代感、專業度）
5. **報告**: 生成 HTML 報告和 JSON 資料

### 為什麼這些來源？

我們選擇展示**真實營運網站**的 gallery，而非設計 mockup 作品集：

| 來源 | 類型 | 優點 |
|------|------|------|
| **Awwwards** | 得獎網站 | 最高品質，真實上線網站 |
| **SiteInspire** | 精選設計 | 人工策展，品質穩定 |
| **Lapa.ninja** | Landing Pages | 專注 landing page，分類清楚 |
| **Landingfolio** | Landing Pages | 按行業分類，參考價值高 |
| **OnePageLove** | 單頁網站 | 單頁設計專家 |
| **DuckDuckGo** | 通用搜尋 | 補充長尾結果 |

## Output

```
output/
├── report.html          # Visual gallery report
├── results.json         # Structured data
└── screenshots/
    ├── site_com_desktop.png
    └── site_com_mobile.png
```

### HTML Report

- Ranked by score (gold/silver/bronze)
- Desktop + mobile screenshots
- Score breakdown (Visual, Layout, Modern, Pro)
- AI-generated comments

### JSON Output

```json
{
  "keyword": "fintech dashboard",
  "generated_at": "2026-03-05T10:00:00",
  "total_results": 5,
  "results": [
    {
      "url": "https://example.com",
      "score": 85,
      "comment": "Clean, modern dashboard with excellent data visualization",
      "breakdown": {
        "visual_appeal": 22,
        "layout": 21,
        "modernity": 22,
        "professionalism": 20
      },
      "screenshots": {
        "desktop": "screenshots/example_com_desktop.png",
        "mobile": "screenshots/example_com_mobile.png"
      }
    }
  ]
}
```

## Scoring Criteria

| Criterion | Max Points | Description |
|-----------|------------|-------------|
| Visual Appeal | 25 | Color harmony, typography, imagery |
| Layout | 25 | Grid usage, spacing, visual hierarchy |
| Modernity | 25 | Contemporary trends, fresh look |
| Professionalism | 25 | Polish, attention to detail |

## Tech Stack

- **Python 3.11+**
- **Click** - CLI framework
- **Playwright** - Browser automation
- **httpx** - Async HTTP client
- **Jinja2** - HTML templating
- **OpenAI/Anthropic** - Vision AI scoring

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black design_scout/
```

## Changelog

### 2026-03-05
- ✨ 新增 Lapa.ninja, Landingfolio, OnePageLove 來源
- ✨ 新增 DuckDuckGo 搜尋（取代 Google）
- 🗑️ 移除 mockup 作品集來源，改用真實營運網站

### 2026-03-04
- 🎉 Initial release

## License

MIT
