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
from action_helpers.action_runner import action_runner
from action_helpers.current_timestamp import current_timestamp
from action_helpers.github_ref_vars import github_ref_vars
from action_helpers.write_output import write_output

def configure(
  clone_dir: str,
  ref_name: str,
  ref_type: str,
  repository: str,
  test_platform: str,
) -> None:
  build_label, build_version = github_ref_vars(
    clone_dir=clone_dir,
    ref_type=ref_type,
    ref_name=ref_name)
  runner = action_runner(test_platform)
  repository_name = repository.replace("/", "-")
  platform_name = test_platform.replace("/", "-")
  test_date = current_timestamp()
  test_id = f"release-{platform_name}-{build_label}__{build_version}"
  test_artifact = f"{repository_name}-test-{test_id}__{test_date}"
  write_output({
    "TEST_ID": test_id,
    "TEST_ARTIFACT": test_artifact,
    "TEST_DATE": test_date,
    "RUNNER": runner,
  })

