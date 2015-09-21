# -*- coding: utf-8-*-
import sys
import logging
import socket
import functools
import pkgutil
if sys.version_info < (3, 3):
    from distutils.spawn import find_executable as _find_executable  # pylint: disable=E0611
else:
    from shutil import which as _find_executable  # pylint: disable=E0611

def find_executable(executable):
    '''
    Finds executable in PATH

    Returns:
        string or None
    '''
    logger = logging.getLogger(__name__)
    logger.debug("Checking executable '%s'...", executable)
    executable_path = _find_executable(executable)
    found = executable_path is not None
    if found:
        logger.debug("Executable '%s' found: '%s'", executable, executable_path)
    else:
        logger.debug("Executable '%s' not found", executable)
    return executable_path

def check_executable(executable):
    '''
    Checks if an executable exists in $PATH.
    Arguments:
        executable -- the name of the executable (e.g. "echo")
    Returns:
        True or False
    '''
    return find_executable(executable) is not None


def check_network_connection(server, port):
    '''
    Checks if jasper can connect a network server.
    Arguments:
        server -- (optional) the server to connect with (Default:
                  "www.google.com")
    Returns:
        True or False
    '''
    logger = logging.getLogger(__name__)
    logger.debug("Checking network connection to server '%s'...", server)
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(server)
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection((host, port), 2)
        sock.close()
    except Exception:  # pragma: no cover
        logger.debug("Network connection not working")
        return False
    logger.debug("Network connection working")
    return True


def check_python_import(package_or_module):
    '''
    Checks if a python package or module is importable.
    Arguments:
        package_or_module -- the package or module name to check
    Returns:
        True or False
    '''
    logger = logging.getLogger(__name__)
    logger.debug("Checking python import '%s'...", package_or_module)
    loader = pkgutil.get_loader(package_or_module)
    found = loader is not None
    if found:
        logger.debug("Python %s '%s' found",
                     "package" if loader.is_package(package_or_module)
                     else "module", package_or_module)
    else:  # pragma: no cover
        logger.debug("Python import '%s' not found", package_or_module)
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
        if typ not in ['int', 'float', 'str', 'enum', 'bool', 'exec']:
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
        if typ == 'exec':
            if isinstance(val, list):
                vals = val
                for val in vals:
                    val = find_executable(val)
                    if val:
                        break
            else:
                val = find_executable(val)
        options[option] = val
    return options
