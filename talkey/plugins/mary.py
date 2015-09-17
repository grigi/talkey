import os
import tempfile
import requests

try:
    from urlparse import urlunsplit
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlunsplit, urlencode

from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS
from talkey.utils import check_network_connection


class MaryTTS(AbstractTTSEngine):
    """
    Uses the MARY Text-to-Speech System (MaryTTS)
    MaryTTS is an open-source, multilingual Text-to-Speech Synthesis platform
    written in Java.
    Please specify your own server instead of using the demonstration server
    (http://mary.dfki.de:59125/) to save bandwidth and to protect your privacy.
    """

    SLUG = "mary-tts"

    @classmethod
    def _get_init_options(cls):
        return {
            'scheme': {
                'type': 'str',
                'default': 'http',
            },
            'host': {
                'type': 'str',
                'default': '127.0.0.1',
            },
            'port': {
                'type': 'int',
                'default': 59125,
                'min': 1,
                'max': 65535,
            }
        }

    def _makeurl(self, path, query={}):
        query_s = urlencode(query)
        urlparts = (self.ioptions['scheme'], self.ioptions['host'] + ':' + str(self.ioptions['port']), path, query_s, '')
        return urlunsplit(urlparts)

    def _is_available(self):
        return check_network_connection(self.ioptions['host'], self.ioptions['port'])

    def _get_options(self):
        return {}

    def _get_languages(self, detectable=True):
        res = requests.get(self._makeurl('voices')).text
        langs = {}
        for voice in [row.split() for row in res.split('\n') if row]:
            lang = voice[1].split('_')[0]
            langs.setdefault(lang, {'default': voice[0], 'voices': {}})
            langs[lang]['voices'][voice[0]] = {
                'gender': voice[2],
                'locale': voice[1]
            }
        return langs

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)

        query = {'OUTPUT_TYPE': 'AUDIO',
                 'AUDIO': 'WAVE_FILE',
                 'INPUT_TYPE': 'TEXT',
                 'INPUT_TEXT': phrase,
                 'LOCALE': voiceinfo['locale'],
                 'VOICE': voice}

        res = requests.get(self._makeurl('/process', query=query))
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(res.content)
            tmpfile = f.name
        self.play(tmpfile)
        os.remove(tmpfile)
