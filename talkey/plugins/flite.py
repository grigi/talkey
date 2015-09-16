import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess
from talkey.utils import check_executable, memoize


class FliteTTS(AbstractTTSEngine):
    """
    Uses the flite speech synthesizer
    Requires flite to be available
    """

    SLUG = 'flite-tts'

    @classmethod
    def get_init_options(cls):
        return {}

    @memoize
    def is_available(self):
        return check_executable('flite')

    def get_options(self):
        return {}

    @memoize
    def get_languages(self, detectable=True):
        output = subprocess.check_output(['flite', '-lv'], universal_newlines=True)
        voices = output[output.find(':') + 1:].split()
        return {
            'en': {
                'default': 'kal',
                'voices': dict([(voice, {}) for voice in voices])
            }
        }

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        cmd = [
            'flite',
            '-voice', voice,
            '-t', phrase
        ]
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd.append(fname)
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        subprocess.call(cmd)
        self.play(fname)
        os.remove(fname)
