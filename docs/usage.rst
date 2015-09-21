Usage
=====

talkey module:
--------------

.. autofunction:: talkey.enumerate_engines

.. autofunction:: talkey.create_engine

.. autoclass:: talkey.Talkey
    :members:

.. autoexception:: talkey.TTSError


Engine options:
---------------

espeak:
^^^^^^^
.. autoclass:: talkey.engines.EspeakTTS

festival:
^^^^^^^^^
.. autoclass:: talkey.engines.FestivalTTS

flite:
^^^^^^
.. autoclass:: talkey.engines.FliteTTS

pico:
^^^^^
.. autoclass:: talkey.engines.PicoTTS

mary:
^^^^^
.. autoclass:: talkey.engines.MaryTTS

google:
^^^^^^^
.. autoclass:: talkey.engines.GoogleTTS


Voice options:
--------------

generic:
^^^^^^^^

``language``
    Language of voice

``voice``
    Specific voice to use

espeak:
^^^^^^^
Config options:

``pitch_adjustment``
    pitch_adjustment option

    :type: int
    :default: 50
    :min: 0
    :max: 99
``variant``
    variant option

    :type: enum
    :default: m3
    :values: , croak, f1, f2, f3, f4, f5, klatt, klatt2, klatt3, klatt4, m1, m2, m3, m4, m5, m6, m7, whisper, whisperf
``words_per_minute``
    words_per_minute option

    :type: int
    :default: 150
    :min: 80
    :max: 450
