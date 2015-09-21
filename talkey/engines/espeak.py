import os
import tempfile
import pipes
from talkey.base import AbstractTTSEngine, subprocess, register


@register
class EspeakTTS(AbstractTTSEngine):
    """
    Uses the eSpeak speech synthesizer.

    Requires ``espeak`` and optionally ``mbrola`` to be available.
    """

    SLUG = "espeak"
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
                'description': 'eSpeak executable path',
                'type': 'exec',
                'default': [
                    'espeak',
                    r'c:\Program Files\eSpeak\command_line\espeak.exe'
                ]
            },
            'mbrola': {
                'description': 'mbrola executable path',
                'type': 'exec',
                'default': 'mbrola'
            },
            'mbrola_voices': {
                'description': 'mbrola voices path',
                'type': 'str',
                'default': '/usr/share/mbrola'
            },
            'passable_only': {
                'description': 'Only allow languages of passable quality, as per http://espeak.sourceforge.net/languages.html',
                'type': 'bool',
                'default': True
            }
        }

    def _is_available(self):
        return self.ioptions['espeak'] is not None

    def has_mbrola(self):
        return self.ioptions['mbrola'] is not None

    def _get_options(self):
        output = subprocess.check_output([self.ioptions['espeak'], '--voices=variant'], universal_newlines=True)
        variants = [row[row.find('!v') + 3:].strip() for row in output.split('\n')[1:] if row]
        return {
            'variant': {
                'type': 'enum',
                'values': sorted([''] + variants),
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
                'default': 150,
            },
        }

    def _get_languages(self):
        'Get all working voices and languages for eSpeak'

        def fix_voice(voice):
            'Work-around bug in eSpeak 1.46 where gender is sometimes missing'
            if voice[2] not in ['M', 'F', '-']:
                return voice[:2] + ['-'] + voice[2:]  # pragma: no cover
            return voice

        output = subprocess.check_output([self.ioptions['espeak'], '--voices'], universal_newlines=True)
        voices = [
            ['mbrola' if fix_voice(row.split())[4].startswith('mb') else 'espeak'] + fix_voice(row.split())[:4]
            for row in output.split('\n')[1:]
            if row
        ]

        if self.has_mbrola():
            output = subprocess.check_output([self.ioptions['espeak'], '--voices=mbrola'], universal_newlines=True)
            mvoices = [fix_voice(row.split())[:5] for row in output.split('\n')[1:] if row]
            for mvoice in mvoices:
                mbfile = mvoice[4].split('-')[1]
                mbfile = os.path.join(self.ioptions['mbrola_voices'], mbfile, mbfile)
                if os.path.isfile(mbfile):
                    voices.append(['mbrola'] + mvoice)

        langs = set([voice[2].split('-')[0] for voice in voices])
        if self.ioptions['passable_only']:
            langs = [lang for lang in langs if lang in self.QUALITY_LANGS]
        tree = dict([(lang, {'voices': {}}) for lang in langs])
        for voice in voices:
            lang = voice[2].split('-')[0]
            if lang in langs:
                tree[lang]['voices'][voice[4]] = {'gender': voice[3], 'pty': int(voice[1]), 'type': voice[0]}
        for lang in langs:
            # Try to find sane default voice, score by pty, then take shortest (for determinism)
            vcs = tree[lang]['voices']
            pty = min([v['pty'] for v in vcs.values()])
            tree[lang]['default'] = sorted([k for k, v in vcs.items() if v['pty'] == pty])[0]
        return tree

    def _say(self, phrase, language, voice, voiceinfo, options):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        vce = voice
        if voiceinfo['type'] == 'espeak' and options['variant']:
            vce += '+' + options['variant']
        cmd = [
            self.ioptions['espeak'],
            '-v', vce,
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
