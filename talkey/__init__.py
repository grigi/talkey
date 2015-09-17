'''
Simple Test-To-Speech (TTS) interface library with multi-language and multi-engine support.
'''
# from . import

__version__ = '0.1.0'

from .tts import enumerate_engines, active_languages, create_engine, configure, say
