from porkchop import PorkchopPlugin

class ThingPlugin(PorkchopPlugin):
  def __init__(self):
    self.refresh = 5

  def get_data(self):
    return {'fred': 'wilma', 'barney': 'betty'}
