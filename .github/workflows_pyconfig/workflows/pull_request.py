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
from typing import NamedTuple
from pathlib import Path


def configure(cfg: NamedTuple, github: NamedTuple, inputs: NamedTuple) -> dict:
  clone_dir = Path(__file__).parent.parent.parent.parent

  is_draft = bool(github.event.pull_request.draft)
  pr_no = github.event.pull_request.number

  if github.event_name == "pull_request_review":
    review_state = github.event.review.state
  else:
    review_state = None

  result_full = False
  result_deb = False
  result_basic = False

  review_state = review_state or ""

  if is_draft:
    print(f"PR #{pr_no} is still in draft, no validation required yet.")
  elif github.event_name == "pull_request_review" and review_state == "approved":
    # A new review was submitted, and the review state is "approved":
    # perform a full validation (ci build on more platforms + deb validation)
    print(f"PR #{pr_no} reviewed and approved")
    result_full = True
  elif github.event_name == "pull_request":
    # The PR was updated, and it is not a draft: perform a basic validation if:
    # - PR.state == 'opened':
    #   -> PR opened as non-draft, perform an initial check
    # - PR.state == 'synchronized':
    #   -> PR updated by new commits.
    #      TODO(asorbini) assert(${{ github.event.action }} != 'approved')
    #      (assumption is that any commit will invalidate a previous 'approved')
    # - PR.state == 'ready_for_review':
    #   -> PR moved out of draft, run basic validation, and possibly full validation too
    #      if the PR is already in "accepted" state
    print(f"PR #{pr_no} updated ({github.event.action})")
    result_basic = True
    if github.event.action == "ready_for_review":
      # (assumption: if the PR is not "mergeable" it must have not been approved.
      # Ideally: we would just query the review state, but that doesn't seem to
      # be available on the pull_request object, see:
      # https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request)
      # So we use the GitHub API to query the state,
      # see: https://stackoverflow.com/a/77647838
      subprocess.run(["gh", "repo", "set-default", github.repository], cwd=clone_dir, check=True)
      review_state = (
        subprocess.run(
          [
            "gh",
            "pr",
            "view",
            str(pr_no),
            "--json",
            "reviewDecision",
            "--jq",
            ".reviewDecision",
          ],
          cwd=clone_dir,
          stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
      )
      print(f"PR #{pr_no} detected review state: '{review_state}'")
      result_full = review_state == "approved"

  # Debian testing requires a debian package, and for now we tie it to the full validation
  result_deb = result_full and (clone_dir / "debian" / "control").is_file()

  print(f"PR #{pr_no} job configuration:")
  print(f"- draft: {is_draft}")
  print(f"- event: {github.event_name}")
  print(f"- action: {github.event.action}")
  print(f"- review: {review_state}")
  print(f"- triggers: basic={result_basic}, full={result_full}, deb={result_deb}")

  return {
    "BASIC_VALIDATION_BASE_IMAGES": json.dumps(cfg.pull_request.validation.basic.base_images),
    "BASIC_VALIDATION_BUILD_PLATFORMS": json.dumps(
      cfg.pull_request.validation.basic.build_platforms
    ),
    "DEB_VALIDATION_BASE_IMAGES": json.dumps(cfg.pull_request.validation.deb.base_images),
    "DEB_VALIDATION_BUILD_ARCHITECTURES": json.dumps(
      cfg.pull_request.validation.deb.build_architectures
    ),
    "FULL_VALIDATION_BASE_IMAGES": json.dumps(cfg.pull_request.validation.full.base_images),
    "FULL_VALIDATION_BUILD_PLATFORMS": json.dumps(cfg.pull_request.validation.full.build_platforms),
    "VALIDATE_FULL": result_full,
    "VALIDATE_DEB": result_deb,
    "VALIDATE_BASIC": result_basic,
  }
