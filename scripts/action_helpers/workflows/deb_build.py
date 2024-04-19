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
from action_helpers.action_runner import action_runner
from action_helpers.git_ref_vars import git_ref_vars
from action_helpers.current_timestamp import current_timestamp
from action_helpers.extract_registries import extract_registries

def configure(
    base_tag: str,
    clone_dir: str,
    deb_builder: str,
    platform: str,
    ref_name: str,
    ref_type: str,
    repository: str,
  ) -> tuple[bool, bool, bool]:
  
  runner = action_runner(f"linux/{platform}")

  _, build_version = git_ref_vars(clone_dir, ref_type, ref_name)

  deb_builder_tag = base_tag.replace(":", "-").replace("/", "-")

  repository_name = repository.replace("/", "-")
  test_date = current_timestamp()
  test_id = f"deb-{deb_builder_tag}-{platform}__{build_version}"
  test_artifact = f"{repository_name}-debtest-{test_id}__{test_date}"
  deb_artifact = f"{repository_name}-deb-{deb_builder_tag}-{platform}__{build_version}__{test_date}"

  registries = extract_registries([base_tag, deb_builder])
  login_dockerhub = "dockerhub" in registries
  login_github = "github" in registries

  write_output({
    "DEB_BUILDER": f"{deb_builder}:{deb_builder_tag}",
    "DEB_ARTIFACT": deb_artifact,
    "LOGIN_DOCKERHUB": login_dockerhub,
    "LOGIN_GITHUB": login_github,
    "RUNNER": runner,
    "TEST_ARTIFACT": test_artifact,
    "TEST_DATE": test_date,
    "TEST_ID": test_id,
  })