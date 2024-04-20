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
import json
from typing import NamedTuple
from pathlib import Path


def configure(clone_dir: Path, cfg: NamedTuple, github: NamedTuple, inputs: NamedTuple) -> dict:
  runner = json.dumps(getattr(cfg.ci.runners, inputs.build_platform.replace("/", "_")))

  repo = github.repository.split("/")[-1]
  build_platform_label = inputs.build_platform.replace("/", "-")
  base_image_tag = inputs.base_image.replace(":", "-")
  tester_image = f"{cfg.ci.tester_repo}:{base_image_tag}"

  test_id = f"ci-{build_platform_label}__{cfg.build.version}"
  test_artifact = f"{repo}-test-{test_id}__{cfg.build.date}"

  return {
    "CI_RUNNER": runner,
    "CI_TESTER_IMAGE": tester_image,
    "TEST_ARTIFACT": test_artifact,
    "TEST_ID": test_id,
  }
