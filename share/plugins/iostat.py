import re
from subprocess import Popen, PIPE

from porkchop.plugin import PorkchopPlugin

class IostatPlugin(PorkchopPlugin):
  def get_data(self):
    command = 'iostat -x'
    cpu_keys = ['user', 'nice', 'system', 'iowait', 'steal', 'idle']
    d1 = {}
    disk_keys = [
      'rrqm',
      'wrqm',
      'read',
      'write',
      'rsec',
      'wsec',
      'avgrq-sz',
      'avgqu-sz',
      'await',
      'svctm',
      'util'
    ]

    output = Popen([command], stdout=PIPE, shell=True).communicate()[0].split('\n')

    cpu_line = re.findall(r'[^\s]+', output[3])
    d1['cpu'] = {}
    for pos in xrange(len(cpu_keys)):
      d1['cpu'].update({cpu_keys[pos]: cpu_line[pos]})

    for stat_line in output[6:]:
      if not stat_line: continue

      device_stats = re.findall(r'[^\s]+', stat_line)
      d1.setdefault(device_stats[0], {})

      for pos in xrange(len(disk_keys)):
        d1[device_stats[0]].update({disk_keys[pos]: device_stats[pos+1]})

    return d1
