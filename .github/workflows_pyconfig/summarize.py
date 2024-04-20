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
import os
from pathlib import Path
import importlib
from .configure import configuration


###############################################################################
#
###############################################################################
def summarize(workflow: str, github: str, inputs: str | None = None):
  cfg = configuration(github, inputs)
  workflow_mod = importlib.import_module(f"workflows_pyconfig.workflows.{workflow}")
  summary = workflow_mod.summarize(github=github, inputs=inputs, cfg=cfg)
  with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as output:
    output.write(summary)
    output.write("\n")
