import glob, os, sys
import time

import porkchop.plugins

class PorkchopPlugin(object):
  config_file = None
  _cache = None
  _data = {}
  _lastrefresh = 0

  def __init__(self):
    self.refresh = 60

  def get_config(self):
    import ConfigParser

    config = {}
    cp = ConfigParser.ConfigParser()
    cp.read(self.config_file)
    for s in cp.sections():
      config.setdefault(s, {})
      for o in cp.options(s):
        config[s][o] = cp.get(s, o)

    return config

  @property
  def data(self):
    if self.should_refresh():
      self.config = self.get_config()
      self.data = self.get_data()

    return self.__class__._data

  @data.setter
  def data(self, value):
    self.__class__._data = value
    self.__class__._lastrefresh = time.time()
    self.__class__._data['refreshtime'] = int(self.__class__._lastrefresh)

  def should_refresh(self):
    if self.__class__._lastrefresh != 0:
      if time.time() - self.__class__._lastrefresh > self.refresh:
        return True
      else:
        return False
    else:
      return True

class PorkchopPluginHandler(object):
  plugins = {}

  def __init__(self, config_dir, directory = None):
    self.config_dir = config_dir

    if directory:
      self.__class__.plugins.update(self.load_plugins(directory))

    self.__class__.plugins.update(self.load_plugins(os.path.dirname(porkchop.plugins.__file__)))

  def load_plugins(self, directory):
    plugins = {}
    sys.path.insert(0, directory)

    for infile in glob.glob(os.path.join(directory, '*.py')):
      if not os.path.basename(infile) == '__init__.py':
        module_name = os.path.splitext(os.path.split(infile)[1])[0]
        plugins[module_name] = self.str_to_obj('%s.%sPlugin' % (module_name,
          module_name.capitalize()))
        plugins[module_name].config_file = os.path.join(self.config_dir,
          '%s.ini' % module_name)

    return plugins

  def str_to_obj(self, astr):
    try:
      return globals()[astr]
    except KeyError:
      try:
        __import__(astr)
        mod=sys.modules[astr]
        return mod
      except ImportError:
        module,_,basename=astr.rpartition('.')
        if module:
          mod=self.str_to_obj(module)
          return getattr(mod,basename)
        else:
          raise
