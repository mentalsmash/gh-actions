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
from action_helpers import (
  write_output,
  docker_registry_from_tag,
)

def configure(
  badge_nightly_base_image: str,
  badge_nightly_version: str,
  badge_stable_base_image: str,
  badge_stable_version: str,
  base_tag: str,
  build_platforms: str,
  build_tag: str,
  ref_type: str,
  release_tags: str,
  tag_suffix: str,
) -> None:
  tag = {
    "tag": f"latest{tag_suffix}",
    "branch": f"branch{tag_suffix}",
  }[ref_type]

  prerel_registry = docker_registry_from_tag(build_tag)
  prerel_image = f"{build_tag}:{tag}"

  badge_version = {
    "tag": badge_stable_version,
    "branch": badge_nightly_version,
  }[ref_type]
  
  badge_base_img = {
    "tag": badge_stable_base_image,
    "branch": badge_nightly_base_image,
  }[ref_type]

  test_platforms = ",".join((
    '"' + platform + '"'
    for platform in build_platforms.split(",")
  ))
  test_platforms = f"[{test_platforms}]"

  docker_tags_config = [
    "type=semver,pattern={{version}}",
    "type=semver,pattern={{major}}.{{minor}}",
    "type=semver,pattern={{major}}",
    *([
        f"type=raw,value={tag},priority=650",
        "type=ref,event=branch",
      ] if ref_type == "branch" else []),
  ]

  write_output({
    "BADGE_BASE_IMG": badge_base_img,
    "BADGE_VERSION": badge_version,
    "BASE_TAG": base_tag,
    "BUILD_TAG": build_tag,
    "DOCKER_BUILD_PLATFORMS": build_platforms,
    "DOCKER_TAGS_CONFIG": docker_tags_config,
    "DOCKER_FLAVOR_CONFIG": f"suffix={tag_suffix},onlatest=true",
    "PRERELEASE_IMAGE": prerel_image,
    "PRERELEASE_REGISTRY": prerel_registry,
    "RELEASE_TAGS": release_tags,
    "TEST_PLATFORMS": test_platforms,
  })
