import pipes
import logging
import subprocess
import tempfile
from abc import ABCMeta, abstractmethod

from talkey import diagnose

class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta

    @classmethod
    def has_audio_output(cls):
        return diagnose.check_executable('aplay')

    @classmethod
    @abstractmethod
    def is_available(cls):
        pass

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def get_languages(self):
        pass

    @abstractmethod
    def say(self, phrase, *args):
        pass

    def play(self, filename):
        # FIXME: Use platform-independent audio-output here
        # See issue jasperproject/jasper-client#188
        cmd = ['aplay', '-D', 'plughw:1,0', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg) for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)



