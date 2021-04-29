import nltk
nltk.download('punkt')

class ShortNewsItem():
    def __init__(self, name, news, bio):
        self.name = name
        self.news = news
        self.bio = bio

class ShortNews():
    def __init__(self):
        self.items = []

    def find(self, name):
        for i, item in enumerate(self.items):
            if name == item.name:
                return i
        return None

def create_news(articles, blacklist, model, correct_str):
    fullstr = ''
    partstr = ''
    for i, article in enumerate(articles):
        if article.content != '':
            content = correct_str(article.content, first_ignore=False)
        else:
            content = ''

        for sent in nltk.tokenize.sent_tokenize(content):
            bad = False
            for blacksubstr in blacklist:
                if blacksubstr in sent:
                    bad = True
                    break
            if not bad:
                if partstr != '' and partstr[-1] != '\n':
                    partstr += ' '
                partstr += sent
            partstr += '\n'
            
        if (i + 1) % 20 == 0 or i + 1 == len(articles):
            if fullstr != '' and fullstr[-1] != '\n':
                fullstr += '\n'
            if len(articles) <= 20:
                fullstr += model(partstr, num_sentences=30)
            else:
                fullstr += model(
                    partstr, 
                    num_sentences=int(300 / len(articles)))
            partstr = ''
    return fullstr

def create_bio(summary, correct_str, n_sent):
    bios = nltk.tokenize.sent_tokenize(correct_str(summary, first_ignore=False))[:n_sent]
    bio = ''
    for pbio in bios:
      if bio != '':
        bio += ' '
      bio += pbio
    return bio