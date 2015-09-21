TTS Engines
===========

Engine interface
----------------

.. autoclass:: talkey.base.AbstractTTSEngine
    :members:
    :private-members:

Creating your own engine
------------------------

Subclass ``talkey.base.AbstractTTSEngine``, and provide the abstract methods:

.. code-block:: python

    from talkey.base import AbstractTTSEngine

    class SampleTTS(AbstractTTSEngine):
        SLUG = "sample"

        @classmethod
        def _get_init_options(cls):
            # Engine options
            return {
                'enabled': {
                    'description': 'Disabled by default',
                    'type': 'bool',
                    'default': False,
                },
            }

        def _is_available(self):
            # Checks for engine availability/readiness
            return True

        def _get_options(self):
            # Same format as _get_init_options
            # This is the voice options
            return {
                'mooing': {
                    'description': 'Cows sound effect',
                    'type': 'bool',
                    'default': False,
                },
            }

        def _get_languages(self):
            # Dict of languages containing voices
            return {
                'en': {
                    'default': 'english',
                    'voices': {
                        'english': {
                            # Any extra options describing this voice
                            # (for private use)
                        },
                        'cowlish': {
                            # Any extra options describing this voice
                            # (for private use)
                        }
                    }
                },
                ...
            }

        def _say(self, phrase, language, voice, voiceinfo, options):
            # Actually run the phrase through the TTS Engine.
            # All parameters will be always provided for you
            ...

