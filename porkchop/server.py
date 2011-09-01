from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
from SocketServer import ThreadingMixIn
import urlparse

from porkchop.plugin import PorkchopPluginHandler

class GetHandler(BaseHTTPRequestHandler):
  def format_body(self, fmt, data):
    if fmt == 'json':
      return json.dumps(data) + '\n'
    else:
      return '\n'.join(self.json_path(data)) + '\n'

  def json_path(self, data):
    results = []
    def path_helper(data, path, results):
      for key, val in data.iteritems():
        if type(val) == dict:
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
    except ValueError:
      path = request.path
      try:
        if self.headers['accept'] == 'application/json':
          fmt = 'json'
        elif self.headers['accept'] in ['text/plain', '*/*']:
          fmt = 'text'
      except KeyError:
        fmt = 'text'

    module = path.split('/')[1]

    try:
      self.send_response(200)
      self.send_header('Content-Type', formats[fmt])
      self.end_headers()
      if module:
        plugin = PorkchopPluginHandler.plugins[module]()
        self.wfile.write(self.format_body(fmt, {module: plugin.data}))
      else:
        for plugin_name, plugin in PorkchopPluginHandler.plugins.iteritems():
          self.wfile.write(self.format_body(fmt, {plugin_name: plugin().data}))
    except:
      self.send_response(404)
      self.send_header('Content-Type', formats[fmt])
      self.end_headers()
      self.wfile.write(self.format_body(fmt, {}))

    return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """ do stuff """
