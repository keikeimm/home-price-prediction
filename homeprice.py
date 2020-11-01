from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import time

#suumo大岡山の賃貸情報1ページ目
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ra=013&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&ek=021505520&rn=0215'

#データ取得
result = requests.get(url)
c = result.content

#HTMLのコードをsoupに入れる。
soup = BeautifulSoup(c)

#物件リストの部分を切り出し,id:js-bukkennListに囲まれたところがそう？
summary = soup.find("div",{'id':'js-bukkenList'})

#ページ数を取得、たぶん35ページ[1,2,3,4,5……35]
body = soup.find("body")
#'class':'pagination pagination_set-nav'はページを切り替えるところに該当するコード
pages = body.find_all("div",{'class':'pagination pagination_set-nav'})
pages_text = str(pages)
pages_split = pages_text.split('</a></li>\n</ol>')
#まだ情報が多いためリストにする
pages_split0 = pages_split[0]
pages_split1 = pages_split0[-3:]
pages_split2 = pages_split1.replace('>','')
pages_split3 = int(pages_split2)
#大岡山の場合pages_split3に35が格納される。

#URLを入れるリスト
urls = []

#1ページ目を格納、最初の大岡山のURLは1ページ目だけ！35ページ分入れる！
urls.append(url)

#2ページ目から最後のページまでを格納
#1ページ目と2ページ目以降でURLの構造が違うためわけておこなった！
for i in range(pages_split3-1):
    pg = str(i+2)
    url_page = url + '&pn=' + pg
    urls.append(url_page)

name = [] #マンション名
address = [] #住所
locations0 = [] #立地1つ目（最寄駅/徒歩~分）
locations1 = [] #立地2つ目（最寄駅/徒歩~分）
locations2 = [] #立地3つ目（最寄駅/徒歩~分）
age = [] #築年数
height = [] #建物高さ
floor = [] #階
rent = [] #賃料
admin = [] #管理費
others = [] #敷/礼/保証/敷引,償却
floor_plan = [] #間取り
area = [] #専有面積

#各ページで以下の動作をループ
for url in urls:
    #物件リストを切り出し
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c)
    summary = soup.find("div",{'id':'js-bukkenList'})
    
    #マンション名、住所、立地（最寄駅/徒歩~分）、築年数、建物高さが入っているcassetteitemを全て抜き出し
    cassetteitems = summary.find_all("div",{'class':'cassetteitem'})

    #各cassetteitemsに対し、以下の動作をループ
    for i in range(len(cassetteitems)):
        #各建物から売りに出ている部屋数を取得
        tbodies = cassetteitems[i].find_all('tbody')
        
        #マンション名取得
        subtitle = cassetteitems[i].find_all("div",{
            'class':'cassetteitem_content-title'})
        subtitle = str(subtitle)
        subtitle_rep = subtitle.replace(
            '[<div class="cassetteitem_content-title">', '')
        subtitle_rep2 = subtitle_rep.replace(
            '</div>]', '')

        #住所取得
        subaddress = cassetteitems[i].find_all("li",{
            'class':'cassetteitem_detail-col1'})
        subaddress = str(subaddress)
        subaddress_rep = subaddress.replace(
            '[<li class="cassetteitem_detail-col1">', '')
        subaddress_rep2 = subaddress_rep.replace(
            '</li>]', '')
        
        #部屋数だけ、マンション名と住所を繰り返しリストに格納（部屋情報と数を合致させるため）
        for y in range(len(tbodies)):
            name.append(subtitle_rep2)
            address.append(subaddress_rep2)

        #立地を取得
        sublocations = cassetteitems[i].find_all("li",{
            'class':'cassetteitem_detail-col2'})
        
        #立地は、1つ目から3つ目までを取得（4つ目以降は無視）
        for x in sublocations:
            cols = x.find_all('div')
            for i in range(len(cols)):
                text = cols[i].find(text=True)
                for y in range(len(tbodies)):
                    if i == 0:
                        locations0.append(text)
                    elif i == 1:
                        locations1.append(text)
                    elif i == 2:
                        locations2.append(text)
                        
        #築年数と建物高さを取得
        #cassetteitem_detail-col3に格納されている
        tbodies = cassetteitems[i].find_all('tbody')
        col3 = cassetteitems[i].find_all("li",{
            'class':'cassetteitem_detail-col3'})
        #col3の中身は<div>築15年</div><div>3階建て</div>みたいな感じつまりi=0は築年数
        for x in col3:
            cols = x.find_all('div')
            for i in range(len(cols)):
                text = cols[i].find(text=True)
                for y in range(len(tbodies)):
                    if i == 0:
                        age.append(text)
                    else:
                        height.append(text)

    #階、賃料、管理費、敷/礼/保証/敷引,償却、間取り、専有面積が入っているtableを全て抜き出し
    tables = summary.find_all('table')

    #各建物（table）に対して、売りに出ている部屋（row）を取得
    rows = []
    for i in range(len(tables)):
        rows.append(tables[i].find_all('tr'))

    #各部屋に対して、tableに入っているtext情報を取得し、dataリストに格納
    data = []
    for row in rows:
        for tr in row:
            cols = tr.find_all('td')
            for td in cols:
                text = td.find(text=True)
                data.append(text)

    #dataリストから、階、賃料、管理費、敷/礼/保証/敷引,償却、間取り、専有面積を順番に取り出す
    index = 0
    for item in data:
        if '階' in item:
            floor.append(data[index])
            rent.append(data[index+1])
            admin.append(data[index+2])
            others.append(data[index+3])
            floor_plan.append(data[index+4])
            area.append(data[index+5])
        index +=1
    
    #プログラムを2秒間停止する
    #time.sleep(2)

#築年数が対応していない可能性あり！
# print(age)

#各リストをシリーズ化
name = Series(name)
address = Series(address)
locations0 = Series(locations0)
locations1 = Series(locations1)
locations2 = Series(locations2)
age = Series(age)
height = Series(height)
floor = Series(floor)
rent = Series(rent)
admin = Series(admin)
others = Series(others)
floor_plan = Series(floor_plan)
area = Series(area)

#各シリーズをデータフレーム化
suumo_df = pd.concat([name, address, age, locations0, locations1, locations2, height, floor, rent, admin, others, floor_plan, area], axis=1)
print(suumo_df)

#築年数が対応していない！他にも対応していないデータがあるかもしれない！