import glob, os, sys
import time

plugins = []

class Porkchop(object):
  def __init__(self):
    self.refresh = 5
    self.last_refresh = None

  def should_refresh(self):
    now = time.time()
    if self.last_refresh:
      if not time.time() - self.last_refresh >= self.refresh:
        return False
    else:
      return True

class PorkchopPluginLoader():
  def plugins(self, d):
    sys.path.insert(0, d)
    modules = []

    for infile in glob.glob(os.path.join(d, '*.py')):
      if not infile == '__init__.py':
        modules.append(__import__(os.path.splitext(os.path.split(infile)[1])[0]))

    return modules
