#!/usr/bin/env python3
"""
Configuration loader for Saransh Nimje's GitHub Profile README generator.
Reads profile data from data/profile.json.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


class ProfileConfig:
    """Loads and provides access to profile configuration."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to data/profile.json relative to project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "data" / "profile.json"
        
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)
        
        return self._config
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get loaded configuration, loading if necessary."""
        if self._config is None:
            self.load()
        return self._config
    
    @property
    def name(self) -> str:
        return self.config.get("name", "")
    
    @property
    def username(self) -> str:
        return self.config.get("username", "")
    
    @property
    def education(self) -> str:
        return self.config.get("education", "")
    
    @property
    def role(self) -> str:
        return self.config.get("role", "")
    
    @property
    def focus(self) -> List[str]:
        return self.config.get("focus", [])
    
    @property
    def current_projects(self) -> List[Dict[str, Any]]:
        return self.config.get("current_projects", [])
    
    @property
    def tech_stack(self) -> Dict[str, List[str]]:
        return self.config.get("tech_stack", {})
    
    @property
    def current_focus(self) -> List[str]:
        return self.config.get("current_focus", [])
    
    @property
    def social_links(self) -> Dict[str, str]:
        return self.config.get("social_links", {})
    
    def get_priority_project(self) -> Dict[str, Any]:
        """Get the priority project (Sovereign AI Workbench)."""
        for project in self.current_projects:
            if project.get("priority", False):
                return project
        return {}


def get_config() -> ProfileConfig:
    """Get a loaded ProfileConfig instance."""
    config = ProfileConfig()
    config.load()
    return config


if __name__ == "__main__":
    # Test loading configuration
    config = get_config()
    print(f"Name: {config.name}")
    print(f"Username: {config.username}")
    print(f"Education: {config.education}")
    print(f"Focus: {', '.join(config.focus)}")
    print(f"Tech Stack Categories: {list(config.tech_stack.keys())}")