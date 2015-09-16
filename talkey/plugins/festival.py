import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess
from talkey.utils import check_executable, memoize


class FestivalTTS(AbstractTTSEngine):
    """
    Uses the festival speech synthesizer
    Requires festival to be available
    """

    SLUG = 'festival-tts'

    SAY_TEMPLATE = """(Parameter.set 'Audio_Required_Format 'riff)
(Parameter.set 'Audio_Command "mv $FILE {outfilename}")
(Parameter.set 'Audio_Method 'Audio_Command)
(SayText "{phrase}")
"""

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
        cmd = ['festival', '--pipe']
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        with tempfile.SpooledTemporaryFile() as in_f:
            in_f.write(self.SAY_TEMPLATE.format(outfilename=fname, phrase=phrase.replace('\\', '\\\\"').replace('"', '\\"')).encode('utf-8'))
            in_f.seek(0)
            self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
            subprocess.call(cmd, stdin=in_f)
        self.play(fname)
        os.remove(fname)

