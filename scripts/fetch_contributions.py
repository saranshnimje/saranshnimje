#!/usr/bin/env python3
"""
Fetch GitHub contribution data from public profile.
Parses the contribution calendar HTML and saves to JSON.
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install requests beautifulsoup4")
    sys.exit(1)


def fetch_contributions(username: str, output_path: str = None) -> dict:
    """
    Fetch contribution data from GitHub public profile.
    
    Args:
        username: GitHub username
        output_path: Path to save JSON (optional)
    
    Returns:
        Dictionary with contribution data
    """
    url = f"https://github.com/users/{username}/contributions"
    
    print(f"Fetching contributions from: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch contributions: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all contribution day elements
    day_elements = soup.select("td.ContributionCalendar-day")
    
    if not day_elements:
        print("WARNING: Could not find contribution calendar elements with primary selector.")
        print("Trying alternative selectors...")
        
        # Try alternative selectors
        day_elements = soup.select("td[data-date]")
        
        if not day_elements:
            print("ERROR: Could not find contribution calendar elements.")
            print("GitHub may have changed their HTML structure.")
            return None
    
    days = []
    total_contributions = 0
    best_day = {"date": "", "count": 0}
    
    for day_elem in day_elements:
        # Get date
        date_str = day_elem.get("data-date", "")
        if not date_str:
            continue
        
        # Get contribution count from aria-label or tooltip
        aria_label = day_elem.get("aria-label", "")
        count = 0
        
        if aria_label:
            # Parse "X contributions on Month Day, Year"
            # or "No contributions on Month Day, Year"
            try:
                parts = aria_label.split()
                if parts and parts[0].isdigit():
                    count = int(parts[0])
            except (ValueError, IndexError):
                count = 0
        
        # Get level from CSS class
        level = 0
        classes = day_elem.get("class", [])
        for cls in classes:
            # Match patterns like "ContributionCalendar-day-3" or "level-3"
            match = re.search(r'(?:level|ContributionCalendar-day)-(\d)', cls)
            if match:
                level = int(match.group(1))
                break
        
        # Also check for data-level attribute
        if level == 0:
            data_level = day_elem.get("data-level", "")
            if data_level and data_level.isdigit():
                level = int(data_level)
        
        days.append({
            "date": date_str,
            "count": count,
            "level": level
        })
        
        total_contributions += count
        
        if count > best_day["count"]:
            best_day = {"date": date_str, "count": count}
    
    if not days:
        print("ERROR: No contribution data found.")
        return None
    
    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Sort days by date
    days_sorted = sorted(days, key=lambda x: x["date"])
    
    # Calculate current streak (from today backwards)
    today = datetime.now().date()
    check_date = today
    
    for day in reversed(days_sorted):
        day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        
        if day_date == check_date and day["count"] > 0:
            current_streak += 1
            check_date -= timedelta(days=1)
        elif day_date < check_date:
            # Day is before our check window, stop
            break
        elif day["count"] == 0:
            # Streak broken
            break
    
    # Calculate longest streak
    for day in days_sorted:
        if day["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    
    # Build result
    result = {
        "username": username,
        "generated_at": datetime.now().isoformat(),
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days
    }
    
    # Save to file
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Saved contribution data to: {output_path}")
    
    print(f"Total contributions: {total_contributions}")
    print(f"Current streak: {current_streak} days")
    print(f"Longest streak: {longest_streak} days")
    if best_day["date"]:
        print(f"Best day: {best_day['date']} ({best_day['count']} contributions)")
    else:
        print(f"Best day: No contributions yet")
    
    return result


def load_existing_data(json_path: str) -> dict:
    """Load existing contribution data if available."""
    json_path = Path(json_path)
    
    if not json_path.exists():
        return None
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate basic structure
        if "days" not in data or not data["days"]:
            print("WARNING: Existing data has no days.")
            return None
        
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARNING: Could not load existing data: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_contributions.py <username> [output.json]")
        print("  username: GitHub username")
        print("  output.json: Path to save JSON (default: data/contributions.json)")
        sys.exit(1)
    
    github_username = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if output_file is None:
        # Default to data/contributions.json
        project_root = Path(__file__).parent.parent
        output_file = project_root / "data" / "contributions.json"
    
    # Try to fetch new data
    new_data = fetch_contributions(github_username, output_file)
    
    if new_data is None:
        # If fetch failed, try to preserve existing data
        existing_data = load_existing_data(output_file)
        
        if existing_data:
            print("Keeping existing contribution data.")
        else:
            print("ERROR: No contribution data available.")
            sys.exit(1)
    else:
        print("Contribution data updated successfully.")