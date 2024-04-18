from pathlib import Path
import os
def write_output(vars: dict[str, object] | None = None, export_env: list[str] | None = None):
  """Helper function to write variables to GITHUB_OUTPUT.
  
  Optionally, re-export environment variables so that they may be
  accessed from jobs.<job_id>.with.<with_id>, and other contexts
  where the env context is not available
  """
  def _output(var: str, val: object):
    output.write(f"{var}<<EOF""\n")
    output.write(str(val))
    output.write("\n")
    output.write("EOF\n")
  github_output = Path(os.environ["GITHUB_OUTPUT"])
  with github_output.open("a") as output:
    for var in (export_env or []):
      val = os.environ.get(var, '')
      _output(var, val)
    for var, val in (vars or {}).items():
      _output(var, val)
