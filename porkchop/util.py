import ConfigParser

class PorkchopUtil(object):
  @classmethod
  def parse_config(self, path):
    config = {}
    cp = ConfigParser.ConfigParser()
    cp.read(path)

    for s in cp.sections():
      config.setdefault(s, {})
      for o in cp.options(s):
        config[s][o] = cp.get(s, o)

    return config
