######
talkey
######

Simple Test-To-Speech (TTS) interface library with multi-language and multi-engine support.

.. image:: https://travis-ci.org/grigi/talkey.svg
    :target: https://travis-ci.org/grigi/talkey?branch=master
.. image:: https://coveralls.io/repos/grigi/talkey/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/grigi/talkey?branch=master

Rationale
=========

I was really intrigued by the concept of jasper, a voice-controlled interface.
I needed it to be multi-lingual like me, so this library is my attempt to make having the
TTS engines multi-lingual. A lot of this code is based of code from the Jasper project,
just refactored to fit purpose and to be testable.

Basic Usage
===========

Install from pypi:

.. code-block:: shell

    pip install talkey

At its simplest use case:

.. code-block:: python

    import talkey
    talkey.configure()
    talkey.say('Old McDonald had a farm')

But for best results you should configure it:

.. code-block:: python

    CONF = {
        # These languages are given better scoring by the language detector
        # to minimise the chance of it detecting a short string completely incorrectly.
        # Order is not important here
        'preferred_languages': [
            'en',
            'af',
            'el',
            'fr',
        ],
        # Here you segment the configuration by engine
        'espeak-tts': {
            # Specify some engine defaults (globally)
            'defaults': {
                    'words_per_minute': 150,
                    'variant': 'f4',
            },
            # Here you specify language-specific configuration
            # e.g. for english we prefer the mbrola en1 voice
            'languages': {
                'en': {
                    'voice': 'english-mb-en1',
                    'words_per_minute': 130
                },
            }
        }
    }

    import talkey
    talkey.configure(CONF)
    talkey.say('Old McDonald had a farm')
