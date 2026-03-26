"""One-command installer for finance-skills-pack.

Usage:
    python setup_env.py --global    # Install skills globally (~/.claude/skills/)
    python setup_env.py --local     # Install skills to current project (.claude/skills/)
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Install finance-skills-pack")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--global", dest="install_global", action="store_true",
                       help="Install skills globally to ~/.claude/skills/")
    group.add_argument("--local", dest="install_local", action="store_true",
                       help="Install skills to .claude/skills/ in current directory")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    skills_src = project_root / "skills"

    if args.install_global:
        target = Path.home() / ".claude" / "skills"
    else:
        target = Path.cwd() / ".claude" / "skills"

    # Copy each skill directory
    for skill_dir in skills_src.iterdir():
        if skill_dir.is_dir():
            dest = target / skill_dir.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(skill_dir, dest)
            print(f"  Installed: /{skill_dir.name} -> {dest}")

    # Install Python dependencies for /backtest
    print("\nInstalling Python dependencies for /backtest...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(project_root / "requirements.txt")],
        check=True,
    )

    print("\nDone! Open Claude Code and try: /stock-check AAPL")


if __name__ == "__main__":
    main()
