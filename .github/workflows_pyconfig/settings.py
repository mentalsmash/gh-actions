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
import subprocess
from pathlib import Path
from typing import NamedTuple
from datetime import datetime


###############################################################################
#
###############################################################################
def _sha_short(clone_dir: Path | str) -> str:
  return (
    subprocess.run(
      ["git", "rev-parse", "--short", "HEAD"],
      cwd=clone_dir,
      stdout=subprocess.PIPE,
    )
    .stdout.decode()
    .strip()
  )


###############################################################################
#
###############################################################################
def _extract_registries(local_org: str, tags: list[str]) -> set[str]:
  def _registry_from_tag(image_tag: str) -> str:
    if image_tag.startswith(f"ghcr.io/{local_org}/"):
      return "github"
    elif image_tag.startswith(f"{local_org}/"):
      return "dockerhub"
    else:
      return None

  registries = set()
  for rel_tag in tags:
    registry = _registry_from_tag(rel_tag)
    if not registry:
      continue
    registries.add(registry)
  return registries


###############################################################################
#
###############################################################################
def settings(cfg: NamedTuple, github: NamedTuple) -> dict:
  clone_dir = Path(__file__).parent.parent

  release_tag = {
    "tag": f"latest{cfg.release.tag_suffix}",
    "branch": f"nightly{cfg.release.tag_suffix}",
  }[github.ref_type]

  docker_build_platforms = ",".join(cfg.release.build_platforms)

  docker_tags_config = "\n".join(
    [
      "type=semver,pattern={{version}}",
      "type=semver,pattern={{major}}.{{minor}}",
      "type=semver,pattern={{major}}",
      *(
        [
          f"type=raw,value={release_tag},priority=650",
          "type=ref,event=branch",
        ]
        if github.ref_type == "branch"
        else []
      ),
    ]
  )

  docker_flavor_config = f"suffix={cfg.release.tag_suffix},onlatest=true"

  ref_sha = _sha_short(clone_dir)

  if github.ref_type == "tag":
    build_label = "stable"
    build_version = github.ref_name
  else:
    build_label = "nightly"
    build_version = f"{github.ref_name}@{ref_sha}"
  build_version = build_version.replace("/", "-")

  repo_org = github.repository.split("/")[0]
  prerel_image = f"{cfg.release.prerelease_repo}:{release_tag}"
  prerel_registries = _extract_registries(
    repo_org,
    [
      cfg.release.base_image,
      prerel_image,
    ],
  )

  release_registries = _extract_registries(
    repo_org,
    [
      *cfg.release.release_repos,
      prerel_image,
    ],
  )

  test_date = datetime.now().strftime("%Y%m%d-%H%M%S")

  test_platforms_matrix = json.dumps(cfg.release.build_platforms)

  debian_base_images_matrix = json.dumps(cfg.debian.base_images)
  debian_build_architectures_matrix = json.dumps(cfg.debian.build_architectures)
  debian_registries = _extract_registries(
    repo_org,
    [
      cfg.debian.builder_repo,
      *cfg.debian.base_images,
    ],
  )

  ci_registries = _extract_registries(
    repo_org,
    [
      cfg.ci.ci_tester_repo,
    ],
  )

  badge_cfg = getattr(cfg.release.badges, build_label)
  badge_filename = github.repository.replace("/", "-") + "-badge-" + build_label
  badge_base_image = badge_cfg.base_img._as_dict()
  badge_base_image["message"] = cfg.release.base_image
  badge_base_image["filename"] = f"{badge_filename}-base-image.json"
  badge_version = badge_cfg.version._as_dict()
  badge_version["message"] = build_version
  badge_version["filename"] = f"{badge_filename}-version.json"

  return {
    "badge": {
      "base_image": badge_base_image,
      "version": badge_version,
    },
    "build": {
      "label": build_label,
      "version": build_version,
    },
    "ci": {
      "login_dockerhub": "dockerhub" in ci_registries,
      "login_github": "github" in ci_registries,
    },
    "debian": {
      "base_images_matrix": debian_base_images_matrix,
      "build_architectures_matrix": debian_build_architectures_matrix,
      "login_dockerhub": "dockerhub" in debian_registries,
      "login_github": "github" in debian_registries,
    },
    "docker": {
      "build_platforms": docker_build_platforms,
      "flavor_config": docker_flavor_config,
      "tags_config": docker_tags_config,
    },
    "prerelease": {
      "image": prerel_image,
      "login_dockerhub": "dockerhub" in prerel_registries,
      "login_github": "github" in prerel_registries,
    },
    "release": {
      "login_dockerhub": "dockerhub" in release_registries,
      "login_github": "github" in release_registries,
      "tag": release_tag,
      "test_platforms_matrix": test_platforms_matrix,
      "release_repos": "\n".join(cfg.release.release_repos),
    },
    "test_date": test_date,
  }
