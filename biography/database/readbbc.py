from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = []
        self.depth = 0
        self.article = False
        self.button = False
        self.section = False
        self.figure = False
        self.header = False
        self.void_elements = ['meta', 'link', 'img']
        self.badlist = []
        self.badnum = 0
        self.title = ''
        self.published = ''
        self.text = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'time' and self.published == '' and self.article:
            self.published = attrs[1][1]

        
        if tag == 'button':
            self.button = True
        if tag == 'article':
            self.article = True
        if tag == 'section':
            self.section = True
        if tag == 'figure':
            self.figure = True
        if tag == 'header':
            self.header = True

        self.depth += 1
        self.stack.append(tag)

        if tag == 'div' and len(attrs) > 0 and (
            attrs[0][1] == 'unordered-list-block' or
            attrs[0][1] == 'crosshead-block' or
            attrs[0][1] == 'social-embed-block' or 
            attrs[0][1] == 'image-block' or
            attrs[0][1] == 'share-tools-panel' or
            attrs[0][1] == 'include-html' or
            'StyledMediaContainer' in attrs[0][1] or
            'StyledMetadata'  in attrs[0][1]):
            self.badnum += 1
            self.badlist.append(True)
        else:
            self.badlist.append(False)

        if tag in self.void_elements:
            self.depth -= 1
            self.stack.pop()
            self.badlist.pop()
            # print('void')

        if self.article and not self.button and not self.section and not self.figure and self.badnum == 0:
            # print("Encountered an beg tag :", tag, self.depth, attrs)
            #a = input()
            pass

    def handle_endtag(self, tag):
        self.depth -= 1
        if len(self.stack) != 0: # Mark Zuckerberg!!!!
            self.stack.pop()

        if self.article and not self.button and not self.section and not self.figure and self.badnum == 0:
            # print("Encountered an end tag :", tag, self.depth + 1)
            # a = input()
            pass

        if len(self.badlist) != 0 and self.badlist[-1] == True: # Mark Zuckerberg!!!!
            self.badnum -= 1
        if len(self.badlist) != 0: # Mark Zuckerberg!!!!
            self.badlist.pop()

        if tag == 'article':
            self.article = False
        if tag == 'button':
            self.button = False
        if tag == 'section':
            self.section = False
        if tag == 'figure':
            self.figure = False
        if tag == 'header':
            self.header = False

    def handle_data(self, data):
        if self.article and not self.button and not self.section and not self.figure and self.badnum == 0:
            # print("Encountered some data  :", data)
            if self.title == '':
                self.title = data
            elif self.header:
                pass
            else:
                if self.text != '' and self.text[-1] != ' ':
                    self.text += ' '
                self.text += data
            # a = input()

def readbbc(html):
    parser = MyHTMLParser()
    parser.feed(html)

    return parser.title, parser.published, parser.text