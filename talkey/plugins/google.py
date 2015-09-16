import os
import tempfile

try:
    import gtts
except ImportError:  # pragma: no cover
    pass

from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS
from talkey.utils import memoize, check_network_connection, check_python_import


class GoogleTTS(AbstractTTSEngine):
    """
    Uses the Google TTS online translator
    Requires pymad and gTTS to be available
    """

    SLUG = "google-tts"

    @classmethod
    def get_init_options(cls):
        return {}

    @memoize
    def is_available(self):
        return (
            check_python_import('gtts')
            and check_network_connection('translate.google.com', 80)
        )

    def get_options(self):
        return {}

    @memoize
    def get_languages(self, detectable=True):
        voices = gtts.gTTS.LANGUAGES.keys()
        langs = {}
        for voice in voices:
            lang = voice[:2]
            langs.setdefault(lang, {'default': voice, 'voices': {}})
            langs[lang]['voices'][voice] = {}
        return langs

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        tts = gtts.gTTS(text=phrase, lang=voice)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self.play(tmpfile, translate=True)
        os.remove(tmpfile)
