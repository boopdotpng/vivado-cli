import sys, os
from dataclasses import dataclass, fields
from typing import List
from .tcl import TCL
import tomli

commands = {}

@dataclass
class Config:
  top_module: str
  sources: str
  constraints: str
  tcl_dir: str = "./tcl-scripts/"
  log_dir: str = "./log/"

def load_config(path="viv.cfg"):
  cfg = {}
  if os.path.exists(path):
    with open(path) as f:
      for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
          continue
        if "=" not in line:
          continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
  return cfg

def config_from_file(path="viv.cfg") -> Config:
  raw = load_config(path)

  keys = {f.name for f in fields(Config)}
  filtered = {k:v for k,v in raw.items() if k in keys}
  return Config(**filtered)

def parse_min_args(args: List[str], valid):
  return {
    k: v 
    for arg in args
    if '=' in arg 
    for k,v in [arg[2:].split('=')]
    if k in valid
  } 

def command(name):
  def reg(fn):
    commands[name] = fn
    return fn
  return reg

@command("new")
def new(args: List[str], config: Config):
  # valid options for new
  parse_min_args(args, ["project_name", "board_name"])
  print(parse_min_args)
  
  name = input("enter project name: ")


@command("add")
def add(args: List[str], config: Config):
  pass

def print_help(): 
  print("valid options for viv:")
  helps = {
    "new": "intialize a new vivado project",
    "add": "add file to program"
  }
  for k in commands.keys(): print(k, helps[k], sep='  ')

def cli_main():
  if len(sys.argv) < 2:
    print_help()
    return
  cmd, *args = sys.argv[1:]
  if cmd not in commands:
    print(f"unknown command: {cmd}")
    print_help()
    return
  config = config_from_file()
  commands[cmd](args, config)
