"""
NthTimeDiff:  plugin which takes two time series
              and returns the time difference between the nth
              events in each series.
Note that nth=1 means taking the first event in time.
"""
import logging

from snewpdag.dag import Node

class NthTimeDiff(Node):
  def __init__(self, nth, **kwargs):
    self.nth = nth # input parameter, specifying which event to choose
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.t = [ 0.0, 0.0 ] # nth times for each source
    self.h = [ (), () ] # histories from each source
    super().__init__(**kwargs)
    if self.nth < 1:
      logging.error('[{}] Invalid event index {}, changed to 1'.format(
                    self.name, self.nth))
      self.nth = 1

  def update(self, data):
    action = data['action']
    source = data['history'][-1]

    # figure out which source updated
    index = self.watch_index(source)
    if index < 0:
      logging.error("[{}] Unrecognized source {}".format(self.name, source))
      return
    if index >= 2:
      logging.error("[{}] Excess source {} detected".format(self.name, source))
      return

    # update the relevant data.
    # Only issue a downstream revocation if the source revocation
    # is new, i.e., the data was valid before.
    newrevoke = False
    if action == 'alert':
      self.valid[index] = True
      self.t[index] = self.get_nth(data['times'])
      self.h[index] = data['history']
    elif action == 'revoke':
      newrevoke = self.valid[index]
      self.valid[index] = False
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return

    # do the calculation if we have two valid inputs.
    if self.valid == [ True, True ]:
      ndata = { 'action': 'alert',
                'history': ( self.h[0], self.h[1] ),
                'dt': self.t[0] - self.t[1] }
      self.notify(ndata)
    elif newrevoke:
      ndata = { 'action': 'revoke',
                'history': ( self.h[0], self.h[1] ) }
      self.notify(ndata)

  def get_nth(self, values):
    """
    get nth smallest value in the list of values.
    note that smallest is nth=1
    """
    lowest = [ values[i] for i in range(self.nth) ]
    current = max(lowest)
    for i in range(self.nth, len(values)):
      v = values[i]
      if v < current:
        lowest.remove(current)
        lowest.append(v)
        current = max(lowest)
    return current
