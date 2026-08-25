#!/usr/bin/env python3
"""
Master generation script for GitHub Profile README.
Runs all generation scripts to create/update profile assets.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config


def main():
    """Run all generation scripts."""
    print("=" * 60)
    print("GitHub Profile README Generator")
    print("=" * 60)
    
    config = get_config()
    print(f"Profile: {config.name} (@{config.username})")
    print()
    
    # Track success/failure
    results = {}
    
    # 1. Generate whoami card
    print("1. Generating whoami card...")
    try:
        from make_whoami_svg import generate_whoami_svg
        path = generate_whoami_svg()
        results["whoami"] = True
        print(f"   [OK] Generated: {path}")
    except Exception as e:
        results["whoami"] = False
        print(f"   [ERROR] Error: {e}")
    
    # 2. Generate stack card
    print("2. Generating stack card...")
    try:
        from make_stack_svg import generate_stack_svg
        path = generate_stack_svg()
        results["stack"] = True
        print(f"   [OK] Generated: {path}")
    except Exception as e:
        results["stack"] = False
        print(f"   [ERROR] Error: {e}")
    
    # 3. Generate projects card
    print("3. Generating projects card...")
    try:
        from make_projects_svg import generate_projects_svg
        path = generate_projects_svg()
        results["projects"] = True
        print(f"   [OK] Generated: {path}")
    except Exception as e:
        results["projects"] = False
        print(f"   [ERROR] Error: {e}")
    
    # 4. Generate focus card
    print("4. Generating focus card...")
    try:
        from make_focus_svg import generate_focus_svg
        path = generate_focus_svg()
        results["focus"] = True
        print(f"   [OK] Generated: {path}")
    except Exception as e:
        results["focus"] = False
        print(f"   [ERROR] Error: {e}")
    
    # 5. ASCII portrait (only if source photo exists)
    print("5. Checking for source photo...")
    source_photo = Path(__file__).parent.parent / "source" / "source-photo.jpg"
    
    if source_photo.exists():
        print("   Source photo found. Generating ASCII portrait...")
        try:
            from prep_photo import prepare_photo
            from make_ascii_svg import generate_ascii_portrait
            
            # Prepare photo
            processed_path = prepare_photo(str(source_photo))
            
            # Generate ASCII SVGs
            animated, static = generate_ascii_portrait(processed_path)
            results["ascii"] = True
            print(f"   [OK] Generated: {animated}")
            print(f"   [OK] Generated: {static}")
        except Exception as e:
            results["ascii"] = False
            print(f"   [ERROR] Error: {e}")
    else:
        print("   No source photo found. Using placeholder.")
        print("   Place your photo at: source/source-photo.jpg")
        results["ascii"] = None  # Skipped
    
    # 6. Fetch contributions and generate heatmap
    print("6. Fetching contribution data...")
    try:
        from fetch_contributions import fetch_contributions, load_existing_data
        from render_heatmap_svg import generate_heatmap_svg, load_contribution_data
        
        json_path = Path(__file__).parent.parent / "data" / "contributions.json"
        
        # Try to fetch new data
        new_data = fetch_contributions(config.username, str(json_path))
        
        if new_data:
            # Generate heatmap from new data
            path = generate_heatmap_svg(new_data)
            results["heatmap"] = True
            print(f"   [OK] Generated: {path}")
        else:
            # Try to use existing data
            existing_data = load_existing_data(str(json_path))
            if existing_data:
                path = generate_heatmap_svg(existing_data)
                results["heatmap"] = True
                print(f"   [OK] Generated from existing data: {path}")
            else:
                results["heatmap"] = False
                print("   [ERROR] No contribution data available")
    except Exception as e:
        results["heatmap"] = False
        print(f"   [ERROR] Error: {e}")
    
    # Summary
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    for asset, status in results.items():
        if status is True:
            print(f"  [OK] {asset}")
        elif status is False:
            print(f"  [FAIL] {asset} (failed)")
        else:
            print(f"  [SKIP] {asset} (skipped)")
    
    print()
    print("Generation complete!")
    print()
    print("Next steps:")
    print("1. Review generated SVGs in assets/ directory")
    print("2. Open SVGs in browser to verify appearance")
    print("3. Push to GitHub and verify profile rendering")
    print("4. Set up GitHub Actions for automatic updates")


if __name__ == "__main__":
    main()