"""Report generation"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape


def generate_html(results: List[Dict], output_path: str, keyword: str) -> str:
    """Generate HTML gallery report from results."""
    # Convert screenshot paths to relative (for portability)
    output_dir = Path(output_path)
    for result in results:
        for device in ('desktop', 'mobile'):
            path = result['screenshots'].get(device)
            if path:
                result['screenshots'][device] = os.path.relpath(path, str(output_dir))

    # Setup Jinja2
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('report.html')

    html = template.render(
        keyword=keyword,
        results=results,
        total_count=len(results),
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / 'report.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(html_path)


def generate_json(results: List[Dict], output_path: str, keyword: str) -> str:
    """Generate JSON report from results."""
    report = {
        'keyword': keyword,
        'generated_at': datetime.now().isoformat(),
        'total_results': len(results),
        'results': results
    }

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / 'results.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(json_path)


def format_result(url: str, screenshots: Dict[str, str]) -> Dict:
    """Format a single result for the report."""
    return {
        'url': url,
        'screenshots': screenshots,
    }
