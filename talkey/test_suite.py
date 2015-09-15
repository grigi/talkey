'''
talkey test suite
'''
# pylint: disable=W0104
from talkey.base import DETECTABLE_LANGS, TTSError
from talkey.plugins import *

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest


class DummyTTSTest(unittest.TestCase):
    '''
    Tests talkey basic functionality
    '''
    CLS = DummyTTS
    SLUG = 'dummy-tts'
    INIT_ATTRS = ['enabled']
    CONF = {
        'enabled': True,
    }
    OBJ_ATTRS = []

    def test_instantiate_blank(self):
        cls = self.CLS
        self.assertEqual(cls.SLUG, self.SLUG)
        self.assertEqual(sorted(cls.get_init_options().keys()), sorted(self.INIT_ATTRS))
        obj = cls(**self.CONF)
        self.assertEqual(obj.SLUG, self.SLUG)
        self.assertEqual(obj.is_available(), True)
        self.assertEqual(sorted(obj.get_options().keys()), sorted(self.OBJ_ATTRS))
        language, voice, voiceinfo, options = obj.configure()
        self.assertEqual(language, 'en')
        self.assertIsNotNone(voice)
        self.assertEqual(voice, obj.get_languages()['en']['default'])
        self.assertEqual(sorted(options.keys()), sorted(self.OBJ_ATTRS))


class FestivalTTSTest(DummyTTSTest):
    CLS = FestivalTTS
    SLUG = 'festival-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = []

class FliteTTSTest(DummyTTSTest):
    CLS = FliteTTS
    SLUG = 'flite-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = []

class EspeakTTSTest(DummyTTSTest):
    CLS = EspeakTTS
    SLUG = 'espeak-tts'
    INIT_ATTRS = []
    CONF = {}
    OBJ_ATTRS = ['words_per_minute', 'pitch_adjustment', 'variant']

