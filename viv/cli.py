import sys, os
from dataclasses import dataclass, field, fields
from typing import List
import tomlkit
from .tcl import TCL

commands = {}

@dataclass
class Config:
  top_module: str = "top"
  sources: List[str] = field(default_factory=list)
  constraints: List[str] = field(default_factory=list)
  tcl_dir: str = "./tcl-scripts/"
  log_dir: str = "./log/"

def load_toml(path="viv.toml"):
  if not os.path.exists(path):
    raise FileNotFoundError(f"no config file found at {path}")
  with open(path, "r") as f:
    return tomlkit.parse(f.read())

def save_toml(data: dict, path="viv.toml"):
  with open(path, "w") as f:
    f.write(tomlkit.dumps(data))

def config_from_file(path="viv.toml") -> Config:
  doc = load_toml(path)
  cfg_dict = {}
  for f in fields(Config):
    # if the field name is present in the top-level doc, use it
    if f.name in doc:
      cfg_dict[f.name] = doc[f.name]
  return Config(**cfg_dict)

def write_new_config(path="viv.toml", project_name="myproj", board_name=""):
  doc = tomlkit.document()
  doc["project_name"] = project_name
  doc["board_name"] = board_name
  # set defaults from Config
  doc["top_module"] = "top"
  doc["sources"] = ["src/top.v"]
  doc["constraints"] = []
  doc["tcl_dir"] = "./tcl-scripts/"
  doc["log_dir"] = "./log/"
  save_toml(doc, path)

def parse_min_args(args: List[str], valid_keys):
  # e.g. parse like: --key=val
  results = {}
  for arg in args:
    if arg.startswith("--") and "=" in arg:
      k, v = arg[2:].split("=", 1)
      if k in valid_keys:
        results[k] = v
  return results

def command(name):
  def register(fn):
    commands[name] = fn
    return fn
  return register

@command("new")
def cmd_new(args: List[str], config: Config):
  # parse minimal args: --project_name=..., --board=...
  opts = parse_min_args(args, ["project_name","board"])
  project_name = opts.get("project_name", "myproj")
  board = opts.get("board", "")
  if os.path.exists("viv.toml"):
    print("viv.toml already exists in this directory, bailing")
    return
  write_new_config("viv.toml", project_name, board)
  print(f"created viv.toml for project '{project_name}'")

@command("add")
def cmd_add(args: List[str], config: Config):
  # just an example
  if not args:
    print("usage: viv add <filename>")
    return
  new_sources = list(config.sources)
  new_sources.extend(args)
  doc = load_toml("viv.toml")
  doc["sources"] = new_sources
  save_toml(doc, "viv.toml")
  print("added sources:", args)

def print_help():
  print("valid commands:")
  print("  new --project_name=... [--board=...]  : initialize project + viv.toml")
  print("  add <filename>                         : add source file to config")
  # more usage details as needed

def cli_main():
  if len(sys.argv) < 2:
    print_help()
    return
  cmd, *args = sys.argv[1:]
  if cmd not in commands:
    print(f"unknown command: {cmd}")
    print_help()
    return
  if cmd == "new":
    # do not load existing viv.toml
    commands[cmd](args, None)
  else:
    # load config from existing viv.toml
    config = config_from_file("viv.toml")
    commands[cmd](args, config)
