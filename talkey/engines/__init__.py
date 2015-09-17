from .dummy import DummyTTS
from .festival import FestivalTTS
from .flite import FliteTTS
from .espeak import EspeakTTS
from .mary import MaryTTS
from .pico import PicoTTS
from .google import GoogleTTS

from talkey.base import TTSError

_ENGINE_MAP = {
    'dummy-tts': DummyTTS,
    'flite-tts': FliteTTS,
    'pico-tts': PicoTTS,
    'festival-tts': FestivalTTS,
    'espeak-tts': EspeakTTS,
    'mary-tts': MaryTTS,
    'google-tts': GoogleTTS,
}

_ENGINE_ORDER = ['google-tts', 'mary-tts', 'espeak-tts', 'festival-tts', 'pico-tts', 'flite-tts']

def enumerate():
    return _ENGINE_ORDER

def create(engine, options=None, defaults=None):
    if engine not in _ENGINE_ORDER:
        raise TTSError('Unknown engine %s' % engine)

    options = options or {}
    defaults = defaults or {}
    einst = _ENGINE_MAP[engine](**options)
    einst.configure(**defaults)
    return einst

