# -*- coding: utf-8-*-
import sys
import logging
import functools
if sys.version_info < (3, 3):
    from distutils.spawn import find_executable  # pylint: disable=E0611
else:
    from shutil import which as find_executable  # pylint: disable=E0611


def check_executable(executable):
    """
    Checks if an executable exists in $PATH.
    Arguments:
        executable -- the name of the executable (e.g. "echo")
    Returns:
        True or False
    """
    logger = logging.getLogger(__name__)
    logger.debug("Checking executable '%s'...", executable)
    executable_path = find_executable(executable)
    found = executable_path is not None
    if found:
        logger.debug("Executable '%s' found: '%s'", executable, executable_path)
    else:
        logger.debug("Executable '%s' not found", executable)
    return found


def process_options(valid_options, _options, error):
    unknown_options = set(_options.keys()).difference(valid_options.keys())
    if unknown_options:
        raise error('Unknown options: %s' % ', '.join(unknown_options))

    options = dict((key, _options.get(key, val.get('default', None))) for key, val in valid_options.items())
    for option in options.keys():
        val = options[option]
        data = valid_options[option]
        typ = data['type']
        if typ not in ['int', 'float', 'str', 'enum', 'bool']:
            raise error('Bad type: %s for option %s' % (typ, option), ['int', 'float', 'str', 'enum', 'bool'])
        keys = data.keys()
        if typ == 'int':
            val = int(float(val))
        if typ == 'float':
            val = float(val)
        if typ in ['int', 'float']:
            if 'min' in keys:
                if val < data['min']:
                    raise error('Bad %s: %s' % (option, val), 'Min is %s' % data['min'])
            if 'max' in keys:
                if val > data['max']:
                    raise error('Bad %s: %s' % (option, val), 'Max is %s' % data['max'])
        if typ == 'enum':
            if val not in data['values']:
                raise error('Bad %s value: %s' % (option, val), data['values'])
        if typ == 'bool':
            val = True if str(val).lower() in ['y', '1', 'yes', 'true', 't'] else False
        options[option] = val
    return options


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer
