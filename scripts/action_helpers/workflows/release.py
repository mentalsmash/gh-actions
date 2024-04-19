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
from action_helpers.project_config import project_config

def configure(clone_dir: str, github: str) -> None:
  cfg, github = project_config(clone_dir, github)

  tag = {
    "tag": f"latest{cfg.release.tag_suffix}",
    "branch": f"nightly{cfg.release.tag_suffix}",
  }[github.ref_type]

  prerel_registry = docker_registry_from_tag(cfg.release.prerelease_tag)
  prerel_image = f"{cfg.release.prerelease_tag}:{tag}"

  badge_version = {
    "tag": cfg.release.badge.stable.version,
    "branch": cfg.release.badge.nightly.version,
  }[github.ref_type]
  
  badge_base_img = {
    "tag": cfg.release.badge.stable.base_image,
    "branch": cfg.release.badge.nightly.base_image,
  }[github.ref_type]

  build_platforms = ",".join(cfg.release.build_platforms)
  test_platforms = ",".join('"'+plat+'"' for plat in cfg.release.build_platforms)
  test_platforms = f"[{test_platforms}]"

  docker_tags_config = "\n".join([
    "type=semver,pattern={{version}}",
    "type=semver,pattern={{major}}.{{minor}}",
    "type=semver,pattern={{major}}",
    *([
        f"type=raw,value={tag},priority=650",
        "type=ref,event=branch",
      ] if github.ref_type == "branch" else []),
  ])

  docker_flavor_config = f"suffix={cfg.release.tag_suffix},onlatest=true"

  release_tags = "\n".join(cfg.release.release_tags)

  write_output({
    "BADGE_BASE_IMG": badge_base_img,
    "BADGE_VERSION": badge_version,
    "BASE_TAG": cfg.release.base_tag,
    "DOCKER_BUILD_PLATFORMS": build_platforms,
    "DOCKER_TAGS_CONFIG": docker_tags_config,
    "DOCKER_FLAVOR_CONFIG": docker_flavor_config,
    "PRERELEASE_TAG": cfg.release.prerelease_tag,
    "PRERELEASE_IMAGE": prerel_image,
    "PRERELEASE_REGISTRY": prerel_registry,
    "RELEASE_TAGS": release_tags,
    "TEST_PLATFORMS": test_platforms,
  })
