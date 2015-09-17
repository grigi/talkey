import langid

from .base import TTSError
from .engines import _ENGINE_MAP, _ENGINE_ORDER

_ENGINES = []
_LANGS = set()

def enumerate_engines():
    return _ENGINE_ORDER

def active_languages():
    return _LANGS

def create_engine(engine, options=None, defaults=None):
    if engine not in _ENGINE_ORDER:
        raise TTSError('Unknown engine %s' % engine)

    options = options or {}
    defaults = defaults or {}
    einst = _ENGINE_MAP[engine](**options)
    einst.configure_default(**defaults)
    return einst

def configure(config=None):
    config = config or {}
    for ename in enumerate_engines():
        try:
            options = config.get(ename,{}).get('options',{})
            defaults = config.get(ename,{}).get('defaults',{})
            en = create_engine(ename, options=options, defaults=defaults)
            _ENGINES.append(en)

            languages = config.get(ename,{}).get('languages',{})
            for lang, conf in languages.items():
                en.configure(language=lang, **conf)
        except TTSError:
            pass

    for en in _ENGINES:
        _LANGS.update(en.languages.keys())

    langid.set_languages(_LANGS)


def say(txt):
    def get_engine_for_lang(lang):
        for en in _ENGINES:
            if lang in en.languages.keys():
                return en
        raise TTSError('Could not match a language')

    if not _LANGS:
        raise TTSError('Could not match a language')

    lang = langid.classify(txt)[0]
    get_engine_for_lang(lang).say(txt, language=lang)
