class XML():
    def __init__(self, version="1.0", encoding="UTF-8"):
        self.content = "<?xml version='%s' encoding='%s'?>\n" % (version, encoding)
        
    def write(self, text):
        self.content += str(text) + "\n"
        
    def open(self, name, attrs={}):
        self.content += "<%s" % name
        for key in attrs.keys():
            self.content += " %s = %r" % (key, attrs[key])
        self.content += ">\n"
        
    def close(self, name):
        self.content += "</%s>\n" % name
    
