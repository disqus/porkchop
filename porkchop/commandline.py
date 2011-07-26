from BaseHTTPServer import HTTPServer
from optparse import OptionParser
from server import GetHandler

from porkchop.plugin import PorkchopPluginHandler

def main():
  plugin_dir = '/usr/share/porkchop/plugins'
  listen_address = ''
  listen_port = 5000

  parser = OptionParser()
  parser.add_option('-d', dest='plugindir',
                    default=plugin_dir,
                    help='Load plugins from DIR (default: %s)' % plugin_dir,
                    metavar='DIR')
  parser.add_option('-s', dest='listen_address',
                    default=listen_address,
                    help='Bind to ADDRESS', metavar='ADDRESS')
  parser.add_option('-p', type="int", dest='listen_port',
                    default=listen_port,
                    help='Bind to PORT (default: %d)' % listen_port,
                    metavar='PORT')

  (options, args) = parser.parse_args()

  PorkchopPluginHandler(options.plugindir)
  server = HTTPServer((options.listen_address, options.listen_port),
    GetHandler)
  server.serve_forever()
