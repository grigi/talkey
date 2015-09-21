from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS


class DummyTTS(AbstractTTSEngine):
    """
    Dummy TTS engine that logs phrases with INFO level instead of synthesizing
    speech.
    """

    SLUG = "dummy"

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
        return True

    def _get_options(self):
        return {}

    def _get_languages(self):
        return dict([
            (lang, {'default': lang, 'voices': {lang: {}}})
            for lang in DETECTABLE_LANGS
        ])

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.info('%s: %s' % (language, phrase))
