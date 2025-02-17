# -*- coding: utf-8 -*-
import jieba
import jieba.analyse
import json
import math
import requests
import time
from bs4 import BeautifulSoup
from operator import itemgetter

from ptt_crawer import get_article
### config variables
# input_path = 'gossiping_10000.json'
input_path = 'NTU_2370.json'
keyWordNUM = 50
maxResultNUM = 20
rankThres = 5
###
docunmentNUM = None
PTT_URL = 'https://www.ptt.cc'
raw_dict = {}
###
def init():
    global raw_dict, docunmentNUM
    print("Initializing")
    file = open(input_path, 'r', encoding = 'utf8')
    raw_dict = json.load(file)
    docunmentNUM = len(raw_dict)
    print(" - done, number of articles :",docunmentNUM)


def main():
    pass

def gen_vocab_count_and_idf():
    print("Generating whole vocab list")
    whole_count = {}
    for art in raw_dict:
        for it in art['seg']:
            if it in ['\n', ' ', '　', '\t']:
                continue
            if it not in whole_count:
                whole_count[it] = {'count':1, 'appearence':0, 'idf':None}
            else:
                whole_count[it]['count'] += 1
    print(' - done, number of vocab : {}'.format(len(whole_count)))

    print("Calculating appearence")
    ### calculate appearence
    for it in raw_dict:
        ### make sure anything appear only once
        seg_list = set(it['seg'])
        for a in seg_list:
            if a in whole_count:
                whole_count[a]['appearence'] += 1
    print(' - done')
    print("Calculating idf")
    for it in whole_count:
        whole_count[it]['idf'] = math.log10(docunmentNUM / whole_count[it]['appearence'])
    print(' - done')
    print('Saving whole vocab')
    file = open("./vocab_count.txt", 'w', encoding='utf8')
    for it in whole_count:
        file.write(str(it) + '\t' + str(whole_count[it]) + '\n')
    print(' - done')

    print('Saving myidf')
    file = open('./myidf.txt', 'w', encoding='utf8')
    for it in whole_count:
        file.write(it + ' ' + str(whole_count[it]['idf']) + '\n')
    print('Done')


def gen_seg_list(save = 0):
    # just need to run once if you save it
    print("Generating seg_list")
    for it in raw_dict:
        seg_list = jieba.lcut(it['article'])
        it['seg'] = seg_list
    if save:
        print("saving")
        file = open(input_path, 'w', encoding = 'utf8')
        json.dump(raw_dict, file)
        # print("Generate seg list DONE!!")    
    print(' - done')

def cal_tfidf(save = 0):
    print("Generating tags for all articles")
    global raw_dict
    cnt = 0
    for it in raw_dict:
        if cnt % 1000 == 0:
            print(' - Processing : {}/{}'.format(cnt, len(raw_dict)))
        cnt += 1
        tags = jieba.analyse.extract_tags(it['article'], keyWordNUM)
        # print(it['title'] + ' : ' + ','.join(tags))
        it['tags'] = tags
    if save:
        print("saving")
        if 'seg' in raw_dict[0]:
            print("Poping \'seg\' elements in dict")
            for it in raw_dict:
                # print(it['seg'])
                it['seg'].pop()
        file = open('./final.json', 'w', encoding = 'utf8')
        json.dump(raw_dict, file, indent=2, sort_keys=True, ensure_ascii=False)
        print("DONE!!")     

def get_similiar_article(url, output_path = './result.txt', save = 1):
    global raw_dict
    comp = get_article(url)
    comp_tags = jieba.analyse.extract_tags(comp, keyWordNUM)
    for it in raw_dict:
        rank = 0
        for a in comp_tags:
            if a in it['tags']:
                rank += 1
        it['rank'] = rank
    raw_dict = sorted(raw_dict, key=itemgetter('rank'), reverse=True)
    # for idx in range(20):
    #     print("{}, (rank : {})".format(raw_dict[idx]['title'], raw_dict[idx]['rank']))
    #     print(PTT_URL + raw_dict[idx]['href'])
    #     print(raw_dict[idx]['tags'])
    print("Saving result")
    if save:
        file = open(output_path, 'w', encoding='utf8')
        for idx in range(maxResultNUM):
            if raw_dict[idx]['rank'] < rankThres:
                break
            ptr = raw_dict[idx]
            file.write("Rank : {}\nTitle : {}\n".format(ptr['rank'], ptr['title']))
            file.write("Href : {}\nDate : {}\n".format(ptr['href'], ptr['date']))
            file.write("{}\n".format(ptr['article']))
            file.write('\n\n-----------------------------------------\n\n')

if __name__ == '__main__':
    # main()
    init()

    ### follow two functions only need to run once every time you change a new corpus
    gen_seg_list()  
    gen_vocab_count_and_idf()
    ###
    
    jieba.analyse.set_idf_path("./myidf.txt")        
    cal_tfidf(1)
    get_similiar_article('https://www.ptt.cc/bbs/NTU/M.1515831748.A.B4B.html','1.txt')
    print('----------------------------------------------')
    get_similiar_article('https://www.ptt.cc/bbs/NTU/M.1515490276.A.8E2.html', '2.txt')
    print('----------------------------------------------')
    get_similiar_article('https://www.ptt.cc/bbs/NTU/M.1514881852.A.AFE.html', '3.txt')
