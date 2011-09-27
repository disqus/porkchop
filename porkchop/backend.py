import socket
import struct
import time
import cPickle

class Carbon(object):
  def __init__(self, host, port, logger):
    self.data = {}
    self.host = host
    self.port = port
    self.logger = logger
    try:
      self.sock = self._connect()
    except socket.error:
      self.logger.fatal('Unable to connect to carbon.')

  def _connect(self, waittime=5):
    self.logger.info('Connecting to carbon on %s:%d', self.host, self.port)
    try:
      sock = socket.socket()
      sock.connect((self.host, self.port))
    except socket.error:
      self.logger.info('Unable to connect to carbon, retrying in %d seconds', waittime)
      time.sleep(waittime)
      self._connect(waittime + 5)

    return sock

  def _send(self, data):
    try:
      self.sock.sendall(self._serialize(data.items()))
    except socket.error:
      raise

  def _serialize(self, data):
    serialized = cPickle.dumps(data, protocol=-1)
    prefix = struct.pack('!L', len(serialized))
    return prefix + serialized

  def send(self):
    """ self.data format: {metric_name: [(t1, val1), (t2, val2)]} """
    buf_sz = 500
    to_send = {}

    for mn in self.data.keys():
      while len(self.data[mn]) > 0:
        l = len(to_send)
        if l < buf_sz:
          to_send.setdefault(mn, [])
          to_send[mn].append(self.data[mn].pop())
        else:
          try:
            self._send(to_send)
            to_send = {}
            to_send.setdefault(mn, [])
            to_send[mn].append(self.data[mn].pop())
          except socket.error:
            self.logger.error('Error sending to carbon, trying to reconnect.')
            self.sock = self._connect()

            # we failed to send, so put it back in the stack and try later
            for ent in to_send:
              self.data[ent[0]].append(ent[1])

    try:
      self._send(to_send)
    except socket.error:
      self.logger.error('Error sending to carbon, trying to reconnect.')
      self.sock = self._connect()

      # we failed to send, so put it back in the stack and try later
      for ent in to_send:
        self.data[ent[0]].append(ent[1])
