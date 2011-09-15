import glob
import os
from subprocess import Popen, PIPE
from porkchop.plugin import PorkchopPlugin

class RunitPlugin(PorkchopPlugin):
  def service_status(self, service):
    return Popen('/usr/bin/sv status %s' % service, stdout=PIPE,
      shell=True).communicate()[0].strip()

  def get_data(self):
    d1 = {}

    service_dirs = glob.glob('/etc/sv/*')
    for dir in service_dirs:
      service = os.path.basename(dir)
      d1[service] = self.service_status(service)

    return d1
