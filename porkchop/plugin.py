"""
porkchop.plugin
~~~~~~~~~~~~~~~

:copyright: (c) 2011-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from collections import defaultdict
import glob
import os
import sys
import socket
import time

import porkchop.plugins
from porkchop.util import PorkchopUtil


class InfiniteDict(defaultdict):
    def __init__(self, type=None, *args, **kwargs):
        super(InfiniteDict, self).__init__(type or self.__class__)


class PorkchopPlugin(object):
    config_file = None
    __delta = None
    __prev = None
    __cache = None
    __data = {}
    __lastrefresh = 0

    def __init__(self):
        self.refresh = 60
        self.force_refresh = False

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

    def gendict(self):
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


class PorkchopPluginHandler(object):
    plugins = {}

    def __init__(self, config_dir, directory=None):
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
                mod = sys.modules[astr]
                return mod
            except ImportError:
                module, _, basename = astr.rpartition('.')
            if module:
                mod = self.str_to_obj(module)
                return getattr(mod, basename)
            else:
                raise
