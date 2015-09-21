import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess, register
from talkey.utils import check_executable


@register
class FliteTTS(AbstractTTSEngine):
    """
    Uses the flite speech synthesizer.

    Requires ``flite`` to be available.
    """

    SLUG = 'flite'

    @classmethod
    def _get_init_options(cls):
        return {
            'flite': {
                'description': 'FLite executable path',
                'type': 'str',
                'default': 'flite'
            },
        }

    def _is_available(self):
        return check_executable(self.ioptions['flite'])

    def _get_options(self):
        return {}

    def _get_languages(self):
        output = subprocess.check_output(['flite', '-lv'], universal_newlines=True)
        voices = output[output.find(':') + 1:].split()
        return {
            'en': {
                'default': 'kal',
                'voices': dict([(voice, {}) for voice in voices])
            }
        }

    def _say(self, phrase, language, voice, voiceinfo, options):
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
