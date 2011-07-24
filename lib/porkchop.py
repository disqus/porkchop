import glob, os, sys
import time

class PorkchopPlugin(object):
  _lastrefresh = 0
  _data = {}

  def __init__(self):
    self.refresh = 60

  @property
  def data(self):
    if self.should_refresh():
      print 'Refreshing...'
      self.__class__._lastrefresh = time.time()
      self.data = self.get_data()

    return self.__class__._data

  @data.setter
  def data(self, value):
    self.__class__._data = value

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

  def __init__(self, directory = None):
    if directory:
      PorkchopPluginHandler.plugins = self.load_plugins(directory)

  def load_plugins(self, directory):
    plugins = {}
    sys.path.insert(0, directory)

    for infile in glob.glob(os.path.join(directory, '*.py')):
      if not os.path.basename(infile) == '__init__.py':
        module_name = os.path.splitext(os.path.split(infile)[1])[0]
        plugins[module_name] = self.str_to_obj('%s.%sPlugin' % (module_name,
          module_name.capitalize()))

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
