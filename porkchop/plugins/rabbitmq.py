from subprocess import Popen, PIPE
from porkchop.plugin import PorkchopPlugin


class RabbitmqPlugin(PorkchopPlugin):
  def get_vhosts(self):
    return Popen(
      "/usr/sbin/rabbitmqctl list_vhosts",
      stdout=PIPE,
      shell=True
    ).communicate()[0]\
     .strip()\
     .split('\n')[1:-1]

  def get_queues(self, vhost):
    raw_queues = Popen(
      "/usr/sbin/rabbitmqctl list_queues -p %s" % vhost,
      stdout=PIPE,
      shell=True
    ).communicate()[0]\
     .strip()\
     .split('\n')[1:-1]

    queues = {}
    for line in raw_queues:
      try:
        queue, size = line.rsplit('\t', 1)
      except:
        pass
      else:
        queues[queue] = int(size)

    return queues

  def get_data(self):
    output = {}

    vhosts = self.get_vhosts()
    for vhost in vhosts:
      queues = self.get_queues(vhost)
      if vhost == '/':
        vhost = 'default'
      if queues:
        output[vhost] = queues

    return {'vhost': output}
