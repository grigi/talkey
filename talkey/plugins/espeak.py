import os
import subprocess
import tempfile
from talkey.base import AbstractTTSEngine, diagnose, pipes


class EspeakTTS(AbstractTTSEngine):
    """
    Uses the eSpeak speech synthesizer.
    Requires espeak to be available
    """

    SLUG = "espeak-tts"

    def __init__(self, voice='default+m3', pitch_adjustment=40, words_per_minute=160):
        super(self.__class__, self).__init__()
        self.voice = voice
        self.pitch_adjustment = pitch_adjustment
        self.words_per_minute = words_per_minute

    @classmethod
    def is_available(cls):
        return (cls.has_audio_output() and
                diagnose.check_executable('espeak'))

    @classmethod
    def get_languages(cls):
        output = subprocess.Popen(['espeak', '--voices'], stdout=subprocess.PIPE).stdout.read()
        voices = [row.split()[1:4] for row in output.split('\n')[1:] if row]
        langs = set([voice[0].split('-')[0] for voice in voices])
        tree = dict([(lang, {'default': None, 'voices': []}) for lang in langs])
        for voice in voices:
            lang = voice[0].split('-')[0]
            tree[lang]['voices'].append({'gender': voice[1], 'name': voice[2]})
            if lang == voice[0]:
                tree[lang]['default'] = voice[2]
        for lang in langs:
            if tree[lang]['default'] is None:
                # If no explicit default, set it to the one with the shortest voice name
                tree[lang]['default'] = sorted([voice['name'] for voice in tree[lang]['voices']])[0]
        return tree

    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = [
            'espeak', 
            '-v', self.voice,
            '-p', self.pitch_adjustment,
            '-s', self.words_per_minute,
            '-w', fname,
            phrase
        ]
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)

