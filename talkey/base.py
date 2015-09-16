import os
import pipes
import logging
import tempfile
from abc import ABCMeta, abstractmethod

try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


from talkey.utils import process_options, check_executable, memoize

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

    @classmethod
    @abstractmethod
    def get_init_options(cls):
        pass  # pragma: no cover

    def __init__(self, **_options):
        self._logger = logging.getLogger(__name__)
        self.ioptions = process_options(self.__class__.get_init_options(), _options, TTSError)

    @memoize
    def has_audio_output(self):
        return check_executable('aplay')

    @abstractmethod
    def is_available(self):
        pass  # pragma: no cover

    @abstractmethod
    def get_options(self):
        pass  # pragma: no cover

    @abstractmethod
    def get_languages(self, detectable=True):
        pass  # pragma: no cover

    def configure(self, language='en', voice=None, **_options):
        if not (self.has_audio_output() and self.is_available()):
            raise TTSError('Not available')

        languages = self.get_languages()
        if language not in languages.keys():
            raise TTSError('Bad language: %s' % language, languages.keys())

        voice = voice if voice else languages[language]['default']
        if voice not in languages[language]['voices'].keys():
            raise TTSError('Bad voice: %s' % voice, languages[language]['voices'].keys())
        voiceinfo = languages[language]['voices'][voice]

        valid_options = self.get_options()
        options = process_options(valid_options, _options, TTSError)
        #print(language, voice, voiceinfo, options)
        return language, voice, voiceinfo, options

    def say(self, phrase, **options):
        language, voice, voiceinfo, options = self.configure(**options)
        self._say(phrase, language, voice, voiceinfo, options)

    @abstractmethod
    def _say(self, phrase, language, voice, voiceinfo, options):
        pass  # pragma: no cover

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
