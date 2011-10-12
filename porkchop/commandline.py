import logging
import socket
from optparse import OptionParser

from porkchop.plugin import PorkchopPluginHandler

def coerce_number(s):
  try:
    return int(s)
  except:
    return float(s)

def get_logger(name, level=logging.INFO):
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  ch = logging.StreamHandler()
  ch.setLevel(level)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  return logger

def main():
  from server import GetHandler
  from porkchop.server import GetHandler, ThreadedHTTPServer
  config_dir = '/etc/porkchop.d'
  plugin_dir = '/usr/share/porkchop/plugins'
  listen_address = ''
  listen_port = 5000

  parser = OptionParser()
  parser.add_option('-c', dest='config_dir',
                    default=config_dir,
                    help='Load configs from DIR (default: %s)' % config_dir,
                    metavar='DIR')
  parser.add_option('-d', dest='plugin_dir',
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

  PorkchopPluginHandler(options.config_dir, options.plugin_dir)
  server = ThreadedHTTPServer((options.listen_address, options.listen_port),
                              GetHandler)
  server.serve_forever()

def collector():
  import requests
  import sys
  import time

  from porkchop.backend import Carbon

  carbon_host = 'localhost'
  carbon_port = 2004
  data = {}
  porkchop_url = 'http://localhost:5000/'

  interval = 60
  prefix = 'porkchop.%s' % socket.gethostname().split('.')[0].replace('.','_')

  parser = OptionParser()
  parser.add_option('--carbon-host', dest='carbon_host',
                    default=carbon_host,
                    help='Connect to carbon on HOST (default: %s)' % carbon_host,
                    metavar='HOST')
  parser.add_option('--carbon-port', type='int', dest='carbon_port',
                    default=carbon_port,
                    help='Connect to carbon on PORT (default: %d)' % carbon_port,
                    metavar='PORT')
  parser.add_option('--porkchop-url', dest='porkchop_url',
                    default=porkchop_url,
                    help='Connect to porkchop on URL (default: %s)' % porkchop_url,
                    metavar='URL')
  parser.add_option('-i', type='int', dest='interval',
                    default=interval,
                    help='Fetch data at INTERVAL (default: %d)' % interval,
                    metavar='INTERVAL')
  parser.add_option('-n', dest='noop',
                    default=False,
                    help='Don\'t actually send to graphite',
                    action='store_true')
  parser.add_option('-P', dest='prefix',
                    default=prefix,
                    help='Graphite prefix (default: %s)' % prefix)
  parser.add_option('-v', dest='verbose',
                    default=False,
                    help='Verbose logging',
                    action='store_true')


  (options, args) = parser.parse_args()

  if options.verbose:
    logger = get_logger('porkchop-collector', logging.DEBUG)
  else:
    logger = get_logger('porkchop-collector')

  if not options.noop:
    carbon = Carbon(options.carbon_host, options.carbon_port, logger)

  while True:
    now = int(time.time())
    try:
      logger.debug('Fetching porkchop data from %s', options.porkchop_url)
      r = requests.get(options.porkchop_url, headers={'x-porkchop-refresh': 'true'})
      r.raise_for_status()
    except:
      logger.error('Got bad response code from porkchop: %s', sys.exc_info()[1])

    lines = []
    for line in r.content.strip('\n').splitlines():
      (key, val) = line.lstrip('/').split(' ', 1)
      key = '.'.join([options.prefix, key.replace('/', '.')])
      data.setdefault(key, [])

      try:
        data[key].append((now, coerce_number(val)))

        for met in data.keys():
          for datapoint in data[met]:
            logger.debug('Sending: %s %s %s', met, datapoint[0], datapoint[1])

        if not options.noop:
          carbon.data = data
          carbon.send()
      except:
        pass

    sleep_time = options.interval - (int(time.time()) - now)
    if sleep_time > 0:
      logger.info('Sleeping for %d seconds', sleep_time)
      time.sleep(sleep_time)
