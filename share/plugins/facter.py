from porkchop import Porkchop
import re
import subprocess

class FacterPlugin(Porkchop):
  def data(self):
    d1 = {}
    p = re.compile('(.*?)\s=>\s(.*)')

    output = subprocess.check_output(['facter'])
    for line in output.split('\n'):
      match = p.match(line)
      if match:
        d1[match.group(1)] = match.group(2)

    return d1
