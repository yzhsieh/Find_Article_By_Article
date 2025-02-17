# DSP final project


## 動機
通常在各個網路論壇中，如果想要找尋某個議題的討論文章，只能使用論壇給予的搜尋功能，但如果關鍵字下錯，甚至有些文章標題沒有打出關鍵字，則就沒有辦法找到所有想要的結果。
而因為課堂上有教到article summary的相關知識，讓我覺得可以往這個方向開發"以文搜文"的系統。然而就算是相同討論主題的文章也不太可能產生相同的summary，因此我退而使用tf-idf，想要找出每篇文章的關鍵詞，再透過比對關鍵詞的方式來找出相關主題的文章

雖然感覺蠻簡單的但我google"以文搜文"沒有看到什麼人或是網站有做這件事情，不知道是因為太簡單了還是成果不太好

## 設計
首先利用爬蟲程式爬取論壇的文章並進行整理(此處使用PTT八卦版或NTU版之文章)，接著使用JieBa套件對每個文章都進行斷詞，然後計算這些文章的tf-idf。最後透過得到的tf-idf取得每個文章的關鍵詞。
進行檢索的時候也是把文章抓取下來後並斷詞，接著使用前面的td-idf檔案來取得關鍵詞，最後拿這些關鍵詞比較文章庫，取出比較相近的文章資訊。

### 流程圖如下：
![](https://i.imgur.com/m4CTadn.png)


## 紀錄
### 爬蟲
本範例是爬PTT的討論版(有測試過NTU版以及Gossip版)
本階段主要會遇到的問題除了爬蟲的語法之外，因為八卦版會限制18歲以上才能觀看，所以進入時會跳確認頁面，我們可藉由request時加入 "cookies={'over18': '1'}" 來避免這頁跳出來。

### 文章整理
雖然每篇文章都會出現的字(如"標題"、"日期"字樣)因tf-idf可以忽略，但仍有一些每篇文章都不一樣的內容(如網址、作者id)可能被誤判為關鍵詞，因此需要拿掉。
標題、作者id等因為出現地方固定，可以在爬蟲時就忽略掉，但因網址出現的地方不固定，而且作者也有可能在文章中留下網址(如貼圖連結，轉貼連結)，因此我利用以下regex來過濾掉文中所有網址
```python
    final = re.sub(r'https?:\/\/[\w.\/]*\B', '', final, flags=re.MULTILINE)
```


### tf-idf
如果直接使用JieBa來計算tf-idf會出現很奇怪的結果，因此我們必須要自己來產生所有詞的idf。
不過自己寫的idf會遇到一些問題，會有一些透明字元被辨認出來，但在JieBa載入idf時就會出錯，因此必須手動挑掉他，以下是我實驗時曾出現過的錯誤狀況(後來有進行預處理，但還是無法挑掉所有錯誤，我是去jieba package中的tdidf.py改寫一些code來幫助我把錯誤忽略or挑出來)
  1. 空白
  2. \n (在文件中是完全空白的一行)
  3. 有蠻多奇怪的空白 (在文件中只看的到機率)

### 關鍵詞比對
如果找出的關鍵詞組不錯的話，這部分就蠻容易的。
我的作法是將每篇文章的關鍵詞組與要檢索的關鍵詞組比對，看有幾個相同的關鍵詞，再輸出相同數量大於一個threshold的所有文章。

## 成果
(略，有興趣可以去看report中的此部分)
## 討論與改進
　在程式我直接使用JieBa的內建詞庫來斷詞，一開始在看斷出來的詞時覺得有一些些會斷在怪怪的地方，但如果要改進的話必須要使用自訂義詞庫，建立詞庫必須手動(我還沒想到自動的方式)而且曠日費時。而後來因為結果表現還不錯我就沒有打算要弄自訂義詞庫。

　另外，JieBa的斷詞有提供三種模式：全模式、精確模式以及搜尋模式。我使用的是預設的精確模式，全模式則是會將斷詞的所有可能都列出來(ex. 我走進台灣大學 -> 我 / 我走 / 走進 / 台灣 / 台灣大學 / 大學)，因為我認為斷出來的結果會使取關鍵字時取太多同義但長相不同的字，且這樣也會導致資料處理量變大，所以我沒有使用。至於搜尋模式是提取出類似給搜尋引擎用的(實際上就有點像提取關鍵字)，但因為這樣會破壞掉文章結構，也不知道它會把哪些東西刪去，因此我也沒有使用這個模式。

　最後，目前關鍵字的比對方式是單純比較有多少個重複，並輸出重複個數大於一定量的文章，我其實覺得有一點點不嚴謹，如果想要得到更好的結果可能可以考慮其他方式，或是增加參考的東西(如標題)。

## 使用方式
1. 爬蟲(ptt_crawer.py)
可以修改code中的config variables區塊，下面為他們的意義
```python
ONLY_TODAY = 0		#是否只要爬今天
NOPUSH= 1		#是否要忽略推文 (!!尚未實裝，設為0會出錯!!)
MaxPageNum = 2370 			#最多要爬幾頁 (以PTT網頁版為主，一頁最多20篇)
BOARD_URL = '/bbs/NTU/index.html' 	#要爬的板(複製版的部分)
output_path = 'NTU_2370.json'		#輸出檔案的名字
```
2. 產生關鍵字庫 & 測試
目前尚未將產生字庫與測試的指令分開，因每次跑不需要太多時間。
function功能：
```python
init()	#讀入 json檔案
gen_seg_list()	#把文檔斷詞
gen_vocab_count_and_idf() #計算文檔中的所有詞以及其idf
jieba.analyse.set_idf_path("./myidf.txt")	#載入自訂idf檔案       
cal_tfidf() #對每個文章提取關鍵詞
get_similiar_article(url)			#對URL中的文章尋找相關文章
```
如果重複使用一樣的文章庫，則不用再跑gen_seg_list()和gen_vocab_count_and_idf()

此code一樣有config variables，設定如下：
```python
input_path = 'gossiping.json'	#要讀入的文檔
keyWordNUM = 50			#每個文章取多少關鍵詞
maxResultNUM = 20		#輸出相關文章時，最多可以有多少結果
rankThres = 5			#輸出相關文章時，rank至少要多少
```
### Data set
- [PTT NTU板約18000篇文章](https://drive.google.com/drive/folders/1xHPEqWP3_WONVXe20CA7CSibQ_PWhXxo?usp=sharing)
- [PTT NTU板約47000篇文章](https://drive.google.com/drive/folders/135SzvoRDF2bva9gmd4iITBeFKKMgqnB0?usp=sharing)
- [PTT Gossip板約19000篇文章](https://drive.google.com/drive/folders/1G4DpHrtVvafY-FTMnXfRKaAiyeZsDmzq?usp=sharing)
- [PTT Gossip版約180000篇文章](https://drive.google.com/drive/folders/1DiAwSjRNBtbsXxyaxQHSy2CM0Rqknnya?usp=sharing)


## Reference
- https://github.com/fxsjy/jieba
- https://stevenloria.com/tf-idf/
- https://www.wikiwand.com/zh-tw/Tf-idf
- https://atedev.wordpress.com/2007/11/23/%E6%AD%A3%E8%A6%8F%E8%A1%A8%E7%A4%BA%E5%BC%8F-regular-expression/