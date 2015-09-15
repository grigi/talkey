import os
import subprocess
import tempfile
import pipes
from talkey.base import AbstractTTSEngine
from talkey.utils import check_executable, memoize


class FestivalTTS(AbstractTTSEngine):
    """
    Uses the festival speech synthesizer
    Requires festival to be available
    """

    SLUG = 'festival-tts'

    @classmethod
    def get_init_options(cls):
        return {}

    @memoize
    def is_available(self):
        if check_executable('festival'):
            cmd = ['festival', '--pipe']
            with tempfile.SpooledTemporaryFile() as in_f:
                self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
                output = subprocess.check_output(cmd, stdin=in_f, stderr=subprocess.STDOUT, universal_newlines=True).strip()
                if output:
                    self._logger.debug("Output was: '%s'", output)
                return 'No default voice found' not in output
        return False

    def get_options(self):
        return {}

    def get_languages(self, detectable=True):
        return {
            'en': {'default': 'en', 'voices': {'en': {}}}
        }

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        cmd = ['festival', '--tts']
        with tempfile.SpooledTemporaryFile() as in_f:
            in_f.write(phrase)
            in_f.seek(0)
            self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
            output = subprocess.check_output(cmd, stdin=in_f, universal_newlines=True).strip()
            if output:
                self._logger.debug("Output was: '%s'", output)
