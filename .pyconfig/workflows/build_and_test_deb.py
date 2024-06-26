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
  runner = json.dumps(getattr(cfg.ci.runners, f"linux_{inputs.build_architecture}"))

  deb_builder_tag = inputs.base_image.replace(":", "-").replace("/", "-")
  repo = github.repository.split("/")[-1]
  test_id = f"deb-{deb_builder_tag}-{inputs.build_architecture}__{cfg.build.version}"
  test_artifact = f"{repo}-debtest-{test_id}"
  deb_artifact = f"{repo}-deb-{deb_builder_tag}-{inputs.build_architecture}__{cfg.build.version}"

  return {
    "DEB_ARTIFACT": deb_artifact,
    "DEB_BUILDER": f"{cfg.debian.builder.repo}:{deb_builder_tag}",
    "DEB_RUNNER": runner,
    "TEST_ARTIFACT": test_artifact,
    "TEST_ID": test_id,
  }
