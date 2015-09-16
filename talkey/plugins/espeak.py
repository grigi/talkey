import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS, subprocess
from talkey.utils import check_executable, memoize


class EspeakTTS(AbstractTTSEngine):
    """
    Uses the eSpeak speech synthesizer.
    Requires espeak to be available
    """

    SLUG = "espeak-tts"
    # http://espeak.sourceforge.net/languages.html
    QUALITY_LANGS = [
        'en', 'af', 'bs', 'ca', 'cs', 'da', 'de', 'el', 'eo', 'es',
        'fi', 'fr', 'hr', 'hu', 'it', 'kn', 'ku', 'lv', 'nl', 'pl',
        'pt', 'ro', 'sk', 'sr', 'sv', 'sw', 'ta', 'tr', 'zh'
    ]

    @classmethod
    def get_init_options(cls):
        return {}

    @memoize
    def is_available(self):
        return check_executable('espeak')

    @memoize
    def get_options(self):
        output = subprocess.check_output(['espeak', '--voices=variant'], universal_newlines=True)
        variants = [row[row.find('!v/') + 3:].strip() for row in output.split('\n')[1:] if row]
        return {
            'variant': {
                'type': 'enum',
                'values': variants,
                'default': 'm3',
            },
            'pitch_adjustment': {
                'type': 'int',
                'min': 0,
                'max': 99,
                'default': 50,
            },
            'words_per_minute': {
                'type': 'int',
                'min': 80,
                'max': 450,
                'default': 175,
            },
        }

    @memoize
    def get_languages(self, quality=True, detectable=True):
        output = subprocess.check_output(['espeak', '--voices'], universal_newlines=True)
        voices = [row.split()[1:4] for row in output.split('\n')[1:] if row]
        langs = set([voice[0].split('-')[0] for voice in voices])
        if detectable:
            langs = [lang for lang in langs if lang in DETECTABLE_LANGS]
        if quality:
            langs = [lang for lang in langs if lang in self.QUALITY_LANGS]
        tree = dict([(lang, {'default': None, 'voices': {}}) for lang in langs])
        for voice in voices:
            lang = voice[0].split('-')[0]
            if lang in langs:
                tree[lang]['voices'][voice[2]] = {'gender': voice[1]}
                #tree[lang]['voices'].append({'gender': voice[1], 'name': voice[2]})
                if lang == voice[0]:
                    tree[lang]['default'] = voice[2]
        for lang in langs:
            if tree[lang]['default'] is None:
                # If no explicit default, set it to the one with the shortest voice name
                tree[lang]['default'] = sorted(tree[lang]['voices'].keys())[0]
        return tree

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = [
            'espeak',
            '-v', voice + '+' + options['variant'],
            '-p', options['pitch_adjustment'],
            '-s', options['words_per_minute'],
            '-w', fname,
            phrase
        ]
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        subprocess.call(cmd)
        self.play(fname)
        os.remove(fname)
