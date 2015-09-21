from .dummy import DummyTTS
from .festival import FestivalTTS
from .flite import FliteTTS
from .espeak import EspeakTTS
from .mary import MaryTTS
from .pico import PicoTTS
from .google import GoogleTTS

_ENGINE_MAP = {
    'dummy': DummyTTS,
    'flite': FliteTTS,
    'pico': PicoTTS,
    'festival': FestivalTTS,
    'espeak': EspeakTTS,
    'mary': MaryTTS,
    'google': GoogleTTS,
}

_ENGINE_ORDER = ['google', 'mary', 'espeak', 'festival', 'pico', 'flite', 'dummy']
