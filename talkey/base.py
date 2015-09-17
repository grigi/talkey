import os
import pipes
import logging
import tempfile
from abc import ABCMeta, abstractmethod

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


from talkey.utils import process_options, check_executable

import langid
import contextlib
import audioread
import wave

# Get the list of identifiable languages
DETECTABLE_LANGS = sorted([a[0] for a in langid.rank('')])


class TTSError(Exception):

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

    # Define these in your engine
    @classmethod
    @abstractmethod
    def _get_init_options(cls):
        pass  # pragma: no cover

    @abstractmethod
    def _is_available(self):
        pass  # pragma: no cover

    @abstractmethod
    def _get_options(self):
        pass  # pragma: no cover

    @abstractmethod
    def _get_languages(self, detectable=True):
        pass  # pragma: no cover

    @abstractmethod
    def _say(self, phrase, language, voice, voiceinfo, options):
        pass  # pragma: no cover

    @classmethod
    def get_init_options(cls):
        options = {
            'enabled': {
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
        self.language = None
        self.voice = None
        self.options = {}
        self.optionspec = None
        self.languages = None
        self.available = self.is_available()
        if self.available:
            self.optionspec = self.get_options()
            self.languages = self.get_languages()
            self.configure()

    def is_available(self):
        return (
            self.ioptions['enabled']
            and check_executable('aplay')
            and self._is_available()
        )

    def _assert_available(self):
        if not self.ioptions['enabled']:
            raise TTSError('Not enabled')
        if not self.available:
            raise TTSError('Not available')

    def get_options(self):
        self._assert_available()
        return self._get_options()

    def get_languages(self):
        self._assert_available()
        return self._get_languages()

    def _configure(self, language=None, voice=None, **_options):
        self._assert_available()

        language = language or self.language or 'en'
        voice = voice or self.voice

        if language not in self.languages.keys():
            raise TTSError('Bad language: %s' % language, self.languages.keys())

        voice = voice if voice else self.languages[language]['default']
        if voice not in self.languages[language]['voices'].keys():
            raise TTSError('Bad voice: %s' % voice, self.languages[language]['voices'].keys())
        voiceinfo = self.languages[language]['voices'][voice]

        newopts = self.options
        newopts.update(_options)
        options = process_options(self.optionspec, newopts, TTSError)
        return language, voice, voiceinfo, options

    def configure(self, **_options):
        self.language, self.voice, voiceinfo, self.options = self._configure(**_options)

    def say(self, phrase, **_options):
        language, voice, voiceinfo, options = self._configure(**_options)
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        self._say(phrase, language, voice, voiceinfo, options)

    def play(self, filename, translate=False): # pragma: no cover
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

        cmd = ['aplay', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        subprocess.call(cmd)

        if translate:
            os.remove(fname)
