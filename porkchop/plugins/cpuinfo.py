import re

from porkchop.plugin import PorkchopPlugin

class CpuinfoPlugin(PorkchopPlugin):
  def get_data(self):
    d1 = {}
    r1 = re.compile('(\w+)\s+:\s+(\w+)')
    f = open('/proc/cpuinfo', 'r')

    for line in f:
      match = r1.match(line)
      if match:
        k = match.group(1)
        v = match.group(2)
      if k == 'processor':
        proc = v
        d1['processor%s' % proc] = {}
      else:
        d1['processor%s' % proc].update({k: v})

    return d1
