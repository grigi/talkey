import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, DETECTABLE_LANGS, subprocess
from talkey.utils import check_executable


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
    def _get_init_options(cls):
        return {
            'espeak': {
                'type': 'str',
                'default': 'espeak'
            },
            'mbrola': {
                'type': 'str',
                'default': 'mbrola'
            },
            'mbrola_voices': {
                'type': 'str',
                'default': '/usr/share/mbrola'
            },
            'passable_only': {
                'type': 'bool',
                'default': True
            }
        }

    def _is_available(self):
        return check_executable(self.ioptions['espeak'])

    def has_mbrola(self):
        return check_executable(self.ioptions['mbrola'])

    def _get_options(self):
        output = subprocess.check_output([self.ioptions['espeak'], '--voices=variant'], universal_newlines=True)
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
                'default': 40,
            },
            'words_per_minute': {
                'type': 'int',
                'min': 80,
                'max': 450,
                'default': 150,
            },
        }

    def _get_languages(self):
        output = subprocess.check_output([self.ioptions['espeak'], '--voices'], universal_newlines=True)
        voices = [row.split()[:4] for row in output.split('\n')[1:] if row]

        if self.has_mbrola():
            output = subprocess.check_output([self.ioptions['espeak'], '--voices=mbrola'], universal_newlines=True)
            mvoices = [row.split()[:5] for row in output.split('\n')[1:] if row]
            for mvoice in mvoices:
                mbfile = mvoice[4].split('-')[1]
                mbfile = os.path.join(self.ioptions['mbrola_voices'], mbfile, mbfile)
                if os.path.isfile(mbfile):
                    voices.append(mvoice)

        langs = set([voice[1].split('-')[0] for voice in voices])
        if self.ioptions['passable_only']:
            langs = [lang for lang in langs if lang in self.QUALITY_LANGS]
        tree = dict([(lang, {'voices': {}}) for lang in langs])
        for voice in voices:
            lang = voice[1].split('-')[0]
            if lang in langs:
                tree[lang]['voices'][voice[3]] = {'gender': voice[2], 'pty': int(voice[0])}
        for lang in langs:
            # Try to find sane default voice
            vcs = tree[lang]['voices']
            pty = min([v['pty'] for v in vcs.values()])
            tree[lang]['default'] = sorted([k for k,v in vcs.items() if v['pty'] == pty])[0]
        return tree

    def _say(self, phrase, language, voice, voiceinfo, options):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = [
            self.ioptions['espeak'],
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
