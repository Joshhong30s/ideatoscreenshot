# Design Scout

競品 Landing Page 研究工具 — 輸入關鍵字，輸出截圖牆，手動策展

## Features

- **Multi-source Search**: 從 4 個來源蒐集競品 landing page
  - DuckDuckGo (25) — 主要搜尋來源
  - Product Hunt (15) — 熱門產品與新創
  - Landingfolio (10) — 精選 landing pages
  - Lapa.ninja (10) — Landing page gallery
- **Dual Screenshots**: Desktop (1440px) + Mobile (390px) with Retina support
- **Civitai-style Gallery**: 瀑布流圖牆，一目了然
- **Manual Curation**: 標星收藏、筆記、篩選、匯出精選集

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

```bash
# Search and generate report
design-scout "fintech dashboard"

# More results
design-scout "saas landing page" --count 30

# Custom output directory
design-scout "portfolio website" --output ./my-results
```

## How It Works

1. **搜尋**: 從 4 個來源搜尋關鍵字相關的網站（共 60 URLs）
2. **去重**: 移除重複 domain，標準化 URLs
3. **截圖**: 用 Playwright 截取桌面版和手機版截圖
4. **報告**: 生成 Civitai 風格的瀑布流圖牆

## Gallery Report

打開 `output/report.html`，你會看到：

- **瀑布流圖牆** — 所有截圖一目了然
- **Hover 預覽** — 滑鼠移上去顯示網址
- **點擊放大** — 桌面版 + 手機版並排比較
- **標星收藏** — 喜歡的設計點星星標記（存在瀏覽器 localStorage）
- **筆記功能** — 在 lightbox 裡寫下你的觀察
- **鍵盤導航** — 左右箭頭切換，Esc 關閉，S 標星
- **篩選模式** — 只看標星的項目
- **匯出精選** — 把你標記的匯出成 HTML 或 JSON

## Output

```
output/
├── report.html          # Civitai-style gallery report
├── results.json         # Structured data
└── screenshots/
    ├── site_com_desktop.png
    └── site_com_mobile.png
```

## Tech Stack

- **Python 3.11+**
- **Click** - CLI framework
- **Playwright** - Browser automation
- **httpx** - Async HTTP client
- **Jinja2** - HTML templating

## License

MIT
