from porkchop import PorkchopPlugin

class ThingPlugin(PorkchopPlugin):
  def data(self):
    return {'fred': 'wilma', 'barney': 'betty'}
