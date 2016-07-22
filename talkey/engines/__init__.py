from .dummy import DummyTTS
from .espeak import EspeakTTS
from .festival import FestivalTTS
from .flite import FliteTTS
from .google import GoogleTTS
from .mary import MaryTTS
from .pico import PicoTTS
from .say import SayTTS

_ENGINE_MAP = {
    'dummy': DummyTTS,
    'espeak': EspeakTTS,
    'flite': FliteTTS,
    'festival': FestivalTTS,
    'google': GoogleTTS,
    'mary': MaryTTS,
    'pico': PicoTTS,
    'say': SayTTS,
}

_ENGINE_ORDER = ['google', 'mary', 'espeak', 'festival', 'pico', 'flite', 'say', 'dummy']
