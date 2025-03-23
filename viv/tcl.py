import subprocess, shutil, os, xml.etree.ElementTree as ET

def find_vivado_root():
  vivado_path = shutil.which("vivado")
  if not vivado_path:
    raise RuntimeError("vivado not found in PATH")
  vivado_bin = os.path.dirname(vivado_path)
  root = os.path.abspath(os.path.join(vivado_bin, ".."))
  if not os.path.exists(os.path.join(root, "data", "boards", "board_files")):
    raise RuntimeError("vivado install root not found near vivado executable")
  return root

class TCL:
  vivado_root = find_vivado_root()

  @staticmethod
  def get_installed_boards():
    board_dir = os.path.join(TCL.vivado_root, "data", "boards", "board_files")
    board_map = {}
    for folder_name in os.listdir(board_dir):
      board_path = os.path.join(board_dir, folder_name)
      if not os.path.isdir(board_path):
        continue
      for rootdir, dirs, files in os.walk(board_path):
        if "board.xml" in files:
          xml_path = os.path.join(rootdir, "board.xml")
          try:
            tree = ET.parse(xml_path)
            board = tree.getroot()
            vendor = board.get("vendor") or "unknown_vendor"
            board_name = board.get("name") or folder_name

            version_elem = board.find("file_version")
            version = version_elem.text.strip() if version_elem is not None else "1.0"

            rev_elem = board.find(".//revision")
            revision = rev_elem.text.strip() if rev_elem is not None else "1.0"

            part0 = board.find(".//component[@name='part0']")
            fpga_part = part0.get("part_name") if part0 is not None else None

            board_part = f"{vendor}:{board_name}:part0:{revision}:{version}"

            board_map[board_name] = {
              "board_part": board_part,
              "fpga_part": fpga_part,
              "board": board_name
            }
            break
          except Exception as e:
            pass
    return board_map
