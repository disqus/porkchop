from BaseHTTPServer import BaseHTTPRequestHandler
import json
import sys
import time
import types
import urlparse

from porkchop import PorkchopPluginHandler

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
        if type(val) == str:
          results.append(('%s %s' % ('/'.join((path, key)), val)))
        elif type(val) == dict:
          path_helper(val, '/'.join((path, key)), results)

    path_helper(data, '', results)
    return results

  def do_GET(self):
    data = {}
    data['time'] = '%d' % time.time()
    path = urlparse.urlparse(self.path)
    fmt = path.query

    module = path.path.split('/')[1]

    try:
      plugin = PorkchopPluginHandler.plugins[module]()
    except:
      print 'Could not load plugin: %s' % module, sys.exc_info()[0]

    self.send_response(200)
    self.end_headers()
    self.wfile.write(self.format_body(fmt, plugin.data))
    return
