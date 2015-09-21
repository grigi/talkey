Getting Started
===============

Installation
------------

Install from pypi:

.. code-block:: shell

    pip install talkey

Usage
-----

At its simplest use case:

.. code-block:: python

    import talkey
    tts = talkey.Talkey()
    tts.say('Old McDonald had a farm')

Engines supported
^^^^^^^^^^^^^^^^^

By default it will try to locate and use the local instances of the following TTS engines:

* Flite
* SVOX Pico
* Festival
* eSpeak
* mbrola via eSpeak

Installing one or more of those engines should allow the libary to function and generate speech.

It also supports the following networked TTS Engines:

* MaryTTS (needs hosting)
* Google TTS (cloud hosted)

Simple configuration
^^^^^^^^^^^^^^^^^^^^

For best results you should configure it:

.. code-block:: python

    import talkey
    tts = talkey.Talkey(
        preferred_languages = ['en', 'af', 'el', 'fr'],
        espeak = {
            'languages': {
                'en': {
                    'voice': 'english-mb-en1',
                    'words_per_minute': 130
                },
            }
        })
    tts.say('Old McDonald had a farm')
