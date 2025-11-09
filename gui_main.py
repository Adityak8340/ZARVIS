"""
ZARVIS GUI Launcher
Run this file to start ZARVIS with the graphical interface
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import ZARVIS
from src.gui import launch_gui  # Now imports from modular gui package


def main():
    """Main entry point for GUI version."""
    print("=" * 60)
    print("🧠 ZARVIS - Graphical Interface")
    print("=" * 60)
    
    try:
        # Load environment
        load_dotenv()
        
        # Initialize ZARVIS
        print("Initializing ZARVIS...")
        zarvis = ZARVIS()
        
        # Launch GUI
        print("Launching GUI...")
        sys.exit(launch_gui(zarvis))
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    main()
