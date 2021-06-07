import wikipedia, unidecode, re
from readbbc import readbbc
from selenium import webdriver
from googlesearch import search
from tqdm import tqdm


def correct_str(string : str, first_ignore=True):
    if string[-1] != '\n':
            string += '\n'

    string = string.replace(' Jr.', ' Jr')
    string = string.replace(' Inc.', ' Inc')
    string = string.replace(' No.', ' No')
    string = string.replace(' U.S.', ' US')
    string = string.replace(' F.C.', ' FC')
    string = string.replace('== References ==', '')
    string = string.replace('\t', ' ')
    string = string.replace('\r', '')
    string = unidecode.unidecode(string)

    while (string[0] == '\n' or (
        (not first_ignore) and string[0] == ' ')):
        string = string[1:]

    string_old = ''
    while string_old != string:
        string_old = string
        string = string.replace('  ', ' ')
        string = string.replace(' ,', ',')
        string = string.replace(' .', '.')
        string = string.replace(' :', ':')
        string = string.replace(' ;', ';')
        string = string.replace('\n,', ',')
        string = string.replace('\n.', '.')
        string = string.replace('\n:', ':')
        string = string.replace('\n;', ';')

        string = string.replace('\n\n', '\n')
        string = string.replace(' \n', '\n')
        string = string.replace('\n ', '\n')
        
    string = re.sub(r'\.([a-zA-Z])', r'. \1', string)
    string = re.sub(r'\,([a-zA-Z])', r', \1', string)
    string = string.replace('. com', '.com')
    string = string.replace('. co', '.co')
    string = string.replace('. uk', '.uk')
    string = string.replace('. Ru ', '.Ru ')
    string = string.replace('. ru', '.ru')

    return string

class Article():
    def __init__(self, title : str, date : str, content : str):
        self.title = title
        self.date = date
        self.content = content

class Person():
    def __init__(self, names, wikiname, bbclink, pass_articles, wikitext):
        self.names = names
        self.wikiname = wikiname
        self.bbclink = bbclink
        self.summary = ''

        if wikiname is not None:
            wikipage = wikipedia.page(wikiname)
            summary = wikipage.summary
        else:
            summary = wikitext

        brackets = 0
        for c in summary:
            if c == '(':
                brackets += 1

            if brackets == 0:
                self.summary += c

            if c == ')':
                brackets = max(0, brackets - 1)

        self.summary = correct_str(self.summary)

        firis = self.summary.find(' is ')
        firws = self.summary.find(' was ')
        if firis == -1:
            firis = 1000000
        if firws == -1:
            firws = 1000000
        cutps = min(firis, firws)
        if cutps == 1000000:
            print("bad wiki")
        else:
            self.summary = self.summary[cutps:]
        print(self.summary)

        self.articles = []

        if pass_articles:
            return
        
        sname = ''
        for name in names:
            if sname != '':
                sname += ' OR '
            sname += '\"' + name + '\"'
        sname = '('+sname+')'

        print(sname + " site:" + bbclink)
        sites = search(
            sname + " site:" + bbclink, num_results=100)
        print(sites)
        for i, site in enumerate(sites):
            site = site.replace('/av/', '/')
            sites[i] = ''
            nnum = 0
            for c in site:
                sites[i] += c
                if c.isnumeric():
                    nnum += 1
                else:
                    nnum = 0
                if nnum == 8:
                    break
            if nnum != 8:
                sites[i] = 'z'
        
        sites = list(dict.fromkeys(sites))
        if 'z' in sites:
            sites.remove('z')

        print('Got', len(sites), 'articles!')

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--silent")
        driver = webdriver.Chrome('database/chromedriver.exe', options=options)

        for site in tqdm(sites):
            driver.get(site)
            html = driver.page_source
            title, date, content = readbbc(html)

            in_content = False
            for name in names:
                in_content = in_content or (name in title) or (name in content)
            if in_content:
                self.articles.append(Article(title, date, content))
        
        self.articles.sort(key=lambda val: val.date)
        print(len(self.articles), 'added to dataset!')
        driver.quit()

class DataBase():
    def __init__(self):
        self.persons = []

    def add(self, names, wikiname, bbclink='https://www.bbc.com/news/', wikitext=None):
        exists = False
        for person in self.persons:
            if names[0] == person.names[0]:
                exists = True
                break
        if exists:
            print(names[0], "is already in database!")
            return

        person = Person(names, wikiname, bbclink, False, wikitext)
        self.persons.append(person)
        print(names[0], 'added to database!')
        print()
        return len(person.articles)

    def set_bio_from_file(self, name):
        exists = None
        for i, person in enumerate(self.persons):
            if name in person.names:
                exists = i
                break
        if exists is None:
            print(name, "is not in database!")
            return

        f = open('./database/wikibios/' + name + '.txt', 'r')
        self.persons[i].summary = f.read()
        f.close()

    def find(self, name):
        for i, person in enumerate(self.persons):
            if name in person.names:
                return i
        return -1

    def remove(self, name):
        exists = None
        for i, person in enumerate(self.persons):
            if name in person.names:
                exists = i
                break
        if exists is None:
            print(name, "is not in database!")
            return
        del self.persons[exists]
        print(name, 'removed from database!')
        