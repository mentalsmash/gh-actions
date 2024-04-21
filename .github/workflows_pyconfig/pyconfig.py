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
import yaml
import json
import os
import subprocess
from pathlib import Path
from collections import namedtuple
from typing import NamedTuple
import importlib


###############################################################################
#
###############################################################################
def dict_to_tuple(key: str, val: dict) -> NamedTuple:
  fields = {}
  for k, v in val.items():
    if k.startswith("_"):
      # field unsupported by namedtuple
      continue
    if isinstance(v, dict):
      v = dict_to_tuple(k, v)
    k = k.replace("-", "_").replace("/", "_")
    fields[k] = v

  keys = list(fields.keys())
  if not keys:
    return tuple()

  val_cls = namedtuple(key, keys)
  return val_cls(**fields)


###############################################################################
#
###############################################################################
def tuple_to_dict(val: NamedTuple) -> dict:
  result = val._asdict()
  for k in val._fields:
    v = getattr(val, k)
    if isinstance(v, tuple):
      v = tuple_to_dict(v)
    result[k] = v
  return result


###############################################################################
#
###############################################################################
def _select_attribute(ctx: tuple | dict, selector: str) -> str:
  def _getattr(obj: tuple | dict, k: str):
    if isinstance(obj, dict):
      return obj[k]
    else:
      return getattr(obj, k)

  def _lookup_recur(current: tuple | dict, selector_parts: list[str]) -> str:
    selected = _getattr(current, selector_parts[0])
    if len(selector_parts) == 1:
      return selected
    return _lookup_recur(selected, selector_parts[1:])

  selector_parts = selector.split(".")
  if not selector_parts:
    raise RuntimeError("a non-empty selector is required")
  return _lookup_recur(ctx, selector_parts)


###############################################################################
#
###############################################################################
def merge_dicts(result: dict, defaults: dict) -> dict:
  merged = {}
  for k, v in defaults.items():
    r_v = result.get(k)
    if isinstance(v, dict):
      r_v = merge_dicts((r_v or {}), v)
    elif r_v is None:
      r_v = v
    merged[k] = r_v
  return merged


###############################################################################
#
###############################################################################
def sha_short(clone_dir: Path | str) -> str:
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
def extract_registries(local_org: str, tags: list[str]) -> set[str]:
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
def write_output(
  vars: dict[str, bool | str | int | None] | None = None,
  export_env: list[str] | None = None,
):
  """Helper function to write variables to GITHUB_OUTPUT.

  Optionally, re-export environment variables so that they may be
  accessed from jobs.<job_id>.with.<with_id>, and other contexts
  where the env context is not available
  """

  def _output(var: str, val: bool | str | int | None):
    assert val is None or isinstance(
      val, (bool, str, int)
    ), f"unsupported output value type: {var} = {val.__class__}"
    if val is None:
      val = ""
    elif isinstance(val, bool):
      # Normalize booleans to non-empty/empty strings
      # Use lowercase variable name for easier debugging
      val = var.lower() if val else ""
    elif not isinstance(val, str):
      val = str(val)
    print(f"OUTPUT [{var}]: {val}")
    if "\n" not in val:
      output.write(var)
      output.write("=")
      if val:
        output.write(val)
      output.write("\n")
    else:
      output.write(f"{var}<<EOF" "\n")
      output.write(val)
      output.write("\n")
      output.write("EOF\n")

  github_output = Path(os.environ["GITHUB_OUTPUT"])
  with github_output.open("a") as output:
    for var in export_env or []:
      val = os.environ.get(var, "")
      _output(var, val)
    for var, val in (vars or {}).items():
      _output(var, val)


###############################################################################
#
###############################################################################
CloneDir = Path(__file__).parent.parent.parent


###############################################################################
#
###############################################################################
def configuration(
  github: str,
  inputs: str | None = None,
  as_tuple: bool = True,
) -> tuple[tuple, tuple, tuple | dict]:
  from .settings import settings

  github = dict_to_tuple("github", json.loads(github.strip()))
  inputs = (inputs or "").strip()
  if inputs:
    inputs = dict_to_tuple("inputs", json.loads(inputs.strip()))

  cfg_file = Path(__file__).parent / "settings.yml"
  cfg_dict = yaml.safe_load(cfg_file.read_text())

  print(f"Clone directory for {github.repository}: {CloneDir}")
  derived_cfg = settings(clone_dir=CloneDir, cfg=dict_to_tuple("settings", cfg_dict), github=github)

  cfg_dict = merge_dicts(derived_cfg, cfg_dict)
  cfg_dict = merge_dicts(
    cfg_dict,
    {
      "build": {
        "clone_dir": str(CloneDir),
      },
    },
  )
  if as_tuple:
    cfg = dict_to_tuple("settings", cfg_dict)
  else:
    cfg = cfg_dict

  return github, inputs, cfg


###############################################################################
#
###############################################################################
def configure(
  github: str,
  outputs: str | None = None,
  inputs: str | None = None,
  workflow: str | None = None,
):
  github, inputs, cfg_dict = configuration(github, inputs, as_tuple=False)
  cfg = dict_to_tuple("settings", cfg_dict)
  action_outputs = {}

  if outputs is not None:
    for line in outputs.splitlines():
      line = line.strip()
      if not line:
        continue
      var, val_k = line.split("=")
      var = var.strip()
      val_k = val_k.strip()
      ctx_name = val_k[: val_k.index(".")]
      ctx_select = val_k[len(ctx_name) + 1 :]
      ctx = {
        "cfg": cfg,
        "env": os.environ,
        "github": github,
        "inputs": inputs,
      }[ctx_name]
      action_outputs[var] = _select_attribute(ctx, ctx_select)

  if workflow:
    workflow_mod = importlib.import_module(f"workflows_pyconfig.workflows.{workflow}")
    workflow_outputs = workflow_mod.configure(
      clone_dir=CloneDir, cfg=cfg, github=github, inputs=inputs
    )
    action_outputs.update(workflow_outputs or {})

  if action_outputs:
    write_output(action_outputs)


###############################################################################
#
###############################################################################
def summarize(workflow: str, github: str, inputs: str | None = None):
  github, inputs, cfg = configuration(github, inputs)
  workflow_mod = importlib.import_module(f"workflows_pyconfig.workflows.{workflow}")
  summary = workflow_mod.summarize(clone_dir=CloneDir, github=github, inputs=inputs, cfg=cfg)
  with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as output:
    output.write(summary)
    output.write("\n")
