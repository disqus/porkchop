import socket
import struct
import cPickle

class Carbon(object):
  def __init__(self, host, port, logger):
    self.data = []
    self.host = host
    self.port = port
    self.logger = logger
    try:
      self.sock = self._connect()
    except socket.error:
      self.logger.fatal('Unable to connect to carbon.')

  def _connect(self):
    self.logger.info('Connecting to carbon on %s:%d', self.host, self.port)
    sock.connect((self.host, self.port))

    return sock

  def _send(self, data):
    self.logger.info('Sending %d metrics to carbon.', len(data))
    self.sock.sendall(self.serialize(data))

  def _serialize(data):
    serialized = cPickle.dumps(data, protocol=-1)
    prefix = struct.pack('!L', len(serialized))
    return prefix + serialized

  def send(self):
    """ self.data format: {metric_name: [(t1, val1), (t2, val2)]} """
    buf_sz = 500
    to_send = []

    for mn in self.data.keys():
      for datapoint in self.data[mn]:
        l = len(to_send)
        if l < buf_sz:
          to_send.append((mn, self.data[mn].pop()))
        else:
          try:
            self._send(to_send)
            to_send = []
            to_send.append((mn, self.data[mn].pop()))
          except socket.error:
            self.logger.error('Error sending to carbon, trying to reconnect.')
            self.sock = self._connect()

            # we failed to send, so put it back in the stack and try later
            for ent in to_send:
              self.data[ent[0]].append(ent[1])
