import __builtin__
import glob, os, sys

class PorkchopPluginLoader():
  def plugins(self, dir):
    sys.path.insert(0, dir)
    modules = []

    for infile in glob.glob(os.path.join(dir, '*.py')):
      if not infile == '__init__.py':
        modules.append(__import__(os.path.splitext(os.path.split(infile)[1])[0]))

    return modules
