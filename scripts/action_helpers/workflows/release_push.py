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
from action_helpers.docker_registry_from_tag import docker_registry_from_tag

def configure(
  release_tags: str,
  test_tag_registry: str,
) -> None:
  registries = set(test_tag_registry)
  for rel_tag in release_tags.splitlines():
    registry = docker_registry_from_tag(rel_tag)
    registries.add(registry)

  write_output({
    "LOGIN_DOCKERHUB": "dockerhub" in registries,
    "LOGIN_GITHUB": "github" in registries,
  })


