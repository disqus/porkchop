from collections import defaultdict
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
from SocketServer import ThreadingMixIn
import sys
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
        if type(val) in [dict, defaultdict] :
          path_helper(val, '/'.join((path, key)), results)
        else:
          results.append(('%s %s' % (('/'.join((path, key)))\
            .replace('.','_'), val)))

    path_helper(data, '', results)
    return results

  def do_GET(self):
    data = {}
    formats = {'json': 'application/json', 'text': 'text/plain'}
    request = urlparse.urlparse(self.path)

    try:
      (path, fmt) = request.path.split('.')
      if fmt not in formats.keys(): fmt = 'text'
    except ValueError:
      path = request.path
      try:
        if self.headers['accept'] == 'application/json':
          fmt = 'json'
        else:
          fmt = 'text'
      except KeyError:
        fmt = 'text'

    module = path.split('/')[1]

    try:
      if module:
        plugin = PorkchopPluginHandler.plugins[module]()
        self.log_message('Calling plugin: %s' % module)
        data.update({module: plugin.data})
      else:
        for plugin_name, plugin in PorkchopPluginHandler.plugins.iteritems():
          try:
            self.log_message('Calling plugin: %s' % plugin_name)
            data.update({plugin_name: plugin().data})
          except:
            self.log_error('Error loading plugin: name=%s exception=%s', plugin_name, sys.exc_info())

      if len(data):
        self.send_response(200)
        self.send_header('Content-Type', formats[fmt])
        self.end_headers()
        self.wfile.write(self.format_output(fmt, data) + '\n')
      else:
        raise Exception('Unable to load any plugins')
    except:
      self.log_error('Error: %s', sys.exc_info())
      self.send_response(404)
      self.send_header('Content-Type', formats[fmt])
      self.end_headers()
      self.wfile.write(self.format_output(fmt, {}))

    return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """ do stuff """
