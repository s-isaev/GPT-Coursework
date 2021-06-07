from pickle import TRUE
from typing import List
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

def create_news(
    articles : ShortNews, 
    blacklist : list, 
    model, correct_str) -> str:
    """
    С помощью экстрактивной модели строит строку c выжимкой новостей.
    
    Parameters
    ----------
    articles : ShortNews
        Все новости о человеке
    blacklist : list
        Предложения с этими подстроками нужно удалять
    model
        Экстрактивная модель
    correct_str
        Обработка строки
    """

    fullstr = ''
    partstr = ''
    for i, article in enumerate(articles):
        if article.content != '':
            content = correct_str(article.content, first_ignore=False)
        else:
            content = ''

        for sent in nltk.tokenize.sent_tokenize(content):
            bad = False
            # Только левык предложения не заканчиваются точкой
            if sent[-1] != '.':
                bad = True
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

def cut_news(tokenizer, bio_str, news_str, target_len) -> str:
    """
    Обрезает лишние последние предложения у новостей, что суммарная строка влезла
    """
    old_news_len = len(tokenizer.encode(news_str))
    old_bio_len = len(tokenizer.encode(bio_str))

    print('Length before cut:', old_news_len + old_bio_len)
    res_news = ''
    sent_news = nltk.tokenize.sent_tokenize(news_str)
    for sent in sent_news:
        candidate_news = res_news + ''
        if candidate_news != '' and\
            candidate_news[-1] != ' ' and\
                candidate_news[-1] != '\n':
            candidate_news += ' '
        candidate_news += sent
        if len(tokenizer.encode(candidate_news)) \
            + len(tokenizer.encode(bio_str)) > target_len:
            break
        res_news = candidate_news

    print(bio_str, res_news, sep='\n')
    print(
        'Lengtg after cut:',
        len(tokenizer.encode(res_news)) + len(tokenizer.encode(bio_str))
    )
    return res_news

def create_bio(summary, correct_str, n_sent):
    bios = nltk.tokenize.sent_tokenize(correct_str(summary, first_ignore=False))[:n_sent]
    bio = ''
    for pbio in bios:
        if bio != '' and bio[-1] != ' ' and bio[-1] != '\n':
            bio += ' '
        bio += pbio
    return bio