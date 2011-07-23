import glob, os, sys
import time

class PorkchopPlugin(object):
  def __init__(self):
    self.refresh = 60
    self.last_refresh = None

  def should_refresh(self):
    now = time.time()
    if self.last_refresh:
      if not time.time() - self.last_refresh >= self.refresh:
        return False
    else:
      return True

class PorkchopPluginHandler(object):
  plugins = []

  def __init__(self, directory = None):
    if directory:
      PorkchopPluginHandler.plugins = self.load_plugins(directory)

  def load_plugins(self, directory):
    sys.path.insert(0, directory)
    modules = []

    for infile in glob.glob(os.path.join(directory, '*.py')):
      if not os.path.basename(infile) == '__init__.py':
        print infile
        modules.append(__import__(os.path.splitext(os.path.split(infile)[1])[0]))

    return modules
