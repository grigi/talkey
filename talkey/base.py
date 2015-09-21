import os
import pipes
import logging
import tempfile
from abc import ABCMeta, abstractmethod

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess

try:
    import winsound
except ImportError:
    winsound = None

from talkey.utils import process_options, check_executable

import langid
import contextlib
import audioread
import wave

# Get the list of identifiable languages
DETECTABLE_LANGS = sorted([a[0] for a in langid.rank('')])


def genrst(label, opt, txt, indent='    '):
    txt += '\n%s%s:\n\n' % (indent, label)
    for key in sorted(opt.keys()):
        val = opt[key]
        txt += indent + '``%s``\n' % key
        txt += indent + '    %s\n\n' % val.get('description', '%s option' % key)
        txt += indent + '    :type: %s\n' % val['type']
        txt += indent + '    :default: %s\n' % val['default']
        if 'min' in val.keys():
            txt += indent + '    :min: %s\n' % val['min']
        if 'max' in val.keys():
            txt += indent + '    :max: %s\n' % val['max']
        if 'values' in val.keys():
            txt += indent + '    :values: %s\n' % ', '.join(val['values'])
    return txt


def register(cls):
    cls.__doc__ = genrst('Initialization options', cls.get_init_options(), cls.__doc__)
    return cls


class TTSError(Exception):
    '''
    The exception that Talkey will throw if any error occurs.
    '''

    def __init__(self, error, valid_set=None):  # pylint: disable=W0231
        self.error = error
        self.valid_set = valid_set

    def __str__(self):
        if self.valid_set:
            return '%s\nValid set: %s' % (self.error, self.valid_set)
        else:
            return self.error


class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta
    SLUG = None
    'The SLUG is used to identify the engine as text'

    # Define these in your engine
    @classmethod
    @abstractmethod
    def _get_init_options(cls):
        'AbstractMethod: Returns dict of engine options'
        pass  # pragma: no cover

    @abstractmethod
    def _is_available(self):
        'AbstractMethod: Boolean on if engine is available'
        pass  # pragma: no cover

    @abstractmethod
    def _get_options(self):
        'AbstractMethod: Returns dict of voice options'
        pass  # pragma: no cover

    @abstractmethod
    def _get_languages(self):
        'AbstractMethod: Returns dict of supported languages and voices'
        pass  # pragma: no cover

    @abstractmethod
    def _say(self, phrase, language, voice, voiceinfo, options):
        '''
        AbstractMethod: Let engin actually says the phrase

        :phrase: The text phrase to say
        :language: The requested language
        :voice: The requested voice
        :voiceinfo: Data about the requested voice
        :options: Extra options
        '''
        pass  # pragma: no cover

    @classmethod
    def get_init_options(cls):
        '''
        Returns a dict describing the engine options.

        Uses cls._get_init_options()
        '''
        options = {
            'enabled': {
                'description': 'Is enabled?',
                'type': 'bool',
                'default': True
            },
        }
        options.update(cls._get_init_options())
        return options

    # Base class continues here
    def __init__(self, **_options):
        self._logger = logging.getLogger(__name__)
        self.ioptions = process_options(self.__class__.get_init_options(), _options, TTSError)

        # Pre-caching potentially slow results
        self.default_language = 'en'
        self.languages_options = {}
        self.default_options = {}
        self.optionspec = None
        self.languages = None
        self.available = self.is_available()
        if self.available:
            self.optionspec = self.get_options()
            self.languages = self.get_languages()
            self.configure_default()

    def sound_available(self):
        return winsound or check_executable('aplay')

    def is_available(self):
        '''
        Boolean on if engine available.

        Checks if enabled, can output audio and self._is_available()
        '''
        return (
            self.ioptions['enabled']
            and self.sound_available()
            and self._is_available()
        )

    def _assert_available(self):
        if not self.ioptions['enabled']:
            raise TTSError('Not enabled')
        if not self.available:
            raise TTSError('Not available')

    def get_options(self):
        '''
        Returns dict of voice options.

        Raises TTSError if not available.
        '''
        self._assert_available()
        return self._get_options()

    def get_languages(self):
        '''
        Returns dict of supported languages and voices.

        Raises TTSError if not available.
        '''
        self._assert_available()
        return self._get_languages()

    def _get_language_options(self, language):
        if language in self.languages_options.keys():
            return self.languages_options[language]
        return None, {}

    def _configure(self, language=None, voice=None, **_options):
        self._assert_available()

        language = language or self.default_language
        lang_voice, lang_options = self._get_language_options(language)
        voice = voice or lang_voice

        if language not in self.languages.keys():
            raise TTSError('Bad language: %s' % language, self.languages.keys())

        voice = voice if voice else self.languages[language]['default']
        if voice not in self.languages[language]['voices'].keys():
            raise TTSError('Bad voice: %s' % voice, self.languages[language]['voices'].keys())
        voiceinfo = self.languages[language]['voices'][voice]

        lang_options.update(_options)
        options = process_options(self.optionspec, lang_options, TTSError)
        return language, voice, voiceinfo, options

    def configure_default(self, **_options):
        '''
        Sets default configuration.

        Raises TTSError on error.
        '''
        language, voice, voiceinfo, options = self._configure(**_options)
        self.languages_options[language] = (voice, options)
        self.default_language = language
        self.default_options = options

    def configure(self, **_options):
        '''
        Sets language-specific configuration.

        Raises TTSError on error.
        '''
        language, voice, voiceinfo, options = self._configure(**_options)
        self.languages_options[language] = (voice, options)

    def say(self, phrase, **_options):
        '''
        Says the phrase, optionally allows to select/override any voice options.
        '''
        language, voice, voiceinfo, options = self._configure(**_options)
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        self._say(phrase, language, voice, voiceinfo, options)

    def play(self, filename, translate=False):  # pragma: no cover
        '''
        Plays the sounds.

        :filename: The input file name
        :translate: If True, it runs it through audioread which will translate from common compression formats to raw WAV.
        '''
        # FIXME: Use platform-independent and async audio-output here
        # PyAudio looks most promising, too bad about:
        #  --allow-external PyAudio --allow-unverified PyAudio
        if translate:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                fname = f.name
            with audioread.audio_open(filename) as f:
                with contextlib.closing(wave.open(fname, 'w')) as of:
                    of.setnchannels(f.channels)
                    of.setframerate(f.samplerate)
                    of.setsampwidth(2)
                    for buf in f:
                        of.writeframes(buf)
            filename = fname

        if winsound:
            winsound.PlaySound(str(filename), winsound.SND_FILENAME)
        else:
            cmd = ['aplay', str(filename)]
            self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
            subprocess.call(cmd)

        if translate:
            os.remove(fname)
