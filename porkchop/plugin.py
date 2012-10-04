"""
porkchop.plugin
~~~~~~~~~~~~~~~

:copyright: (c) 2011-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from collections import defaultdict
import glob
import imp
import inspect
import os
import sys
import socket
import time

from porkchop.util import PorkchopUtil


class InfiniteDict(defaultdict):
    def __init__(self, type=None, *args, **kwargs):
        super(InfiniteDict, self).__init__(type or self.__class__)


class DotDict(defaultdict):
    def __init__(self):
        defaultdict.__init__(self, DotDict)
    def __setitem__(self, key, value):
        keys = key.split('.')
        for key in keys[:-1]:
            self = self[key]
        defaultdict.__setitem__(self, keys[-1], value)


class PorkchopPlugin(object):
    config_file = None
    __delta = None
    __prev = None
    __cache = None
    __data = {}
    __lastrefresh = 0
    refresh = 60
    force_refresh = False

    def __init__(self, handler):
        self.handler = handler

    @property
    def data(self):
        if self.should_refresh():
            self.config = PorkchopUtil.parse_config(self.config_file)
            if self.prev_data is None:
                self.__class__.__delta = 1
                self.prev_data = self.get_data()
                time.sleep(1)
            else:
                self.prev_data = self.__class__.__data
            self.data = self.get_data()

        result = self.format_data(self.__class__.__data)
        if not result:
            return result
        result['refreshtime'] = self.__class__.__lastrefresh
        return result

    @data.setter
    def data(self, value):
        now = time.time()
        self.__class__.__data = value
        self.__class__.__delta = int(now - self.__class__.__lastrefresh)
        self.__class__.__lastrefresh = now
        self.force_refresh = False

    @property
    def delta(self):
        return self.__class__.__delta

    @property
    def prev_data(self):
        return self.__class__.__prev

    @prev_data.setter
    def prev_data(self, value):
        self.__class__.__prev = value

    def format_data(self, data):
        return data

    def gendict(self, type='infinite'):
        if type.lower() == 'dot':
            return DotDict()
        return InfiniteDict()

    def rateof(self, a, b, ival=None):
        if ival is None:
            ival = self.delta

        a = float(a)
        b = float(b)

        try:
            return (b - a) / ival if (b - a) != 0 else 0
        except ZeroDivisionError:
            if a:
                return -a
            return b

    def should_refresh(self):
        if self.force_refresh:
            return True

        if self.__class__.__lastrefresh != 0:
            return time.time() - self.__class__.__lastrefresh > self.refresh
        return True

    def tcp_socket(self, host, port):
        sock = socket.socket()
        sock.connect((host, port))

        return sock

    def unix_socket(self, path):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path)

        return sock

    def log_error(self, *args, **kwargs):
        return self.handler.log_error(*args, **kwargs)


class PorkchopPluginHandler(object):
    plugins = {}

    def __init__(self, config_dir, directory=None):
        self.config_dir = config_dir
        self.config = PorkchopUtil.parse_config(os.path.join(self.config_dir,
            'porkchop.ini'))

        if directory:
            self.__class__.plugins.update(self.load_plugins(directory))

        self.__class__.plugins.update(
            self.load_plugins(
                os.path.join(os.path.dirname(__file__), 'plugins')
            )
        )

    def load_plugins(self, directory):
        plugins = {}
        sys.path.insert(0, directory)

        try:
            to_load = [p.strip() for p in self.config['porkchop']['plugins'].split(',')]
        except:
            to_load = []

        for infile in glob.glob(os.path.join(directory, '*.py')):
            module_name = os.path.splitext(os.path.split(infile)[1])[0]

            if os.path.basename(infile) == '__init__.py':
                continue
            if to_load and module_name not in to_load:
                continue

            try:
                module = imp.load_source(module_name, infile)
                for namek, klass in inspect.getmembers(module):
                    if inspect.isclass(klass) \
                       and issubclass(klass, PorkchopPlugin) \
                       and klass is not PorkchopPlugin:

                        if hasattr(klass, '__metric_name__'):
                            plugin_name = klass.__metric_name__
                        else:
                            plugin_name = module_name

                        plugins[plugin_name] = klass
                        plugins[plugin_name].config_file = os.path.join(
                            self.config_dir,
                            '%s.ini' % plugin_name
                        )

                        # Only one plugin per module.
                        break

            except ImportError:
                print 'Unable to load plugin %r' % infile
                import traceback
                traceback.print_exc()

        return plugins
