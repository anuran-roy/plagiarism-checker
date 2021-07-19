nltk.download("stopwords")

from nltk.tokenize import sent_tokenize, word_tokenize
import requests
from bs4 import BeautifulSoup
import time
import json
import re
import string
from nltk.corpus import stopwords

stopwords = stopwords.words('english')

def clean_string(text):
    text = text.lower()
    text=''.join([word for word in text if word not in string.punctuation])
    text=''.join([word for word in text.split() if word not in stopwords])

    return text

def getResults(text):
    text = text.replace(" ","+")
    print(text)
    url = f'https://www.bing.com/search?q={text}&qs=n&form=QBRE&sp=-1&pq={text.lower()}"' # f'https://www.google.com?q="{text}&oq={text}&sourceid=chrome&ie=UTF-8"'  # "https://dataquestio.github.io/web-scraping-pages/simple.html"

    # Crafting the proper request to fool Google
    header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'}
    
    page = requests.get(url, headers= header, allow_redirects=True)

    content = BeautifulSoup(page.content, 'html.parser')
    # print(content)
    return content

def process(content):
    res = {}
    res["headlines"] = []
    res["result-stats"] = []
    res["cards"] = []

    for i in content.find_all('h2'):
        entry = i.find('a')
        lnk = None
        if len(str(entry)) >= 28:
            lnk = str(entry)[28:str(entry).index('" target')]
        res["headlines"].append((i.get_text(), lnk))  # list(content.find_all('h3', attrs = {"class": "LC20lb DKV0Md"}))
        # res["cards"].append(i.get_text().replace("/strong&gt;","").replace("&lt;","").replace("strong&gt;",""))

    for i in content.find_all('p'):
        res["cards"].append(i.get_text().replace("/strong&gt;","").replace("&lt;","").replace("strong&gt;",""))
    
    res["result-stats"]=[i.get_text() for i in content.find_all('span', attrs = {"class": "sb_count"})][0]   # [i.get_text() for i in content.find_all('div', attrs = {"id": "result-stats"})]  # [i.get_text() for i in content.find_all('p')]

    # for i in res.keys():
    #     print(res[i])

    return res
def web_search(sentence_list):

    search_results = {}

    for i in range(len(sentence_list)):
        cnt = getResults(sentence_list[i])
        search_results[sentence_list[i]] = process(cnt)
        time.sleep(2)

        print(f"Completion percent: {i/len(sentence_list)*100}%")

    return search_results

def similarity(s1, s2):
    l1 = word_tokenize(s1)
    l2 = word_tokenize(s2)

    v1 = []; v2 = []

    set1 = {w for w in l1 if not w in stopwords}
    set2 = {w for w in l2 if not w in stopwords}

    rvect = set1.union(set2)

    for w in rvect:
        if w in set1:
            v1.append(1)
        else:
            v1.append(0)
        
        if w in set2:
            v2.append(1)
        else:
            v2.append(0)
    
    score = 0

    for i in range(len(rvect)):
        score += v1[i]*v2[i]
    div = float((sum(v1)*sum(v2))**0.5)

    if div > 0:
        score /= div
    else:
        score = 0
    return score

def scorer(sentence_list, sentence_list_web):
    len1 = len(sentence_list)
    len2 = 0
    for i in sentence_list_web:
        len2 += len(i)
    f = 0

    for i in range(len1):
        if sentence_list_web[i] == []:
            f += 1
        else:
            for j in range(len(sentence_list_web[i])):
                f += similarity(sentence_list[i], sentence_list_web[i][j])
    
    f /= len2

    return f

def extractor(resdict):
    slweb = []
    for i in resdict.keys():
        itm = resdict[i]['cards']
        # print(itm)
        slweb.append(itm)

    return slweb


def driver(txt): # Driver code 
    txt = '''{}'''.format(txt)

    sen = []

    sen0 = sent_tokenize(txt)
    for i in sen0:
        sen.append(i)  # (clean_string(i))

    # print(sen)

    results = extractor(web_search(sen))

    scorer_results = scorer(sen, results)

    print(f"Plagiarism = {scorer_results*100}%")

txt = input("Enter text:")
driver(txt)