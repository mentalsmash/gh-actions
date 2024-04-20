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
from typing import NamedTuple

from ..write_output import write_output


def configure(cfg: NamedTuple, github: NamedTuple, inputs: NamedTuple) -> dict:
  runner = cfg.ci.runners[f"linux/{inputs.build_platform}"]

  deb_builder_tag = inputs.base_image.replace(":", "-").replace("/", "-")
  repository_name = github.repository.replace("/", "-")
  test_id = f"deb-{deb_builder_tag}-{inputs.build_platform}__{cfg.dyn.build.version}"
  test_artifact = f"{repository_name}-debtest-{test_id}__{cfg.dyn.test_date}"
  deb_artifact = f"{repository_name}-deb-{deb_builder_tag}-{inputs.build_platform}__{cfg.dyn.build.version}__{cfg.dyn.test_date}"

  write_output(
    {
      "DEB_ARTIFACT": deb_artifact,
      "DEB_BUILDER": f"{cfg.debian.builder_repo}:{deb_builder_tag}",
      "DEB_RUNNER": runner,
      "TEST_ARTIFACT": test_artifact,
      "TEST_ID": test_id,
    }
  )
