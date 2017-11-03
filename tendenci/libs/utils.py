import sys
import os.path

def python_executable():
    """
    Get the path of the python interpreter that is running the current process,
    for use when spawning a new python process.

    If a virtualenv is used and this interpreter was started without first
    calling `source /path/to/venv/bin/activate` then
    subprocess.Popen('python', ...) and other similar calls will run the default
    system Python instead of the appropriate virtualenv Python.  To ensure that
    the appropriate virtualenv Python is enabled, use this function's return
    value instead of 'python' in such calls.
    """
    path = sys.executable
    if os.path.basename(path).startswith('python'):
        # Typical case, when running under a normal python interpreter named
        # "python" or perhaps something like "python2.7".
        return path
    if os.path.basename(path) == 'uwsgi':
        # When running under uWSGI, the "uwsgi" binary is the interpreter for
        # the current process, but it cannot be used like the normal "python"
        # binary to spawn arbitrary new python processes, so we must determine
        # the path to the associated "python" binary.
        import uwsgi
        path = uwsgi.opt.get('home')
        if path is not None:
            path += '/bin/python'
            if os.path.isfile(path):
                return path
    # The current interpreter's executable has an unexpected name.  To avoid
    # issues if this is an embedded interpreter that cannot be used like the
    # normal "python" binary (similar to the "uwsgi" binary), try to find an
    # associated "python" binary.
    path = sys.prefix+'/bin/python'
    if os.path.isfile(path):
        return path
    # If all else fails, run whatever "python" is in the PATH.  If
    # `source /path/to/venv/bin/activate` was called before starting this
    # interpreter, then this should run the appropriate virtualenv Python,
    # otherwise this should run the system Python.
    return 'python'
