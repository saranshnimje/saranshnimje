#!/usr/bin/env python3
"""
Generate contribution heatmap SVG from contribution data.
Creates an animated GitHub-style contribution calendar.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_contribution_data(json_path: str) -> dict:
    """Load contribution data from JSON file."""
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Contribution data not found: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_heatmap_svg(
    data: dict,
    output_path: str = None,
    weeks: int = 52
) -> str:
    """
    Generate contribution heatmap SVG.
    
    Args:
        data: Contribution data dictionary
        output_path: Path to save SVG (optional)
        weeks: Number of weeks to display (default: 52)
    
    Returns:
        Path to generated SVG
    """
    if output_path is None:
        output_path = Path(__file__).parent.parent / "assets" / "contribution" / "heatmap.svg"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # GitHub contribution colors
    colors = {
        0: "#161b22",  # No contributions
        1: "#0e4429",  # Low
        2: "#006d32",  # Moderate
        3: "#26a641",  # High
        4: "#39d353",  # Very high
    }
    
    # Create a dictionary for quick lookup
    days_dict = {day["date"]: day for day in data.get("days", [])}
    
    # Calculate date range (end at today, go back `weeks` weeks)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(weeks=weeks, days=end_date.weekday())
    
    # Generate calendar grid
    calendar_days = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        day_data = days_dict.get(date_str, {"count": 0, "level": 0})
        
        calendar_days.append({
            "date": date_str,
            "count": day_data["count"],
            "level": day_data["level"],
            "weekday": current_date.weekday(),
            "week": (current_date - start_date).days // 7
        })
        
        current_date += timedelta(days=1)
    
    # Calculate dimensions
    cell_size = 12
    cell_gap = 3
    padding_left = 40
    padding_top = 40
    padding_right = 20
    padding_bottom = 80
    
    # Calculate actual number of weeks needed
    max_week = max(day["week"] for day in calendar_days) if calendar_days else 0
    actual_weeks = max_week + 1
    
    svg_width = padding_left + actual_weeks * (cell_size + cell_gap) + padding_right
    svg_height = padding_top + 7 * (cell_size + cell_gap) + padding_bottom
    
    # Month labels
    month_labels = []
    current_month = -1
    
    for day in calendar_days:
        month = datetime.strptime(day["date"], "%Y-%m-%d").month
        if month != current_month:
            current_month = month
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_labels.append({
                "name": month_names[month - 1],
                "week": day["week"]
            })
    
    # Weekday labels
    weekday_labels = ["Mon", "Wed", "Fri"]
    
    # Build SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
  <title>Contribution activity for {data.get("username", "GitHub user")}</title>
  <desc>GitHub-style contribution heatmap showing daily activity over the past year</desc>
  
  <!-- Background -->
  <rect width="{svg_width}" height="{svg_height}" fill="#0d1117"/>
  
  <!-- Header -->
  <g font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="12">
    <text x="{padding_left}" y="20" fill="#f0f6fc" font-size="14">CONTRIBUTIONS</text>
    <text x="{padding_left}" y="32" fill="#8b949e" font-size="10">{data.get("total_contributions", 0)} contributions in the last year</text>
  </g>
  
  <!-- Calendar -->
  <g transform="translate({padding_left}, {padding_top})">
'''
    
    # Add month labels
    for label in month_labels:
        x = label["week"] * (cell_size + cell_gap)
        svg_content += f'    <text x="{x}" y="-5" fill="#8b949e" font-family="monospace" font-size="10">{label["name"]}</text>\n'
    
    # Add weekday labels
    for i, label in enumerate(weekday_labels):
        y = i * 2 * (cell_size + cell_gap) + cell_size
        svg_content += f'    <text x="-30" y="{y}" fill="#8b949e" font-family="monospace" font-size="10" text-anchor="end">{label}</text>\n'
    
    # Add contribution cells with animation
    for day in calendar_days:
        x = day["week"] * (cell_size + cell_gap)
        y = day["weekday"] * (cell_size + cell_gap)
        
        # Determine color based on contribution level
        level = min(day["level"], 4)
        fill_color = colors[level]
        
        # Calculate animation delay based on position (diagonal reveal)
        delay = (day["week"] + day["weekday"]) * 0.01
        
        # Escape date for XML
        date_escaped = day["date"].replace("&", "&amp;")
        
        svg_content += f'''    <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{fill_color}" opacity="0">
      <title>{day["count"]} contributions on {date_escaped}</title>
      <animate attributeName="opacity" from="0" to="1" dur="0.2s" begin="{delay:.3f}s" fill="freeze"/>
    </rect>
'''
    
    svg_content += '''  </g>
  
  <!-- Legend -->
  <g transform="translate(''' + str(svg_width - 150) + ''', ''' + str(svg_height - 40) + ''')">
    <text x="0" y="0" fill="#8b949e" font-family="monospace" font-size="10">Less</text>
'''
    
    # Legend cells
    for i in range(5):
        x = 35 + i * (cell_size + cell_gap)
        svg_content += f'    <rect x="{x}" y="-10" width="{cell_size}" height="{cell_size}" rx="2" fill="{colors[i]}"/>\n'
    
    svg_content += f'''    <text x="{35 + 5 * (cell_size + cell_gap) + 5}" y="0" fill="#8b949e" font-family="monospace" font-size="10">More</text>
  </g>
  
  <!-- Stats -->
  <g transform="translate({padding_left}, {svg_height - 25})" font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="10" fill="#8b949e">
    <text x="0" y="0">Current streak: {data.get("current_streak", 0)} days</text>
    <text x="180" y="0">Longest streak: {data.get("longest_streak", 0)} days</text>
    <text x="360" y="0">Best day: {data.get("best_day", {}).get("date", "N/A")} ({data.get("best_day", {}).get("count", 0)})</text>
  </g>
</svg>'''
    
    # Write SVG file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_heatmap_svg.py <contributions.json> [output.svg]")
        print("  contributions.json: Path to contribution data")
        print("  output.svg: Path to save SVG (default: assets/contribution/heatmap.svg)")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Load data
    contribution_data = load_contribution_data(json_file)
    
    # Generate SVG
    result = generate_heatmap_svg(contribution_data, output_file)
    print(f"Generated: {result}")