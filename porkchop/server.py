"""
porkchop.server
~~~~~~~~~~~~~~~

:copyright: (c) 2011-2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import json
import traceback
import urlparse

from porkchop.plugin import PorkchopPluginHandler


class GetHandler(BaseHTTPRequestHandler):
    def format_output(self, fmt, data):
        if fmt == 'json':
            return json.dumps(data)
        else:
            return '\n'.join(self.json_path(data))

    def json_path(self, data):
        results = []

        def path_helper(data, path, results):
            for key, val in data.iteritems():
                if isinstance(val,  dict):
                    path_helper(val, '/'.join((path, key)), results)
                else:
                    results.append(('%s %s' % (('/'.join((path, key)))\
                           .replace('.', '_'), val)))

        path_helper(data, '', results)
        return results

    def do_GET(self):
        data = {}
        formats = {'json': 'application/json', 'text': 'text/plain'}
        request = urlparse.urlparse(self.path)

        try:
            (path, fmt) = request.path.split('.')
            if fmt not in formats.keys():
                fmt = 'text'
        except ValueError:
            path = request.path
            if self.headers.get('accept', False) == 'application/json':
                fmt = 'json'
            else:
                fmt = 'text'

        if self.headers.get('x-porkchop-refresh', False):
            force_refresh = True
        else:
            force_refresh = False

        module = path.split('/')[1]

        try:
            if module:
                plugin = PorkchopPluginHandler.plugins[module](self)
                plugin.force_refresh = force_refresh
                self.log_message('Calling plugin: %s with force=%s' % (module, force_refresh))
                data.update({module: plugin.data})
            else:
                for plugin_name, plugin in PorkchopPluginHandler.plugins.iteritems():
                    try:
                        plugin.force_refresh = force_refresh
                        self.log_message('Calling plugin: %s with force=%s' % (plugin_name, force_refresh))
                        # if the plugin has no data, it'll only have one key:
                        # refreshtime
                        result = plugin(self).data
                        if len(result) > 1:
                            data.update({plugin_name: result})
                    except Exception, e:
                        self.log_error('Error loading plugin: name=%s exception=%s, traceback=%s', plugin_name, e,
                                       traceback.format_exc())

            if len(data):
                self.send_response(200)
                self.send_header('Content-Type', formats[fmt])
                self.end_headers()
                self.wfile.write(self.format_output(fmt, data) + '\n')
            else:
                raise Exception('Unable to load any plugins')
        except Exception, e:
            self.log_error('Error: %s\n%s', e, traceback.format_exc())
            self.send_response(404)
            self.send_header('Content-Type', formats[fmt])
            self.end_headers()
            self.wfile.write(self.format_output(fmt, {}))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
