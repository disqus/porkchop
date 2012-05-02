"""
porkchop.util
~~~~~~~~~~~~~

:copyright: (c) 2011-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
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


    @classmethod
    def char_filter(cls, s):
        import string

        wanted = string.letters + string.digits + string.punctuation
        return "".join(c for c in s if c in wanted and not c == '.')
