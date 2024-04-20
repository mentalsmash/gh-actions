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


def summarize(github: NamedTuple, inputs: NamedTuple, cfg: NamedTuple) -> str:
  repo = github.repository.split("/")
  repo_url = f"https://github.com/{github.repository}"

  def _image_url(image: str) -> str:
    image_repo = image.split(":")[0]
    repo_name = image_repo.split("/")[-1]
    if image.startswith("ghcr.io/"):
      return f"{repo_url}/pkgs/container/{repo_name}"
    elif image.startswith(github.repository):
      return f"https://hub.docker.com/r/{image_repo}"
    else:
      # unknown registry
      return f"https://{image_repo}"

  return "\n".join(
    [
      f"# {repo} - {cfg.dyn.build.label.capitalize()} Release - {cfg.dyn.build.version}"
      "\n"
      "\n"
      f"| Property | Value |"
      "\n"
      f"|----------|-------|"
      "\n"
      f"| **Commit SHA** | [`{github.sha}`]({repo_url}/tree/{github.sha}) |"
      "\n"
      f"| **Release Settings** | [settings.yml]({repo_url}/blob/{github.sha}/.github/workflows_pyconfig/settings.yml) |"
      "\n"
      f"| **Pre-release Image** | [`{cfg.dyn.prerelease.image}`]({_image_url(cfg.dyn.prerelease.image)}) |",
      "".join(
        [
          "| **Release Images** | <ul>",
          *(f"<li>[`{img}`]({_image_url(img)})</li>" for img in cfg.dyn.release.images),
          "</ul> |",
        ]
      ),
      "",
    ]
  )
