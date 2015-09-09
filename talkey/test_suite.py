'''
talkey test suite
'''
# pylint: disable=W0104
import os
from configy import load_config, config
from .languages import DETECTABLE_LANGS

BASE_DIR = os.path.dirname(__file__)

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

# Load some default config
load_config(data={
    'Something': {
        'one': '1',
    },
})


class TalkeyBaiscTest(unittest.TestCase):
    '''
    Tests talkey basic functionality
    '''

        
