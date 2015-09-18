import langid

from .base import TTSError
from .engines import _ENGINE_MAP, _ENGINE_ORDER


def enumerate_engines():
    return _ENGINE_ORDER

def create_engine(engine, options=None, defaults=None):
    if engine not in _ENGINE_MAP.keys():
        raise TTSError('Unknown engine %s' % engine)

    options = options or {}
    defaults = defaults or {}
    einst = _ENGINE_MAP[engine](**options)
    einst.configure_default(**defaults)
    return einst

class Talkey(object):

    def __init__(self, config=None):
        config = config or {}

        self.engines = []
        self.languages = set()
        self.preferred_languages = set(config.get('preferred_languages', []))
        self.preferred_factor = float(config.get('preferred_factor', 80.0))

        for ename in enumerate_engines():
            try:
                options = config.get(ename,{}).get('options',{})
                defaults = config.get(ename,{}).get('defaults',{})
                en = create_engine(ename, options=options, defaults=defaults)
                self.engines.append(en)

                languages = config.get(ename,{}).get('languages',{})
                for lang, conf in languages.items():
                    en.configure(language=lang, **conf)
            except TTSError:
                pass

        for en in self.engines:
            self.languages.update(en.languages.keys())

        langid.set_languages(self.languages)

        if not self.languages:
            raise TTSError('No supported languages')

    def classify(self, txt):
        ranks = []
        for lang, score in langid.rank(txt):
            if lang in self.preferred_languages:
                score *= self.preferred_factor
            ranks.append((lang, score))
        ranks.sort(key=lambda x:x[1], reverse=True)
        return ranks[0][0]

    def get_engine_for_lang(self, lang):
        for en in self.engines:
            if lang in en.languages.keys():
                return en
        raise TTSError('Could not match language')

    def say(self, txt):
        lang = self.classify(txt)
        self.get_engine_for_lang(lang).say(txt, language=lang)

