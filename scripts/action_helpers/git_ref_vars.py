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
from pathlib import Path
from action_helpers.sha_short import sha_short

def git_ref_vars(clone_dir: Path | str, ref_type: str, ref_name: str) -> tuple[str, str]:
  if ref_type == "branch":
    build_label = "nightly"
    build_version = f"{ref_name}@{sha_short(clone_dir)}"
  elif ref_type == "tag":
    build_label = "stable"
    build_version = ref_name
  else:
    raise RuntimeError("unknown ref type", ref_type)
  build_version = build_version.replace("/", "-")
  return build_label, build_version
