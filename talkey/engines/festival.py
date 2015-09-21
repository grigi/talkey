import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess, register
from talkey.utils import check_executable


@register
class FestivalTTS(AbstractTTSEngine):
    """
    Uses the festival speech synthesizer.

    Requires ``festival`` to be available.
    """

    SLUG = 'festival'

    SAY_TEMPLATE = """(Parameter.set 'Audio_Required_Format 'riff)
(Parameter.set 'Audio_Command "mv $FILE {outfilename}")
(Parameter.set 'Audio_Method 'Audio_Command)
(SayText "{phrase}")
"""

    @classmethod
    def _get_init_options(cls):
        return {
            'festival': {
                'description': 'Festival executable path',
                'type': 'str',
                'default': 'festival'
            },
        }

    def _is_available(self):
        if check_executable(self.ioptions['festival']):
            cmd = ['festival', '--pipe']
            with tempfile.SpooledTemporaryFile() as in_f:
                self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
                output = subprocess.check_output(cmd, stdin=in_f, stderr=subprocess.STDOUT, universal_newlines=True).strip()
                return 'No default voice found' not in output
        return False  # pragma: no cover

    def _get_options(self):
        return {}

    def _get_languages(self):
        return {
            'en': {'default': 'en', 'voices': {'en': {}}}
        }

    def _say(self, phrase, language, voice, voiceinfo, options):
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
