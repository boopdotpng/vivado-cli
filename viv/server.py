import subprocess, threading, queue, time

class VivadoServer:
  def __init__(self, vivado_cmd="vivado -mode tcl -nolog -nojournal -notrace"):
    self.proc = subprocess.Popen(vivado_cmd.split(),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                bufsize=1,
                                text=True)
    self._q = queue.Queue()
    threading.Thread(target=self._reader, daemon=True).start()

  def _reader(self):
    for line in self.proc.stdout:
      self._q.put(line)

  def send(self, cmd: str):
    if not cmd.endswith("\n"): cmd += "\n"
    self.proc.stdin.write(cmd)
    self.proc.stdin.flush()

  def recv(self, timeout=5):
    out = []
    deadline = time.time() + timeout
    while time.time() < deadline:
      try:
        line = self._q.get(timeout=deadline - time.time())
        out.append(line)
        if line.strip().endswith("Vivado%"):
          break
      except queue.Empty:
        break
    return "".join(out)

  def exec(self, cmd: str):
    self.send(cmd)
    return self.recv()

  def close(self):
    self.exec("exit")
    self.proc.wait()

# example usage
if __name__ == "__main__":
  viv = VivadoServer()
  print(viv.exec("get_parts"))
  viv.close()
