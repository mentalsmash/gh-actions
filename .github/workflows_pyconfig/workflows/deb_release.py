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


def configure(
  deb_artifacts_prefix: str,
  deb_platforms: str,
  deb_images: str,
  event_name: str,
  ref_name: str,
  ref_type: str,
) -> tuple[bool, bool, bool]:
  deb_build = (event_name == "workflow_run" and ref_name == "master") or ref_type == "tag"
  write_output(
    {
      "DEB_BUILD": deb_build,
      "DEB_IMAGES": deb_images,
      "DEB_PLATFORMS": deb_platforms,
      "DEB_ARTIFACTS_PREFIX": deb_artifacts_prefix,
    }
  )
