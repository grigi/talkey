######
talkey
######

Simple Text-To-Speech (TTS) interface library with multi-language and multi-engine support.

.. image:: https://travis-ci.org/grigi/talkey.svg
    :target: https://travis-ci.org/grigi/talkey?branch=master
.. image:: https://coveralls.io/repos/grigi/talkey/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/grigi/talkey?branch=master

Documentation: http://talkey.readthedocs.org/

Rationale
=========

I was really intrigued by the concept of jasper, a voice-controlled interface.
I needed it to be multi-lingual like me, so this library is my attempt to make having the
TTS engines multi-lingual. A lot of this code is inspired by the Jasper project.

System Requirements
===================

* Python 2.7 or later
* An installed TTS engine (see below for help installing one)
* macOS (tested on 10.11 and 10.12), Linux (Ubuntu, Debian), Windows

Basic Usage
===========

Install from pypi:

.. code-block:: shell

    pip install talkey

At its simplest use case:

.. code-block:: python

    import talkey
    tts = talkey.Talkey()
    tts.say('Old McDonald had a farm')

If you get a ``talkey.base.TTSError: No supported languages`` error, it means that you don't have a supported TTS engine installed. Please see below.

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


For best results you should configure it:

.. code-block:: python

    import talkey
    tts = talkey.Talkey(
        # These languages are given better scoring by the language detector
        # to minimise the chance of it detecting a short string completely incorrectly.
        # Order is not important here
        preferred_languages=['en', 'af', 'el', 'fr'],

        # The factor by which preferred_languages gets their score increased, defaults to 80.0
        preferred_factor=80.0,

        # The order of preference of using a TTS engine for a given language.
        # Note, that networked engines (Google, Mary) is disabled by default, and so is dummy
        # default: ['google', 'mary', 'espeak', 'festival', 'pico', 'flite', 'dummy']
        # This sets eSpeak as the preferred engine, the other engines may still be used
        #  if eSpeak doesn't support a requested language.
        engine_preference=['espeak'],

        # Here you segment the configuration by engine
        # Key is the engine SLUG, in this case ``espeak``
        espeak={
            # Specify the engine options:
            'options': {
                'enabled': True,
            },

            # Specify some default voice options
            'defaults': {
                    'words_per_minute': 150,
                    'variant': 'f4',
            },

            # Here you specify language-specific voice options
            # e.g. for english we prefer the mbrola en1 voice
            'languages': {
                'en': {
                    'voice': 'english-mb-en1',
                    'words_per_minute': 130
                },
            }
        }
    )
    tts.say('Old McDonald had a farm')

Installing TTS engines
======================

Ubuntu/Debian:
--------------

For festival:

.. code-block:: shell

    sudo apt-get install festival

For flite:

.. code-block:: shell

    sudo apt-get install flite

For SVOX Pico:

.. code-block:: shell

    sudo apt-get install libttspico-utils

For eSpeak:

.. code-block:: shell

    sudo apt-get install espeak

For mbrola and en1 voice:

.. code-block:: shell

    sudo apt-get install mbrola-en1

Windows:
--------

Install eSpeak:

    Go to http://espeak.sourceforge.net/download.html and download and install ``setup_espeak-<version>.exe``

For mbrola and its voices:

    Go to http://espeak.sourceforge.net/mbrola.html and download and install ``MbrolaTools<version>.exe`` and follow directions to install voices from  http://www.tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html

For google TTS:

    install python package gTTS

    Download ffmpeg from http://ffmpeg.zeranoe.com/builds/

    Extract with 7Zip, and add the \\bin folder to the PATH.

    e.g.:
        extract to C:\\ffmpeg and add C:\\ffmpeg\\bin to the PATH

    (In cmd.exe you should be able to just run ffmpeg and see it showing information, then it is working right)
