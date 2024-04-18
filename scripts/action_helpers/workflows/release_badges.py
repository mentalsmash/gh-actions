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
from action_helpers.sha_short import sha_short
from action_helpers.write_output import write_output
from action_helpers.github_ref_vars import github_ref_vars

def configure(
  clone_dir: str,
  ref_type: str,
  ref_name: str,
  repository: str,
) -> None:
  build_type, _ = github_ref_vars(clone_dir, ref_type, ref_name)

  if ref_type == "branch":
    version = sha_short(clone_dir)
    color_version = "orange"
  elif ref_type == "tag":
    version = ref_name
    color_version = "green"
  else:
    raise RuntimeError("invalid ref type", ref_type)

  badge_filename = repository.replace("/", "-") + "-badge-" + build_type

  write_output({
    "VERSION": version,
    "COLOR_VERSION": color_version,
    "COLOR_BASE_IMG": "blue",
    "TAG": build_type,
    "BADGE_FILENAME": badge_filename,
  })


