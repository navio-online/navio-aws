from subprocess import check_call, CalledProcessError
import sys
import os
import fnmatch
import contextlib
import random
import functools
import json
from datetime import date, datetime


@contextlib.contextmanager
def safe_cd(path):
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)


def execute(script, *args):
    popen_args = [script]

    for arg in args:
        if type(arg) == list:
            popen_args.extend(arg)
        else:
            popen_args.append(arg)

    try:
        return check_call(popen_args, shell=False)
    except CalledProcessError as ex:
        # print(ex)
        # sys.exit(ex.returncode)
        raise ex
    except Exception as ex:
        print('Error running script '
              '{} with args {}: {}'.format(script, args, ex))
        sys.exit(1)


def ls(walk_dir, *patterns):
    """
    Returns a generator yielding files matching the given patterns
    :type dir_path: str
    :type patterns: [str]
    :rtype : [str]
    :param dir_path: Directory to search for files/directories under. Defaults to current dir.
    :param patterns: Patterns of files to search for. Defaults to ["*"]. Example: ["*.json", "*.xml"]
    """
    path_patterns = patterns or ["*"]

    result = list()
    for root_dir, dir_names, file_names in os.walk(walk_dir):
        filter_partial = functools.partial(fnmatch.filter, file_names)

        for file_name in itertools.chain(*map(filter_partial, path_patterns)):
            result.append(os.path.join(root_dir, file_name))

    return result


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def generatePassword(**kwargs):
    try:
        xrange
    except NameError:
        xrange = range

    _kwargs = {
        'len': 8,
        'symbols': "!@#$%^&*()_+-=[]{}",
        'digits': '0123456789',
        'upper_count': 2,
        'digits_count': 1,
        'symbols_count': 1
    }
    _kwargs.update(kwargs)

    _kwargs['len'] = max(_kwargs['len'],
                         1 +
                         int(_kwargs.get('upper_count')) +
                         min(len(_kwargs.get('digits')),
                             _kwargs.get('digits_count')) +
                         min(len(_kwargs.get('symbols')),
                             _kwargs.get('symbols_count'))
                         )

    rnd = random.sample(
        range(0, int(_kwargs.get('len'))),
        int(_kwargs.get('upper_count')) +
        min(len(_kwargs.get('digits')), _kwargs.get('digits_count')) +
        min(len(_kwargs.get('symbols')), _kwargs.get('symbols_count'))
    )

    lowcase_letters = "abcdefghijklmnopqrstuvwxyz"
    upcase_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # generate base password string using lowcase alphabet
    result = "".join([random.SystemRandom().choice(lowcase_letters)
                      for _ in xrange(int(_kwargs.get('len')))])

    # put uppercase if any
    if _kwargs.get('upper_count') and _kwargs.get('upper_count') > 0:
        for x in range(0, _kwargs.get('upper_count')):
            rndUpcaseLetter = random.randint(0, len(upcase_letters)-1)
            result = replaceIdx(result, rnd.pop(), upcase_letters[
                rndUpcaseLetter])

    if _kwargs.get('digits_count') and _kwargs.get('digits_count') > 0:
        for x in range(0, _kwargs.get('digits_count')):
            rndDigitIdx = random.randint(0, len(_kwargs.get('digits'))-1)
            result = replaceIdx(result, rnd.pop(), _kwargs.get('digits')[
                rndDigitIdx])

    if _kwargs.get('symbols_count') and _kwargs.get('symbols_count') > 0:
        for x in range(0, _kwargs.get('symbols_count')):
            rndSymbolIdx = random.randint(0, len(_kwargs.get('symbols'))-1)
            result = replaceIdx(result, rnd.pop(), _kwargs.get('symbols')[
                rndSymbolIdx])

    return result


def replaceIdx(s, idx, char):
    return s[:idx] + char + s[idx+1:]


_pyntexit_registered = False


def _pyntexit_register():
    global _pyntexit_registered
    if not _pyntexit_registered:
        import atexit
        atexit.register(_pyntexit)
        _pyntexit_registered = True


def _pyntexit():
    import datetime
    print('Script exited at {}'.format(
        datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
    import platform
    if platform.system() == 'Darwin':
        execute('osascript', '-e',
                'display notification "Script finished" with title "Pynt"')


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def dump(obj):
    print(json.dumps(obj, indent=1, default=json_serial))
