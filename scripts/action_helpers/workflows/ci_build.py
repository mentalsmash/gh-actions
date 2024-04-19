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
from action_helpers.write_output import write_output
from action_helpers.git_ref_vars import git_ref_vars
from action_helpers.action_runner import action_runner
from action_helpers.current_timestamp import current_timestamp
from action_helpers.extract_registries import extract_registries

def configure(
    base_image: str,
    build_platform: str,
    ci_tester_tag: str,
    clone_dir: str,
    ref_name: str,
    ref_type: str,
    repository: str):
  _, build_version = git_ref_vars(clone_dir, ref_type, ref_name)
  runner = action_runner(build_platform)
  repository_name = repository.replace("/", "-")
  build_platform_label = build_platform.replace("/", "-")
  base_image_tag = base_image.replace(":", "-")
  ci_tester_image = f"{ci_tester_tag}:{base_image_tag}"
  test_date = current_timestamp()
  test_id = f"ci-{build_platform_label}__{build_version}"
  test_artifact = f"{repository_name}-test-{test_id}__{test_date}"

  registries = extract_registries([ci_tester_image])

  write_output({
    "CI_TESTER_IMAGE": ci_tester_image,
    "LOGIN_GITHUB": "github" in registries,
    "LOGIN_DOCKERHUB": "dockerhub" in registries,
    "RUNNER": runner,
    "TEST_ARTIFACT": test_artifact,
    "TEST_ID": test_id,
    "TEST_DATE": test_date,
  })
