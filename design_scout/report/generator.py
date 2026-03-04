"""Report generation"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def generate_html(results: List[Dict], output_path: str, keyword: str) -> str:
    """Generate HTML report from results.
    
    Args:
        results: List of result dicts with url, screenshots, score, comment, breakdown
        output_path: Path to save HTML file
        keyword: Search keyword used
        
    Returns:
        Path to generated HTML file
    """
    # Sort by score descending
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    
    # Setup Jinja2
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    template = env.get_template('report.html')
    
    # Render
    html = template.render(
        keyword=keyword,
        results=sorted_results,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # Write to file
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    html_path = output / 'report.html' if output.is_dir() else output
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return str(html_path)


def generate_json(results: List[Dict], output_path: str, keyword: str) -> str:
    """Generate JSON report from results.
    
    Args:
        results: List of result dicts
        output_path: Path to save JSON file
        keyword: Search keyword used
        
    Returns:
        Path to generated JSON file
    """
    # Sort by score descending
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    
    report = {
        'keyword': keyword,
        'generated_at': datetime.now().isoformat(),
        'total_results': len(sorted_results),
        'results': sorted_results
    }
    
    # Write to file
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    json_path = output / 'results.json' if output.is_dir() else output
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return str(json_path)


def format_result(
    url: str,
    screenshots: Dict[str, str],
    evaluation: Dict[str, Any]
) -> Dict:
    """Format a single result for the report.
    
    Args:
        url: Website URL
        screenshots: Dict with desktop and mobile screenshot paths
        evaluation: AI evaluation result
        
    Returns:
        Formatted result dict
    """
    return {
        'url': url,
        'screenshots': screenshots,
        'score': evaluation.get('total_score', 0) if evaluation else 0,
        'comment': evaluation.get('comment', '') if evaluation else '',
        'breakdown': {
            'visual_appeal': evaluation.get('visual_appeal', 0),
            'layout': evaluation.get('layout', 0),
            'modernity': evaluation.get('modernity', 0),
            'professionalism': evaluation.get('professionalism', 0),
        } if evaluation else None
    }
