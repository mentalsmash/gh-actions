
import subprocess
from pathlib import Path

def sha_short(clone_dir: Path | str) -> str:
  return subprocess.run([
    "git", "rev-parse", "--short", "HEAD"
  ], cwd=clone_dir, stdout=subprocess.PIPE).stdout.decode().strip()

