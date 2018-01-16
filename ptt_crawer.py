import requests
import time
import json
from bs4 import BeautifulSoup
import re
### config variables
ONLY_TODAY = 0
NOPUSH= 1
MaxPageNum = 2370
BOARD_URL = '/bbs/NTU/index.html'
output_path = 'NTU_2370.json'
###
PTT_URL = 'https://www.ptt.cc'
# BOARD_URL = '/bbs/Gossiping/index.html'

today = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def get_article(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    soup = BeautifulSoup(resp.text, 'html5lib')
    # print(soup.text)
    main_content = soup.find(id="main-content")
    errcnt = 0
    while main_content == None:
        errcnt += 1
        if errcnt > 5:
            return False
            print("QQQQQ  Can not get this article")
        print("ERROR retrying connect : {}".format(errcnt))
        time.sleep(2)
        resp = requests.get(
        url=url,
        cookies={'over18': '1'}
        )
        soup = BeautifulSoup(resp.text, 'html5lib')
        main_content = soup.find(id="main-content")


    if NOPUSH:
        ptr = main_content.find_all('div', class_="push")
        for a in ptr:
            a.decompose()
    filtered = [ v for v in main_content.stripped_strings if v[0] not in ['※', '◆'] and v[:2] not in ['--'] and v != url ]
    filtered = filtered[8:]
    # print(filtered)
    if len(filtered) == 0:
        return False
    # print(main_content.text)
    # print(filtered)
    final = ''.join(filtered)
    final = re.sub(r'https?:\/\/[\w.\/]*\B', '', final, flags=re.MULTILINE)
    # print(final)
    if NOPUSH:
        return final

def get_titles(dom, date, only_today = True):
    soup = BeautifulSoup(dom, 'html5lib')

    #取得上一頁連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    # print(prev_url)
    #取得本頁面文章資訊
    raw = soup.find_all('div', attrs={'class':'r-ent'})
    # print(len(raw))

    articles = []
    for a in raw:
        date = a.find('div', attrs={'class':'date'}).text.strip() 
        nrec = a.find('div', attrs={'class':'nrec'}).text.strip()
        author = a.find('div', attrs={'class':'author'}).text.strip()                   
        title = a.find('div', attrs={'class':'title'}).text.strip()
        try:
            nrec = int(nrec)
        except ValueError:
            if nrec == '爆':
                nrec = 100
            elif len(nrec) == 0:
                nrec = 0
            elif nrec == 'XX':
                nrec = -100
            elif nrec[0] == 'X':
                nrec = int(nrec[1:]) * (-10)
            else:
                nrec = "DontKnow"
        # 取得文章連結及標題
        if only_today:
            if date != today:
                break
        if a.find('a'):  # 有超連結，表示文章存在，未被刪除
            href = a.find('a')['href']
            print('>>>', title)
            print('>>>', href)
            print()
            article = get_article(PTT_URL + href)
            if article == False:
                continue
            articles.append({
                'date':date,
                'push_count':nrec,
                'author':author,
                'title':title,
                'href':href,
                'article' : article
            })
    return articles,prev_url

def main():
    init_time = time.time()
    current_url = PTT_URL + BOARD_URL
    currrent_page = get_web_page(current_url)
    articles = []
    cnt = 1
    for i in range(MaxPageNum):
        print('Processing #{} page, current articles number : {}  time used : {}'.format(cnt, len(articles), time.time()-init_time))
             
        cnt += 1
        tmp_artciles, prev_url = get_titles(currrent_page, today, only_today = ONLY_TODAY)
        if len(tmp_artciles) == 0:
            break
        articles.extend(tmp_artciles)
        current_url = PTT_URL + prev_url
        currrent_page = get_web_page(current_url)
        if i % 500 == 0 and i != 0:
            print("Saving article for {} pages".format(i))
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)
        
    


    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)
    print('ALL DONE!!!')
    print("Number of articles : ", len(articles))
if __name__ == '__main__':
    main()
    # get_article('https://www.ptt.cc/bbs/Gossiping/M.1515996800.A.716.html')