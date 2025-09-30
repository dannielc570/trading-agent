#!/usr/bin/env python3
"""Launch the Trading Platform Web UI"""
import uvicorn
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from web_ui.app import app

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Starting Trading Strategy Platform Web UI")
    print("=" * 80)
    print()
    print("📊 Dashboard URL: http://localhost:8080")
    print("📚 API Docs: http://localhost:8080/docs")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 80)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
