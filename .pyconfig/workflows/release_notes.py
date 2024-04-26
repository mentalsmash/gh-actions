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
from pathlib import Path
from typing import NamedTuple
import json
from fnmatch import fnmatch

from release_tracker import ReleaseTracker


def _image_link(github: NamedTuple, cfg: NamedTuple, image: str) -> str:
  image_repo = image.split(":")[0]
  repo_name = image_repo.split("/")[-1]
  if image.startswith("ghcr.io/"):
    url = f"{cfg.build.repository.url}/pkgs/container/{repo_name}"
  elif image.startswith(github.repository):
    url = f"https://hub.docker.com/r/{image_repo}"
  else:
    # unknown registry
    url = f"https://{image_repo}"
  return f"[`{image}`]({url})"


def _deb_pkg_link(github: NamedTuple, cfg: NamedTuple, pkg: Path) -> str:
  if github.ref_type != "tag":
    return f"`{pkg.name}`"
  url = f"{cfg.build.repository.url}/releases/download/{github.ref_name}/{pkg.name}"
  return f"[`{pkg.name}`]({url})"


def summarize(clone_dir: Path, github: NamedTuple, inputs: NamedTuple, cfg: NamedTuple) -> str:
  workspace_dir = Path(f"{github.workspace}")
  # Read release-tracker commit id
  reltracker_commit_f = Path(f"{cfg.build.artifacts_dir}/release-tracker.commit")
  reltracker_commit = reltracker_commit_f.read_text()
  # Read list of generated images from the release-tracker's summary
  reltracker_summary_f = Path(f"{cfg.build.artifacts_dir}/release-tracker-summary.json")
  reltracker_summary = json.loads(reltracker_summary_f.read_text())
  reltracker_version_id = ReleaseTracker.version_id(
    reltracker_summary["entry"]["created_at"], reltracker_summary["entry"]["version"]
  )
  release_docker_manifest_f_rel = Path(
    f"{reltracker_summary['storage']}/{reltracker_summary['track']}/{reltracker_version_id}/docker-manifests.json"
  )
  release_docker_manifest_f = workspace_dir / release_docker_manifest_f_rel
  release_docker_manifest = json.loads(release_docker_manifest_f.read_text())

  release_docker_layers = {}
  for img, img_manifest in release_docker_manifest["images"].items():
    img_layers = release_docker_layers[img] = release_docker_layers.get(img, {})
    arch_layers = {
      layer["digest"]: {
        "image": img,
        "platform": layer["platform"],
        "unknown": False,
      }
      for layer in img_manifest["manifests"]
      if layer["platform"]["os"] != "unknown"
    }
    unknown_layers = {
      layer["digest"]: {"image": img, "platform": base_platform, "unknown": True}
      for layer in img_manifest["manifests"]
      if layer["platform"]["os"] == "unknown"
      for base_platform in [
        next(
          base_layer_cfg["platform"]
          for base_layer, base_layer_cfg in arch_layers.items()
          if base_layer == layer["annotations"]["vnd.docker.reference.digest"]
        )
      ]
    }
    img_layers.update(arch_layers)
    img_layers.update(unknown_layers)

  reltracker_log_url = f"{cfg.release.tracker.url}/blob/{reltracker_commit}/{cfg.build.profile}/{release_docker_manifest_f_rel}"

  generated_images = set(release_docker_manifest["images"].keys())
  # generated_images = reduce(lambda r, v: r | set(v), release_docker_manifest["layers"].values(), set())
  missing_images = set(cfg.release.final_images) - generated_images

  # Detect generated Debian packages
  deb_packages = list(Path(cfg.build.artifacts_dir).glob("*.deb"))
  expected_deb_packages_globs = [
    f"{cfg.build.repository.name}_*_{arch}.deb" for arch in cfg.debian.builder.architectures
  ]
  missing_deb_packages = [
    matched
    for glob in expected_deb_packages_globs
    for matched in [next((pkg for pkg in deb_packages if fnmatch(pkg, glob)), None)]
    if matched
  ]

  missing_section = bool(missing_images or missing_deb_packages)

  result = [
    f"# {cfg.build.repository.name} - {cfg.build.profile} release - {cfg.build.version}",
    "",
    "## Configuration",
    "",
    "| Property | Value |",
    "|----------|-------|",
    "| **CI Settings** "
    + f"| [settings.yml]({cfg.build.repository.url}/blob/{github.sha}/{cfg.build.settings_file})"
    + " |",
    "| **Source Commit** | "
    + f"[`{github.sha}`]({cfg.build.repository.url}/tree/{github.sha})"
    + " |",
    # "| **GitHub Release** | "
    # + (
    #   f"[{github.ref_name}]({cfg.build.repository.url}/releases/tag/{github.ref_name})"
    #   if github.ref_type == "branch"
    #   else "N/A"
    # )
    # + " |",
    "| **Release Log** | " f"[{reltracker_version_id}]({reltracker_log_url})" " |",
    "",
    "## Artifacts",
    "",
    "| Type | Artifacts |",
    "|------|-----------|",
    f"| **Pre-release Image** | {_image_link(github, cfg, cfg.release.prerelease_image)} |",
    "| **Release Images** | "
    + "".join(
      [
        "<ul>",
        *(f"<li>{_image_link(github, cfg, img)}</li>" for img in generated_images),
        "</ul> |",
      ]
    )
    + " |",
    "| **Debian Packages** | "
    + (
      "".join(
        [
          "<ul>",
          *(f"<li>{_deb_pkg_link(github, cfg, pkg)}</li>" for pkg in deb_packages),
          "</ul>",
        ]
      )
      if deb_packages
      else "No packages were generated."
    )
    + " |",
    "",
    *(
      [
        "## Missing Artifacts",
        "",
        "| Type | Artifacts |",
        "|------|-----------|",
        "| **Release Images** | "
        + "".join(
          [
            "<ul>",
            *(f"<li>{_image_link(github, cfg, img)}</li>" for img in missing_images),
            "</ul> |",
          ]
        )
        + " |",
        "| **Debian Packages** | "
        + "".join(
          [
            "<ul>",
            *(f"<li>`{pkg}`</li>" for pkg in missing_deb_packages),
            "</ul>",
          ]
        )
        + " |",
        "",
      ]
      if missing_section
      else []
    ),
    "## Docker Image Manifests ",
    "| **Image** | **Manifest** | **Platform** |",
    "|-----------|--------------|--------------|",
    *(
      f"| `{layer['image']}` | `{digest}` | `{layer['platform']['os']}`/`{layer['platform']['architecture']}`{' (unknown)' if layer['unknown'] else ''} |"
      for layers in release_docker_layers.values()
      for digest, layer in layers.items()
    ),
    "",
  ]

  return "\n".join(result)
