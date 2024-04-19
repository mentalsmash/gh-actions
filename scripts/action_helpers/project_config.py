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
from pathlib import Path

from collections import namedtuple
from typing import NamedTuple

def project_config(
    clone_dir: str,
    github: str) -> tuple[NamedTuple, NamedTuple]:
  def _dict_to_ntuple(key: str, val: dict) -> NamedTuple:
    fields = {}
    for k, v in val.items():
      if isinstance(v, dict):
        v = _dict_to_ntuple(k, v)
      k = k.replace("-", "_")
      fields[k] = v
    
    keys = list(fields.keys())
    print("DEFINING TUPLE:", key, keys)
    val_cls = namedtuple(key, keys)
    return val_cls(**fields)

  settings = yaml.safe_load(
    Path(f"{clone_dir}/project.yml").read_text())
  github = yaml.safe_load(github)

  return settings, github
