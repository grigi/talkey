'''
talkey test suite
'''
# pylint: disable=W0104
from os.path import isfile
from talkey.base import DETECTABLE_LANGS, TTSError
from talkey.plugins import *
from talkey.utils import check_executable, process_options, memoize

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

class CheckExecutableTest(unittest.TestCase):

    def test_check_executable_found(self):
        self.assertTrue(check_executable('file'))

    def test_check_executable_not_found(self):
        self.assertFalse(check_executable('aieaoauu_not-findable_lfsdauybqwer'))

class MemoizeTest(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    @memoize
    def up_counter(self, *args, **kwargs):
        self.counter += 1
        return self.counter

    def test_memoize_no_call(self):
        self.assertEqual(self.counter, 0)

    def test_memoize_call_blank(self):
        self.up_counter()
        self.assertEqual(self.counter, 1)
        self.up_counter()
        self.assertEqual(self.counter, 1)

    def test_memoize_call_params(self):
        self.up_counter()
        self.up_counter(1,2)
        self.assertEqual(self.counter, 2)
        self.up_counter(1,2)
        self.assertEqual(self.counter, 2)
        self.up_counter()
        self.assertEqual(self.counter, 2)

    def test_memoize_call_keywords(self):
        self.up_counter()
        self.up_counter(1,2)
        self.up_counter(1,2, word=3)
        self.assertEqual(self.counter, 3)
        self.up_counter(1,2, word=4)
        self.assertEqual(self.counter, 4)
        self.up_counter(1,2, word=3)
        self.assertEqual(self.counter, 4)
        self.up_counter(1,2)
        self.assertEqual(self.counter, 4)
        self.up_counter()
        self.assertEqual(self.counter, 4)

class ProcessOptionsTest(unittest.TestCase):

    def test_process_options_unknown_param(self):
        with self.assertRaisesRegexp(TTSError, 'Unknown options'):
            process_options({}, {'test': 'fail'}, TTSError)

    def test_process_options_bad_type(self):
        with self.assertRaisesRegexp(TTSError, 'Bad type: garbage'):
            process_options({'test': {'type': 'garbage'}}, {'test': 'fail'}, TTSError)

    def test_process_options_default_none(self):
        spec = {'test': {'type': 'str'}}
        ret = process_options(spec, {}, TTSError)
        self.assertEqual(ret, {'test': None})

    def test_process_options_default_provided(self):
        spec = {'test': {'type': 'str', 'default': 'moo'}}
        ret = process_options(spec, {}, TTSError)
        self.assertEqual(ret, {'test': 'moo'})

    def test_process_options_bool(self):
        spec = {'test': {'type': 'bool'}}
        ret = process_options(spec, {}, TTSError)
        self.assertEqual(ret, {'test': False})
        ret = process_options(spec, {'test': 'yEs'}, TTSError)
        self.assertEqual(ret, {'test': True})

    def test_process_options_int(self):
        spec = {'test': {'type': 'int', 'min': 5, 'max': 8}}
        with self.assertRaises(TypeError):
            process_options(spec, {}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Min is 5'):
            process_options(spec, {'test': 3}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Max is 8'):
            process_options(spec, {'test': 10}, TTSError)
        ret = process_options(spec, {'test': '6'}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': '6.2'}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': 6}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': 6.1}, TTSError)
        self.assertEqual(ret, {'test': 6})

    def test_process_options_int(self):
        spec = {'test': {'type': 'float', 'min': 5.2, 'max': 8.9}}
        with self.assertRaises(TypeError):
            process_options(spec, {}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Min is 5.2'):
            process_options(spec, {'test': 3}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Max is 8.9'):
            process_options(spec, {'test': 10}, TTSError)
        ret = process_options(spec, {'test': '6'}, TTSError)
        self.assertEqual(ret, {'test': 6.0})
        ret = process_options(spec, {'test': '6.2'}, TTSError)
        self.assertEqual(ret, {'test': 6.2})
        ret = process_options(spec, {'test': 6}, TTSError)
        self.assertEqual(ret, {'test': 6.0})
        ret = process_options(spec, {'test': 6.1}, TTSError)
        self.assertEqual(ret, {'test': 6.1})

    def test_process_options_enum(self):
        spec = {'test': {'type': 'enum', 'values': ['one', 'two', 'four']}}
        with self.assertRaisesRegexp(TTSError, 'Bad test value: None'):
            process_options(spec, {}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Bad test value: three'):
            process_options(spec, {'test': 'three'}, TTSError)
        ret = process_options(spec, {'test': 'two'}, TTSError)
        self.assertEqual(ret, {'test': 'two'})


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
        if not self.CLS:
            raise unittest.SkipTest()

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

