import os
import tempfile

try:
    import gtts
except ImportError:  # pragma: no cover
    pass

from talkey.base import AbstractTTSEngine, register
from talkey.utils import check_network_connection, check_python_import


@register
class GoogleTTS(AbstractTTSEngine):
    """
    Uses the Google TTS online translator.

    Requires module ``gTTS`` to be available.
    """

    SLUG = "google"

    @classmethod
    def _get_init_options(cls):
        return {
            'enabled': {
                'description': 'Is enabled?',
                'type': 'bool',
                'default': False,
            },
        }

    def _is_available(self):
        return (
            check_python_import('gtts')
            and check_network_connection('translate.google.com', 80)
        )

    def _get_options(self):
        return {}

    def _get_languages(self):
        voices = gtts.gTTS.LANGUAGES.keys()
        langs = {}
        for voice in voices:
            lang = voice[:2]
            langs.setdefault(lang, {'default': voice, 'voices': {}})
            langs[lang]['voices'][voice] = {}
        return langs

    def _say(self, phrase, language, voice, voiceinfo, options):
        tts = gtts.gTTS(text=phrase, lang=voice)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self.play(tmpfile, translate=True)
        os.remove(tmpfile)
