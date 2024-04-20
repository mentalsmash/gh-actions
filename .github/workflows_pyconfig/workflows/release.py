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


def summarize(github: NamedTuple, input: NamedTuple, cfg: NamedTuple) -> str:
  def _image_url(image: str) -> str:
    if image.startswith("ghcr.io/"):
      repo_name = image.split("/")[-1]
      return f"{github.repositoryUrl}/pkgs/container/{repo_name}"
    elif image.startswith(github.repository):
      return f"https://hub.docker.com/r/{image}"
    else:
      # unknown registry
      return f"https://{image}"

  return "\n".join(
    [
      f"# {cfg.dyn.build.label.capitalize()} Release - {cfg.dyn.build.version}"
      "\n"
      "\n"
      f"| **Commit SHA** | `{github.sha}` |"
      "\n"
      f"| **Release Settings** | [setting.yml]({github.repositoryUrl}/blob/{github.sha}/.github/workflows_pyconfig/settings.yml) |",
      "".join(
        [
          "| **Released Images** | <ul>",
          *(f"<li>[`{img}`]({_image_url(img)})</li>" for img in cfg.dyn.release.images),
          "</ul> |",
        ]
      ),
      "",
    ]
  )
