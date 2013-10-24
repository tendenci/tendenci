import subprocess


class SubProcessManager(object):
    process = None

    @staticmethod
    def set_process(args):
        if SubProcessManager.process is None:
            p = subprocess.Popen(args)
            SubProcessManager.process = p

    @staticmethod
    def poll_process():
        if SubProcessManager.process is None:
            return None
        else:
            return SubProcessManager.process.poll()
