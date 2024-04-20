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


def summarize(github: NamedTuple, inputs: NamedTuple, cfg: NamedTuple) -> str:
  repo = github.repository.split("/")[-1]
  repo_url = f"https://github.com/{github.repository}"

  settings_link = (
    f"[settings.yml]({repo_url}/blob/{github.sha}/.github/workflows_pyconfig/settings.yml)"
  )

  def _image_link(image: str) -> str:
    image_repo = image.split(":")[0]
    repo_name = image_repo.split("/")[-1]
    if image.startswith("ghcr.io/"):
      url = f"{repo_url}/pkgs/container/{repo_name}"
    elif image.startswith(github.repository):
      url = f"https://hub.docker.com/r/{image_repo}"
    else:
      # unknown registry
      url = f"https://{image_repo}"
    return f"[`{image}`]({url})"

  prerel_image_link = _image_link(cfg.dyn.prerelease.image)
  rel_images_list = "".join(
    [
      "<ul>",
      *(f"<li>{_image_link(img)}</li>" for img in cfg.dyn.release.images),
      "</ul> |",
    ]
  )

  def _deb_pkg_link(pkg: Path) -> str:
    if github.ref_type != "tag":
      return f"`{pkg.name}`"
    url = f"{repo_url}/releases/download/{github.ref_name}/{pkg.name}"
    return f"[`{pkg}`]({url})"

  artifacts_dir = Path(github.workspace) / "artifacts"
  deb_packages = list(artifacts_dir.glob("*.deb"))
  deb_packages_list = "".join(
    [
      "<ul>",
      *(f"<li>{_deb_pkg_link(pkg)}</li>" for pkg in deb_packages),
      "</ul>",
    ]
  )

  summary_title = f"{cfg.dyn.build.label} release - {repo} - {cfg.dyn.build.version}"

  return (
    f"# {summary_title}"
    "\n"
    "\n"
    f"| Property | Value |"
    "\n"
    f"|----------|-------|"
    "\n"
    f"| **Commit SHA** | [`{github.sha}`]({repo_url}/tree/{github.sha}) |"
    "\n"
    f"| **Release Settings** | {settings_link} |"
    "\n"
    f"| **Pre-release Image** | {prerel_image_link} |"
    "\n"
    f"| **Release Images** | {rel_images_list} |"
    "\n"
    f"| **Debian Packages** | {deb_packages_list} |"
    "\n"
    "\n"
  )
