###############################################################################
# Copyright 2020-2024 Andrea Sorbini
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################
import shlex
from pathlib import Path
import os
def write_output(vars: dict[str, bool | str | int] | None = None, export_env: list[str] | None = None):
  """Helper function to write variables to GITHUB_OUTPUT.
  
  Optionally, re-export environment variables so that they may be
  accessed from jobs.<job_id>.with.<with_id>, and other contexts
  where the env context is not available
  """
  def _output(var: str, val: bool | str | int):
    assert isinstance(val, (bool,  str, int)), f"unsupported output value type: {var} = {val.__class__}"
    if isinstance(val, bool):
      # Normalize booleans to non-empty/empty strings
      # Use lowercase variable name for easier debugging
      val = var.lower() if val else ''
    elif not isinstance(val, str):
      val = str(val)
    # Quote non empty strings
    if val:
      val = shlex.quote(val)
    print(f"OUTPUT [{var}]: {val}")
    output.write(var)
    output.write("=")
    if val:
      output.write(val)
    output.write("\n")
    # output.write(f"{var}<<EOF""\n")
    # output.write(str(val))
    # output.write("\n")
    # output.write("EOF\n")
  github_output = Path(os.environ["GITHUB_OUTPUT"])
  with github_output.open("a") as output:
    for var in (export_env or []):
      val = os.environ.get(var, '')
      _output(var, val)
    for var, val in (vars or {}).items():
      _output(var, val)
