'''
talkey test suite
'''
# pylint: disable=W0104
from os.path import isfile
from talkey.base import DETECTABLE_LANGS, TTSError
from talkey.plugins import *

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

LAST_PLAY = None

# Patch AbstractTTSEngine.play to record its params
from talkey.base import AbstractTTSEngine, subprocess
def fakeplay(self, filename):
    global LAST_PLAY
    output = subprocess.check_output(['file', filename], universal_newlines=True)
    LAST_PLAY = (self, filename, output)
AbstractTTSEngine.play = fakeplay

class BaseTTSTest(unittest.TestCase):
    '''
    Tests talkey basic functionality
    '''
    CLS = None
    SLUG = None
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = []
    EVAL_PLAY = True

    @classmethod
    def setUpClass(cls):
        if not cls.CLS:
            raise unittest.SkipTest()

    def setUp(self):
        global LAST_PLAY
        LAST_PLAY = None

    def test_class_init_options(self):
        cls = self.CLS
        self.assertEqual(cls.SLUG, self.SLUG)
        self.assertEqual(sorted(cls.get_init_options().keys()), sorted(self.INIT_ATTRS))

    def test_class_instantiation(self):
        obj = self.CLS(**self.CONF)
        self.assertEqual(obj.SLUG, self.SLUG)
        self.assertEqual(obj.is_available(), True)
        self.assertEqual(sorted(obj.get_options().keys()), sorted(self.OBJ_ATTRS))

    def test_class_configure(self):
        obj = self.CLS(**self.CONF)
        language, voice, voiceinfo, options = obj.configure()
        self.assertEqual(language, 'en')
        self.assertIsNotNone(voice)
        self.assertEqual(voice, obj.get_languages()['en']['default'])
        self.assertEqual(sorted(options.keys()), sorted(self.OBJ_ATTRS))

    def test_class_say(self):
        obj = self.CLS(**self.CONF)
        obj.say('Cows go moo')
        if self.EVAL_PLAY:
            inst, filename, output = LAST_PLAY
            self.assertIn('WAVE audio', output)
            self.assertEqual(inst, obj)
            self.assertFalse(isfile(filename), 'Tempfile not deleted')


class DummyTTSTest(BaseTTSTest):
    CLS = DummyTTS
    SLUG = 'dummy-tts'
    INIT_ATTRS = ['enabled']
    CONF = {
        'enabled': True,
    }
    OBJ_ATTRS = []
    EVAL_PLAY = False


class FestivalTTSTest(BaseTTSTest):
    CLS = FestivalTTS
    SLUG = 'festival-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = []
    EVAL_PLAY = True


class FliteTTSTest(BaseTTSTest):
    CLS = FliteTTS
    SLUG = 'flite-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = []
    EVAL_PLAY = True


class EspeakTTSTest(BaseTTSTest):
    CLS = EspeakTTS
    SLUG = 'espeak-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = ['words_per_minute', 'pitch_adjustment', 'variant']
    EVAL_PLAY = True

