'''
talkey test suite
'''
# pylint: disable=W0104
from talkey.base import DETECTABLE_LANGS, TTSError, AbstractTTSEngine, subprocess
from talkey.engines import *
from talkey.utils import check_executable, process_options
from talkey.tts import create_engine, Talkey

from os.path import isfile

try:
    import unittest2 as unittest  # pylint: disable=F0401
except ImportError:
    import unittest

LAST_PLAY = None


# Patch AbstractTTSEngine.play to record its params
# Really need to make this loosely connected
def fakeplay(self, filename, translate=False):
    global LAST_PLAY
    output = subprocess.check_output(['file', filename], universal_newlines=True)
    LAST_PLAY = (self, filename, output)
AbstractTTSEngine.play = fakeplay


class CheckExecutableTest(unittest.TestCase):

    def test_check_executable_found(self):
        self.assertTrue(check_executable('file'))

    def test_check_executable_not_found(self):
        self.assertFalse(check_executable('aieaoauu_not-findable_lfsdauybqwer'))


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
        ret = process_options(spec, {'test': '6'}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': '6.2'}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': 6}, TTSError)
        self.assertEqual(ret, {'test': 6})
        ret = process_options(spec, {'test': 6.1}, TTSError)
        self.assertEqual(ret, {'test': 6})

    def test_process_options_int_min(self):
        with self.assertRaisesRegexp(TTSError, 'Min is 5'):
            process_options({'test': {'type': 'int', 'min': 5}}, {'test': 3}, TTSError)
        process_options({'test': {'type': 'int'}}, {'test': 3}, TTSError)

    def test_process_options_int_max(self):
        with self.assertRaisesRegexp(TTSError, 'Max is 8'):
            process_options({'test': {'type': 'int', 'max': 8}}, {'test': 10}, TTSError)
        process_options({'test': {'type': 'int'}}, {'test': 10}, TTSError)

    def test_process_options_float(self):
        spec = {'test': {'type': 'float', 'min': 5.2, 'max': 8.9}}
        with self.assertRaises(TypeError):
            process_options(spec, {}, TTSError)
        ret = process_options(spec, {'test': '6'}, TTSError)
        self.assertEqual(ret, {'test': 6.0})
        ret = process_options(spec, {'test': '6.2'}, TTSError)
        self.assertEqual(ret, {'test': 6.2})
        ret = process_options(spec, {'test': 6}, TTSError)
        self.assertEqual(ret, {'test': 6.0})
        ret = process_options(spec, {'test': 6.1}, TTSError)
        self.assertEqual(ret, {'test': 6.1})

    def test_process_options_float_min(self):
        with self.assertRaisesRegexp(TTSError, 'Min is 5.2'):
            process_options({'test': {'type': 'float', 'min': 5.2}}, {'test': 3}, TTSError)
        process_options({'test': {'type': 'float'}}, {'test': 3}, TTSError)

    def test_process_options_float_max(self):
        with self.assertRaisesRegexp(TTSError, 'Max is 8.9'):
            process_options({'test': {'type': 'float', 'max': 8.9}}, {'test': 10}, TTSError)
        process_options({'test': {'type': 'float'}}, {'test': 10}, TTSError)

    def test_process_options_enum(self):
        spec = {'test': {'type': 'enum', 'values': ['one', 'two', 'four']}}
        with self.assertRaisesRegexp(TTSError, 'Bad test value: None'):
            process_options(spec, {}, TTSError)
        with self.assertRaisesRegexp(TTSError, 'Bad test value: three'):
            process_options(spec, {'test': 'three'}, TTSError)
        ret = process_options(spec, {'test': 'two'}, TTSError)
        self.assertEqual(ret, {'test': 'two'})


class CreateEngineTest(unittest.TestCase):

    def test_create_engine(self):
        eng = create_engine('dummy', options={'enabled': True})
        self.assertEqual(eng.SLUG, 'dummy')
        self.assertTrue(eng.available)
        assert eng.languages

    def test_create_engine_bad(self):
        with self.assertRaisesRegexp(TTSError, 'Unknown engine'):
            create_engine('baddy')


class TalkeyTest(unittest.TestCase):
    TXTS = [
        # Actual, Unweighted, Text
        ('en', 'pl', 'Cows go moo'),
        ('en', 'en', 'Old McDonald had a farm'),
        ('af', 'nl', "Ou boer McDonald het 'n plaas gehad"),
    ]

    def setUp(self):
        global LAST_PLAY
        LAST_PLAY = None

    def test_create_basic(self):
        tts = Talkey()
        for txt in self.TXTS:
            self.assertEqual(txt[1], tts.classify(txt[2]))

        self.assertEqual(tts.get_engine_for_lang('en').SLUG, 'espeak')

        tts.say('Old McDonald had a farm')
        inst, filename, output = LAST_PLAY
        self.assertIn('WAVE audio', output)
        self.assertEqual(inst, tts.engines[0])
        self.assertFalse(isfile(filename), 'Tempfile not deleted')

    def test_create_weighted(self):
        tts = Talkey(preferred_languages=['en', 'af'])
        for txt in self.TXTS:
            self.assertEqual(txt[0], tts.classify(txt[2]))

        tts = Talkey(preferred_languages=['en', 'af'], preferred_factor=10.0)
        self.assertEqual(self.TXTS[2][1], tts.classify(self.TXTS[2][2]))

    def test_create_empty(self):
        with self.assertRaisesRegexp(TTSError, 'No supported languages'):
            Talkey(
                espeak={'options': {'enabled': False}},
                festival={'options': {'enabled': False}},
                pico={'options': {'enabled': False}},
                flite={'options': {'enabled': False}},
            )

    def test_create_language_config(self):
        tts = Talkey(
            espeak={
                'languages': {
                    'en': {
                        'voice': 'english-mb-en1',
                        'words_per_minute': 130
                    },
                }
            },
        )
        eng = tts.engines[0]
        self.assertEqual(eng.languages_options['en'][0], 'english-mb-en1')
        self.assertEqual(eng.languages_options['en'][1]['words_per_minute'], 130)

    def test_get_engine_for_lang(self):
        tts = Talkey(
            espeak={'options': {'enabled': False}},
        )
        self.assertEqual(tts.get_engine_for_lang('fr').SLUG, 'pico')
        with self.assertRaisesRegexp(TTSError, 'Could not match language'):
            tts.get_engine_for_lang('af')

    def test_engine_preference(self):
        tts = Talkey(engine_preference=['pico'])

        self.assertEqual(tts.engines[0].SLUG, 'pico')
        self.assertEqual(tts.engines[1].SLUG, 'espeak')


class BaseTTSTest(unittest.TestCase):
    '''
    Tests talkey basic functionality
    '''
    # pylint: disable=E1102
    CLS = None
    SLUG = None
    INIT_ATTRS = ['enabled']
    CONF = {}
    OBJ_ATTRS = []
    EVAL_PLAY = True
    SKIP_IF_NOT_AVAILABLE = False
    FILE_TYPE = 'WAVE audio'

    @classmethod
    def setUpClass(cls):
        if not cls.CLS:
            raise unittest.SkipTest()

    def setUp(self):
        global LAST_PLAY
        LAST_PLAY = None

        # Stupid py2.6, Grrr
        if not self.CLS:
            raise unittest.SkipTest()

    def skip_not_available(self):
        if self.SKIP_IF_NOT_AVAILABLE and not self.CLS(**self.CONF).is_available():
            # Skip networked engines if not available to prevent spurious failiures
            raise unittest.SkipTest()  # pragma: no cover

    def test_class_init_options(self):
        cls = self.CLS
        self.assertEqual(cls.SLUG, self.SLUG)
        self.assertEqual(sorted(cls.get_init_options().keys()), sorted(self.INIT_ATTRS))

    def test_configure_not_enabled(self):
        with self.assertRaisesRegexp(TTSError, 'Not enabled'):
            self.CLS(enabled=False).configure()

    def test_class_instantiation(self):
        self.skip_not_available()
        obj = self.CLS(**self.CONF)
        self.assertEqual(obj.SLUG, self.SLUG)
        self.assertEqual(obj.is_available(), True)
        self.assertEqual(sorted(obj.get_options().keys()), sorted(self.OBJ_ATTRS))

    def test_class_configure(self):
        self.skip_not_available()
        obj = self.CLS(**self.CONF)
        language, voice, voiceinfo, options = obj._configure()
        self.assertEqual(language, 'en')
        self.assertIsNotNone(voice)
        self.assertEqual(voice, obj.get_languages()['en']['default'])
        self.assertEqual(sorted(options.keys()), sorted(self.OBJ_ATTRS))

    def test_class_say(self):
        self.skip_not_available()
        obj = self.CLS(**self.CONF)
        obj.say('Cows go moo')
        if self.EVAL_PLAY:
            inst, filename, output = LAST_PLAY
            self.assertIn(self.FILE_TYPE, output)
            self.assertEqual(inst, obj)
            self.assertFalse(isfile(filename), 'Tempfile not deleted')


class DummyTTSTest(BaseTTSTest):
    CLS = DummyTTS
    SLUG = 'dummy'
    CONF = {'enabled': True}
    EVAL_PLAY = False

    def test_configure_bad_language(self):
        with self.assertRaisesRegexp(TTSError, 'Bad language'):
            self.CLS(enabled=True).configure(language='bad')

    def test_configure_bad_voice(self):
        with self.assertRaisesRegexp(TTSError, 'Bad voice'):
            self.CLS(enabled=True).configure(voice='bad')


class FestivalTTSTest(BaseTTSTest):
    CLS = FestivalTTS
    SLUG = 'festival'
    INIT_ATTRS = ['enabled', 'festival']


class FliteTTSTest(BaseTTSTest):
    CLS = FliteTTS
    SLUG = 'flite'
    INIT_ATTRS = ['enabled', 'flite']


class EspeakTTSTest(BaseTTSTest):
    CLS = EspeakTTS
    SLUG = 'espeak'
    INIT_ATTRS = ['enabled', 'espeak', 'mbrola', 'mbrola_voices', 'passable_only']
    OBJ_ATTRS = ['words_per_minute', 'pitch_adjustment', 'variant']
    EVAL_PLAY = True

    def test_get_languages_options(self):
        pat = self.CLS(passable_only=True).get_languages()
        paf = self.CLS(passable_only=False).get_languages()
        assert len(paf.keys()) > len(pat.keys())

    def test_mbrola_language(self):
        obj = self.CLS(**self.CONF)
        obj.say('Cows go moo', voice='english-mb-en1')
        inst, filename, output = LAST_PLAY
        self.assertIn(self.FILE_TYPE, output)
        self.assertEqual(inst, obj)
        self.assertFalse(isfile(filename), 'Tempfile not deleted')

    def test_enabled_not_available(self):
        with self.assertRaisesRegexp(TTSError, 'Not available'):
            self.CLS(enabled=True, espeak='badexec').configure()

    def test_no_mbrola(self):
        obj = self.CLS(enabled=True)
        assert 'english-mb-en1' in obj.languages['en']['voices'].keys()

        obj = self.CLS(enabled=True, mbrola='badexec')
        assert 'english-mb-en1' not in obj.languages['en']['voices'].keys()


class PicoTTSTest(BaseTTSTest):
    CLS = PicoTTS
    SLUG = 'pico'
    INIT_ATTRS = ['enabled', 'pico2wave']


class MaryTTSTest(BaseTTSTest):
    CLS = MaryTTS
    SLUG = 'mary'
    INIT_ATTRS = ['enabled', 'host', 'port', 'scheme']
    CONF = {'enabled': True}#, 'host': 'mary.dfki.de'}
    EVAL_PLAY = True
    SKIP_IF_NOT_AVAILABLE = True


class GoogleTTSTest(BaseTTSTest):
    CLS = GoogleTTS
    SLUG = 'google'
    CONF = {'enabled': True}
    FILE_TYPE = 'MPEG ADTS, layer III'
    SKIP_IF_NOT_AVAILABLE = True
