
# Import for python 3, else 2.7
try:
  from html.parser import HTMLParser
except ImportError:
  from HTMLParser import HTMLParser


class Clean(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)
