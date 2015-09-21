Getting Started
===============

Installation
------------

Install from pypi:

.. code-block:: shell

    pip install talkey

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
* Google TTS (cloud hosted) Requires:

    .. code-block:: shell

        pip install gTTS

Usage
-----

At its simplest use case:

.. code-block:: python

    import talkey
    tts = talkey.Talkey()
    tts.say('Old McDonald had a farm')

If you get a ``talkey.base.TTSError: No supported languages`` error, it means that you don't have a supported TTS engine installed. Please see below.

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

Installing TTS engines
----------------------

Ubuntu/Debian:
^^^^^^^^^^^^^^

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

For mbrola and en1 voice (example, there are many other mbrola- packages):

.. code-block:: shell

    sudo apt-get install mbrola-en1

Windows:
^^^^^^^^

Install eSpeak:

    Go to http://espeak.sourceforge.net/download.html and download and install ``setup_espeak-<version>.exe``

For mbrola and its voices:

    Go to http://espeak.sourceforge.net/mbrola.html and download and install ``MbrolaTools<version>.exe`` and follow directions to install voices from  http://www.tcts.fpms.ac.be/synthesis/mbrola/mbrcopybin.html

For google TTS:

    install python package gTTS

    Download ffmpeg from http://ffmpeg.zeranoe.com/builds/

    Extract with 7Zip, and add the \bin folder to the PATH.

    e.g.:
        extract to C:\ffmpeg and add C:\ffmpeg\bin to the PATH

    (In cmd.exe you should be able to just run ffmpeg and see it showing information, then it is working right)

