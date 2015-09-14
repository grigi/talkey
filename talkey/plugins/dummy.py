from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS


class DummyTTS(AbstractTTSEngine):
    """
    Dummy TTS engine that logs phrases with INFO level instead of synthesizing
    speech.
    """

    SLUG = "dummy-tts"

    @classmethod
    def get_init_options(cls):
        return {
            'enabled': {
                'type': 'bool',
                'default': False,
            },
        }

    def is_available(self):
        return self.ioptions['enabled']

    def get_options(self):
        return {}

    def get_languages(self, detectable=True):
        return dict([
            (lang, {'default': lang, 'voices': {lang: {}}})
            for lang in DETECTABLE_LANGS
        ])

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.info('%s: %s' % (language, phrase))
