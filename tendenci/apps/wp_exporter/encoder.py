from builtins import str

class XML():
    def __init__(self, version="1.0", encoding="UTF-8"):
        self.content = '<?xml version="%s" encoding="%s"?>\n' % (version, encoding)

    def write(self, text, depth=0):
        txt = ""
        for i in range(0, depth):
            txt += "    "
        txt += str(text) + "\n"
        self.content += txt

    def open(self, name, attrs={}, depth=0):
        txt = ""
        for i in range(0, depth):
            txt += "    "
        self.content += txt
        self.content += "<%s" % name
        for key in attrs:
            self.content += ' %s = "%s"' % (key, attrs[key])
        self.content += ">\n"

    def close(self, name, depth=0):
        txt = ""
        for i in range(0, depth):
            txt += "    "
        self.content += txt
        self.content += "</%s>\n" % name
