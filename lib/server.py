from BaseHTTPServer import BaseHTTPRequestHandler
import json
import sys
import time
import types
import urlparse

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
    class_name = '%sPlugin' % module.capitalize()

    try:
      loader = self.str_to_class(module, class_name)()

      if loader.should_refresh():
        data[module] = loader.data()
      else:
        data = {}
    except:
      print 'failed to load class for %s' % class_name
      data = {}

    self.send_response(200)
    self.end_headers()
    self.wfile.write(self.format_body(fmt, data))
    return

  def str_to_class(self, module, klass):
    try:
      identifier = getattr(sys.modules[module], klass)
    except AttributeError:
      raise NameError("%s doesn't exist." % klass)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
      return identifier
    raise TypeError("%s is not a class." % klass)
