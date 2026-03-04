# Design Scout

全自動設計靈感搜集工具 — 輸入關鍵字，輸出 Top 5 設計截圖 + AI 評分

## Installation

```bash
pip install -e .
playwright install chromium
```

## Usage

```bash
design-scout "fintech dashboard"
design-scout "saas landing page" --count 10 --output ./results
```

## Features

- Multi-source search (Google, Awwwards, Dribbble)
- Dual screenshots (Desktop 1440px + Mobile 390px)
- AI scoring (0-100 with comments)
- HTML report output
