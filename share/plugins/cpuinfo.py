from porkchop import Porkchop
import re

class CpuinfoPlugin(Porkchop):
  def data(self):
    d1 = {}
    p = re.compile('(\w+)\s+:\s+(\w+)')
    f = open('/proc/cpuinfo', 'r')

    for line in f:
      match = p.match(line)
      if match:
        k = match.group(1)
        v = match.group(2)
      if k == 'processor':
        proc = v
        d1['processor%s' % proc] = {}
      else:
        d1['processor%s' % proc].update({k: v})

    return d1
