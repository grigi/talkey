import os
import subprocess
import tempfile
import pipes
from talkey.base import AbstractTTSEngine
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
        output = subprocess.Popen(['flite', '-lv'], stdout=subprocess.PIPE).stdout.read()
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
        with tempfile.SpooledTemporaryFile() as out_f:
            self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
            subprocess.call(cmd, stdout=out_f, stderr=out_f)
            out_f.seek(0)
            output = out_f.read().strip()
        if output:
            self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)
