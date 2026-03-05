# 🎨 Design Scout

競品 Landing Page 研究工具 — 輸入關鍵字，輸出 Top 設計截圖 + AI 評分

## Features

- **Multi-source Search**: 聚焦競品 landing page 研究
  - DuckDuckGo (25) — 主要搜尋來源
  - Product Hunt (15) — 熱門產品與新創
  - Landingfolio (10) — 精選 landing pages
  - Lapa.ninja (10) — Landing page gallery
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

1. **搜尋**: 從 4 個來源搜尋關鍵字相關的網站（共 60 URLs）
2. **去重**: 移除重複 domain，標準化 URLs
3. **截圖**: 用 Playwright 截取桌面版和手機版截圖
4. **評分**: 用 AI Vision 模型評分（視覺、佈局、現代感、專業度）
5. **報告**: 生成 HTML 報告和 JSON 資料

### 搜尋來源配置

聚焦**競品 landing page 研究**，選擇高品質的真實網站來源：

| 來源 | 數量 | 說明 |
|------|------|------|
| **DuckDuckGo** | 25 | 主要搜尋引擎，廣泛覆蓋 |
| **Product Hunt** | 15 | 熱門新創產品，趨勢指標 |
| **Landingfolio** | 10 | 按行業分類的 landing pages |
| **Lapa.ninja** | 10 | 精選 landing page gallery |

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
  "generated_at": "2026-03-05T12:00:00",
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

### 2026-03-05 (v2)
- 🎯 聚焦競品 landing page 研究
- ✨ 新增 Product Hunt 來源
- ⬆️ DuckDuckGo 提權至 25 URLs
- 🗑️ 移除 Awwwards, SiteInspire, OnePageLove

### 2026-03-05 (v1)
- ✨ 新增 Lapa.ninja, Landingfolio, OnePageLove
- ✨ 新增 DuckDuckGo 搜尋

### 2026-03-04
- 🎉 Initial release

## License

MIT
