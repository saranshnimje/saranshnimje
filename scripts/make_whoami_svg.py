#!/usr/bin/env python3
"""
Generate whoami.svg card for GitHub profile README.
Creates a terminal-style information card with fade-in animation.
"""

import sys
from pathlib import Path

# Add scripts directory to path for config import
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config


def generate_whoami_svg(output_path: str = None) -> str:
    """Generate whoami.svg based on profile configuration."""
    config = get_config()
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / "assets" / "cards" / "whoami.svg"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build the content lines
    lines = [
        f"{config.username}@github:~$ whoami",
        "",
        config.name,
        "─" * 30,
        "",
        "Role",
        f"→ {config.role}",
        "",
        "Focus",
    ]
    
    # Add focus items
    for item in config.focus:
        lines.append(f"→ {item}")
    
    lines.extend([
        "",
        "Currently building",
        f"→ {config.get_priority_project().get('name', 'N/A')}",
        "",
        "Status",
        "→ Learning",
        "→ Building",
        "→ Experimenting",
    ])
    
    # Calculate dimensions
    line_height = 24
    padding = 40
    max_line_length = max(len(line) for line in lines) if lines else 20
    
    # Calculate width based on character width (monospace font)
    char_width = 12
    width = max(max_line_length * char_width + padding * 2, 490)
    height = len(lines) * line_height + padding * 2
    
    # Generate SVG content
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <title>Whoami information card for {config.name}</title>
  <desc>Terminal-style card showing personal information and current focus areas</desc>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" rx="8" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  
  <!-- Terminal dots -->
  <circle cx="20" cy="20" r="6" fill="#ff5f56"/>
  <circle cx="40" cy="20" r="6" fill="#ffbd2e"/>
  <circle cx="60" cy="20" r="6" fill="#27c93f"/>
  
  <!-- Content -->
  <g font-family="'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace" font-size="14">
'''
    
    # Add each line with fade-in animation
    for i, line in enumerate(lines):
        y = padding + 30 + i * line_height
        
        # Escape XML special characters
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Determine text color
        if i == 0:  # Command line
            color = "#39d353"
        elif line.startswith("→"):
            color = "#c9d1d9"
        elif line in ["Role", "Focus", "Currently building", "Status"]:
            color = "#f0f6fc"
        elif line == config.name:
            color = "#f0f6fc"
        elif line.startswith("─"):
            color = "#30363d"
        else:
            color = "#8b949e"
        
        # Add animation delay based on line index
        delay = i * 0.05
        
        svg_content += f'''    <text x="{padding}" y="{y}" fill="{color}" opacity="0">
      <animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay:.2f}s" fill="freeze"/>
      {escaped_line}
    </text>
'''
    
    svg_content += '''  </g>
</svg>'''
    
    # Write the SVG file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return str(output_path)


if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    result = generate_whoami_svg(output_file)
    print(f"Generated: {result}")