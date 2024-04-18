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
import subprocess
from pathlib import Path

def pull_request_validate_actions(
    clone_dir: Path,
    pr_no: int,
    event_name: str,
    event_action: str,
    is_draft: bool,
    review_state: str | None = None) -> tuple[bool, bool, bool]:
  result_full = False
  result_basic = False
  result_not_needed = False

  review_state = review_state or ""

  if event_name == "pull_request_review":
    if review_state == "approved":
      # A new review was submitted, and the review state is "approved":
      # perform a full validation (ci build on more platforms + deb validation)
      result_full = True
      # If the PR is still in draft: perform also a basic validation
      if is_draft:
        result_basic = True
    else:
      # A new review was submitted, but the state is not "approved": nothing to do yet
      pass
  elif event_name == "pull_request":
    if is_draft:
      # The PR was updated but it is still in draft: nothing to do
      pass
    else:
      # The PR was updated, and it is not a draft: perform a basic validation if:
      # - PR.state == 'opened':
      #   -> PR opened as non-draft, perform an initial check
      # - PR.state == 'synchronized':
      #   -> PR updated by new commits.
      #      TODO(asorbini) assert(${{ github.event.action }} != 'approved')
      #      (assumption is that any commit will invalidate a previous 'approved')
      # - PR.state == 'ready_for_review':
      #   -> PR moved out of draft, run basic validation only if not already 'approved'.
      #      (assumption: a basic validation was already performed on the `pull_request_review`
      #       event for the approval.)
      if event_action in ("opened", "synchronized"):
        result_basic = True
      elif event_action == "ready_for_review":
        # (assumption: if the PR is not "mergeable" it must have not been approved.
        # Ideally: we would just query the review state, but that doesn't seem to
        # be available on the pull_request object, see:
        # https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request)
        # So we use the GitHub API to query the state,
        # see: https://stackoverflow.com/a/77647838
        subprocess.run([
          "gh", "repo", "set-default", clone_dir
        ], check=True)
        review_state = subprocess.run([
          "gh", "pr", "view", str(pr_no), "--json", "reviewDecision", "--jq", ".reviewDecision"
        ], cwd=clone_dir, stdout=subprocess.PIPE).stdout.decode().strip()
        if review_state == "approved":
          result_not_needed = True
        else:
          result_basic = True


  return (result_full, result_basic, result_not_needed)