import os
from pathlib import Path
import re
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List

@dataclass
class ProjectConfig:
  name: str = "fpga_test_project"
  top_module: str = "top"
  part: str = ""
  board: str = ""

@dataclass
class FilesConfig:
  sources: List[str] = field(default_factory=lambda: ["src/top.v"])
  constraints: List[str] = field(default_factory=lambda: ["constraints/top.xdc"])
  include_dirs: List[str] = field(default_factory=lambda: [""])

@dataclass
class SimulationConfig:
  tool: str = "xsim"
  testbenches: List[str] = field(default_factory=lambda: ["test/top_tb.v"])
  waves: bool = True

@dataclass
class SynthesisConfig:
  strategy: str = "default"
  flatten_hierarchy: str = "none"

@dataclass
class ImplementationConfig:
  optimize: bool = True
  place_directive: str = "Explore"
  route_directive: str = "Quick"

@dataclass
class ProgrammingConfig:
  openocd_interface: str = "digilent"
  bitstream: str = "build/top.bit"
  autoprogram: bool = False

@dataclass
class VivadoConfig:
  version: str = "2024.2"
  tcl_hooks: List[str] = field(default_factory=lambda: ["hooks/pre.tcl", "hooks/post.tcl"])

@dataclass
class Config:
  project: ProjectConfig = ProjectConfig()
  files: FilesConfig = FilesConfig()
  simulation: SimulationConfig = SimulationConfig()
  synthesis: SynthesisConfig = SynthesisConfig()
  implementation: ImplementationConfig = ImplementationConfig()
  programming: ProgrammingConfig = ProgrammingConfig()
  vivado: VivadoConfig = VivadoConfig()

class ConfigManager:
  def __init__(self, local_filename="viv.toml", home_filename=".viv.toml"):
    self.home_path = Path.home() / home_filename
    self.local_path = Path(local_filename)
    if not self.local_path.exists():
      raise FileNotFoundError(f"local config file '{local_filename}' not found.")
    self.config_dict = {}
    self.load(self.home_path)
    self.load(self.local_path)
    self.config = Config()
    self._apply_dict_to_dataclass()

  def load(self, path: Path):
    if not path.exists():
      return
    with open(path, "r") as f:
      parsed = self._parse_toml(f.read())
      self._deep_update(self.config_dict, parsed)

  def _deep_update(self, base: dict, updates: dict):
    for k, v in updates.items():
      if isinstance(v, dict) and k in base and isinstance(base[k], dict):
        self._deep_update(base[k], v)
      else:
        base[k] = v

  def get(self, section, key, default=None):
    return self.config_dict.get(section, {}).get(key, default)

  def get_section(self, section):
    return self.config_dict.get(section, {})

  def _parse_toml(self, text: str) -> dict:
    data = {}
    current = None
    sec_re = re.compile(r'^\s*\[(.+?)\]\s*$')
    kv_re = re.compile(r'^\s*([\w\-]+)\s*=\s*(.+?)\s*(#.*)?$')

    def conv(v: str):
      v = v.strip()
      if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
      if v.lower() == "true":
        return True
      if v.lower() == "false":
        return False
      if v.startswith("[") and v.endswith("]"):
        return [conv(x) for x in v[1:-1].split(",") if x.strip()]
      try:
        return int(v)
      except:
        pass
      try:
        return float(v)
      except:
        pass
      try:
        return datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ")
      except:
        pass
      return v

    for line in text.splitlines():
      line = line.strip()
      if not line or line.startswith("#"):
        continue
      sec = sec_re.match(line)
      if sec:
        current = {}
        data[sec.group(1)] = current
        continue
      kv = kv_re.match(line)
      if kv and current is not None:
        current[kv.group(1)] = conv(kv.group(2))
    return data

  def _apply_dict_to_dataclass(self):
    d = self.config_dict
    for section_name in asdict(self.config):
      section_data = d.get(section_name)
      if section_data:
        section_obj = getattr(self.config, section_name)
        for key, value in section_data.items():
          if hasattr(section_obj, key):
            setattr(section_obj, key, value)

  def update_from_dataclass(self):
    new_dict = asdict(self.config)
    self._deep_update(self.config_dict, new_dict)

  def diff(self) -> dict:
    new_dict = asdict(self.config)
    diff = {}
    for section, new_vals in new_dict.items():
      old_vals = self.config_dict.get(section, {})
      section_diff = {}
      for key, new_val in new_vals.items():
        old_val = old_vals.get(key)
        if new_val != old_val:
          section_diff[key] = {"old": old_val, "new": new_val}
      if section_diff:
        diff[section] = section_diff
    return diff

  def write_local(self):
    lines = []
    for section, content in self.config_dict.items():
      lines.append(f"[{section}]")
      for key, value in content.items():
        if isinstance(value, list):
          val_str = "[ " + ", ".join(str(item) for item in value) + " ]"
        elif isinstance(value, bool):
          val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
          val_str = str(value)
        elif isinstance(value, datetime):
          val_str = value.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
          val_str = f'"{value}"'
        lines.append(f"{key} = {val_str}")
      lines.append("")  # blank line between sections
    with open(self.local_path, "w") as f:
      f.write("\n".join(lines))
