import re
from subprocess import Popen, PIPE

from porkchop import PorkchopPlugin

class FacterPlugin(PorkchopPlugin):
  def get_data(self):
    d1 = {}
    r1 = re.compile('(.*?)\s=>\s(.*)')

    output = Popen(['facter'], stdout=PIPE, shell=True).communicate()[0]
    for line in output.split('\n'):
      match = r1.match(line)
      if match:
        d1[match.group(1)] = match.group(2)

    return d1
