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
from pathlib import Path
from collections import namedtuple
from typing import NamedTuple
import importlib

from .write_output import write_output
from .settings import settings


###############################################################################
#
###############################################################################
def _dict_to_tuple(key: str, val: dict) -> NamedTuple:
  fields = {}
  for k, v in val.items():
    if isinstance(v, dict):
      v = _dict_to_tuple(k, v)
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
def _tuple_to_dict(val: NamedTuple) -> dict:
  result = val._asdict()
  for k in val._fields:
    v = getattr(val, k)
    if isinstance(v, NamedTuple):
      v = _tuple_to_dict(v)
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
def _merge_dicts(result: dict, defaults: dict) -> dict:
  merged = {}
  for k, v in defaults.items():
    r_v = result.get(k)
    if isinstance(v, dict):
      r_v = _merge_dicts((r_v or {}), v)
    elif r_v is None:
      r_v = v
    merged[k] = r_v
  return merged


###############################################################################
#
###############################################################################
def configure(
  github: str,
  outputs: str | None = None,
  inputs: str | None = None,
  workflow: str | None = None,
):
  github = _dict_to_tuple("github", json.loads(github))
  if inputs:
    inputs = _dict_to_tuple("inputs", json.loads(inputs))

  cfg_file = Path(__file__).parent / "settings.yml"
  cfg_dict = yaml.safe_load(cfg_file.read_text())

  derived_cfg = settings(cfg=_dict_to_tuple("settings", cfg_dict), github=github)

  # cfg = merge_dicts(derived_cfg, cfg_dict)
  cfg_dict["dyn"] = derived_cfg
  cfg = _dict_to_tuple("settings", cfg_dict)

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
    workflow_mod = importlib.import_module(f"workflow.{workflow}")
    dyn_outputs = workflow_mod.configure(cfg=cfg, github=github, inputs=inputs)
    if dyn_outputs:
      action_outputs.update(dyn_outputs)

  if action_outputs:
    write_output(action_outputs)
