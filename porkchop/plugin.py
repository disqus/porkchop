from collections import defaultdict
import glob, os, sys
import socket
import time

import porkchop.plugins
from porkchop.util import PorkchopUtil

class PorkchopPlugin(object):
  config_file = None
  _cache = None
  _data = {}
  _lastrefresh = 0

  def __init__(self):
    self.refresh = 60
    self.force_refresh = False

  @property
  def data(self):
    if self.should_refresh():
      self.config = PorkchopUtil.parse_config(self.config_file)
      self.data = self.get_data()

    return self.__class__._data

  @data.setter
  def data(self, value):
    self.__class__._data = value
    self.__class__._lastrefresh = time.time()
    self.__class__._data['refreshtime'] = int(self.__class__._lastrefresh)
    self.force_refresh = False

  def gendict(self):
    return defaultdict(self.gendict)

  def rateof(self, a, b, ival):
    return (float(b) - float(a)) / ival if (float(b) - float(a)) > 0 else 0

  def should_refresh(self):
    if self.force_refresh:
      return True

    if self.__class__._lastrefresh != 0:
      if time.time() - self.__class__._lastrefresh > self.refresh:
        return True
      else:
        return False
    else:
      return True

  def tcp_socket(self, host, port):
    try:
      sock = socket.socket()
      sock.connect((host, port))
    except socket.error:
      raise

    return sock

  def unix_socket(self, path):
    try:
      sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      sock.connect(path)
    except socket.error:
      raise

    return sock

class PorkchopPluginHandler(object):
  plugins = {}

  def __init__(self, config_dir, directory = None):
    self.config_dir = config_dir
    self.config = PorkchopUtil.parse_config(os.path.join(self.config_dir,
      'porkchop.ini'))

    if directory:
      self.__class__.plugins.update(self.load_plugins(directory))

    self.__class__.plugins.update(self.load_plugins(os.path.dirname(porkchop.plugins.__file__)))

  def load_plugins(self, directory):
    plugins = {}
    sys.path.insert(0, directory)

    try:
      to_load = [p.strip() for p in self.config['porkchop']['plugins'].split(',')]
    except:
      to_load = []

    for infile in glob.glob(os.path.join(directory, '*.py')):
      module_name = os.path.splitext(os.path.split(infile)[1])[0]
      if os.path.basename(infile) != '__init__.py' and \
          (not to_load or module_name in to_load):
        try:
          plugins[module_name] = self.str_to_obj('%s.%sPlugin' % (module_name,
            module_name.capitalize()))
          plugins[module_name].config_file = os.path.join(self.config_dir,
            '%s.ini' % module_name)
        except ImportError:
          pass

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
