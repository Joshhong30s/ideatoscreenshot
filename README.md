# 🎨 Design Scout

全自動設計靈感搜集工具 — 輸入關鍵字，輸出 Top 設計截圖 + AI 評分

## Features

- **Multi-source Search**: Google + Awwwards
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
  "generated_at": "2026-03-04T23:00:00",
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

## License

MIT
