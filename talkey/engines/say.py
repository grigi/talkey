import platform
import pipes
from talkey.base import AbstractTTSEngine, subprocess, register


@register
class SayTTS(AbstractTTSEngine):
    """
    Uses the built-in TTS engine `say` on macOS.
    """

    SLUG = 'say'

    @classmethod
    def _get_init_options(cls):
        return {
            'say': {
                'description': 'Say executable path',
                'type': 'str',
                'default': r'say'
            },
        }

    def sound_available(self):
        """
        We must override this function since the winsound module and the aplay
        executable do not exist on macOS.
        """
        return platform.system() == 'Darwin'

    def _is_available(self):
        return platform.system() == 'Darwin'

    def _get_options(self):
        return {}

    def _get_languages(self):
        """
        Parses the output of `say -v '?'`
        """
        lines = subprocess.check_output([self.ioptions['say'], '-v', '?'], universal_newlines=True).split("\n")
        langs = {}
        for line in lines:
            voice = line.split()
            if len(voice) < 2: continue
            if voice[1][:2] not in langs:
                langs[voice[1][:2]] = {
                    'default': voice[0],
                    'voices': { } }
            langs[voice[1][:2]]['voices'][voice[0]] = {}
        return langs

    def _say(self, phrase, language, voice, voiceinfo, options):
        cmd = [
            'say',
            phrase
        ]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        subprocess.call(cmd)
