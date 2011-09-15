import json
import urllib2
from porkchop.plugin import PorkchopPlugin


num_keys = [
  "executing_mappers",
  "mem_allocated",
  "mem_total",
  "node_get_fsm_time_100",
  "node_get_fsm_time_95",
  "node_get_fsm_time_99",
  "node_get_fsm_time_mean",
  "node_get_fsm_time_median",
  "node_gets_total",
  "node_put_fsm_time_100",
  "node_put_fsm_time_95",
  "node_put_fsm_time_99",
  "node_put_fsm_time_mean",
  "node_put_fsm_time_median",
  "node_puts_total",
  "pbc_active",
  "pbc_connects_total",
  "read_repairs_total",
  "vnode_gets_total",
  "vnode_puts_total",
]

len_keys = ["connected_nodes"]

class RiakPlugin(PorkchopPlugin):
  def get_data(self):
    output = {}

    stats = json.loads(urllib2.urlopen("http://localhost:8098/stats").read())

    for key in num_keys:
      output[key] = stats[key]

    for len_key in len_keys:
      output[len_key] = len(stats[len_key])

    return output
