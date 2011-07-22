from porkchop import Porkchop

class ThingPlugin(Porkchop):
  def data(self):
    return {'fred': 'wilma', 'barney': 'betty'}
