'''
This will check that a certain key/field exists in the payload,
and if not, consume the action.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_key() checks that the desired key/field exists in the payload

Input: data as payload + search_key
'''

import logging
from snewpdag.dag import Node

class ValidateKey(Node):
    def __init__(self, in_field, **kwargs):
        self.in_field = in_field
        self.on_alert = kwargs.pop('on_alert', None)
        self.on_reset = kwargs.pop('on_reset', None)
        self.on_revoke = kwargs.pop('on_revoke', None)
        self.on_report = kwargs.pop('on_report', None)
        super().__init__(**kwargs)
    
    def check_key(self, data): # check that the key exists
        if self.in_field in data:
            return True
        else:
            logging.error('Desired key [{}] not found in payload and action is consumed'.format(self.in_field))
            return False
    
    def alert(self, data):
        if self.on_alert:
            return self.check_key(data)
        else:
            return False
    
    def revoke(self, data):
        if self.on_revoke:
            return self.check_key(data)
        else:
            return False

    def reset(self, data):
        if self.on_reset:
            return self.check_key(data)
        else:
            return False

    def report(self, data):
        if self.on_report:
            return self.check_key(data)
        else:
            return False