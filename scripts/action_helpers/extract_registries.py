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
from action_helpers.docker_registry_from_tag import docker_registry_from_tag

def extract_registries(tags: list[str]) -> set[str]:
  registries = set()
  for rel_tag in tags:
    registry = docker_registry_from_tag(rel_tag)
    registries.add(registry)
  return registries

