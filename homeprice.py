#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import time

# 大岡山の賃貸情報1ページ目
url = 'https:'
# データ取得
result = requests.get(url)
c = result.content

# HTMLのコードをsoupに入れる。
soup = BeautifulSoup(c, 'html.parser')

# 物件リストの部分を切り出し,id:js-bukkennListに囲まれたところがそう？
summary = soup.find("div", {'id': 'js-bukkenList'})

# ページ数を取得、たぶん35ページ[1,2,3,4,5……35]
body = soup.find("body")
# 'class':'pagination pagination_set-nav'はページを切り替えるところに該当するコード
pages = body.find_all("div", {'class': 'pagination pagination_set-nav'})
pages_text = str(pages)
pages_split = pages_text.split('</a></li>\n</ol>')
# まだ情報が多いためリストにする
pages_split0 = pages_split[0]
pages_split1 = pages_split0[-3:]
pages_split2 = pages_split1.replace('>', '')
pages_split3 = int(pages_split2)
# 大岡山の場合pages_split3に35が格納される。

# URLを入れるリスト
urls = []

# 1ページ目を格納、最初の大岡山のURLは1ページ目だけ！35ページ分入れる！
urls.append(url)

# 2ページ目から最後のページまでを格納
# 1ページ目と2ページ目以降でURLの構造が違うためわけておこなった！
for i in range(pages_split3-1):
    pg = str(i+2)
    url_page = url + '&pn=' + pg
    urls.append(url_page)
name = []  # マンション名
address = []  # 住所
locations0 = []  # 立地1つ目（最寄駅/徒歩~分）
locations1 = []  # 立地2つ目（最寄駅/徒歩~分）
locations2 = []  # 立地3つ目（最寄駅/徒歩~分）
age = []  # 築年数
height = []  # 建物高さ
floor = []  # 階
rent = []  # 賃料
admin = []  # 管理費
deposit = []
gratuity = []  # 敷/礼/保証/敷引,償却
floor_plan = []  # 間取り
area = []  # 専有面積


def get_informaion_about_home(html_elements, obj_list):
    """
    obj_list[str]: 値を追加したいリスト
    elements[list]: 取り出したい情報だけが含まれているHTMLクラス
    """
    for inculde_value in html_elements:
        element_text = inculde_value.text.split('/n')[0]
        obj_list.append(element_text)
    return obj_list


# 各ページで以下の動作をループ
for url in urls:
    # 物件リストを切り出し
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c)
    summary = soup.find("div", {'id': 'js-bukkenList'})

    # マンション名、住所、立地（最寄駅/徒歩~分）、築年数、建物高さが入っているcassetteitemを全て抜き出し
    cassetteitems = summary.find_all("div", {'class': 'cassetteitem'})

    # 各cassetteitemsに対し、以下の動作をループ
    for i in range(len(cassetteitems)):
        # 各建物から売りに出ている部屋数を取得
        tbodies = cassetteitems[i].find_all('tbody')
        # マンション名取得
        subtitle = cassetteitems[i].find_all("div", {
            'class': 'cassetteitem_content-title'})
        subtitle = str(subtitle)
        subtitle_rep = subtitle.replace(
            '[<div class="cassetteitem_content-title">', '')
        subtitle_rep2 = subtitle_rep.replace(
            '</div>]', '')

        # 住所取得
        subaddress = cassetteitems[i].find_all("li", {
            'class': 'cassetteitem_detail-col1'})
        subaddress = str(subaddress)
        subaddress_rep = subaddress.replace(
            '[<li class="cassetteitem_detail-col1">', '')
        subaddress_rep2 = subaddress_rep.replace(
            '</li>]', '')

        # 部屋数だけ、マンション名と住所を繰り返しリストに格納（部屋情報と数を合致させるため）
        for y in range(len(tbodies)):
            name.append(subtitle_rep2)
            address.append(subaddress_rep2)

        # 立地を取得
        sublocations = cassetteitems[i].find_all("li", {
            'class': 'cassetteitem_detail-col2'})
        # 立地は、1つ目から3つ目までを取得（4つ目以降は無視）
        for x in sublocations:
            cols = x.find_all('div')
            for j in range(len(cols)):
                text = cols[j].find(text=True)
                for y in range(len(tbodies)):
                    if j == 0:
                        locations0.append(text)
                    elif j == 1:
                        locations1.append(text)
                    elif j == 2:
                        locations2.append(text)

        # 築年数と建物高さを取得
        # cassetteitem_detail-col3に格納されている
        tbodies = cassetteitems[i].find_all('tbody')
        col3 = cassetteitems[i].find_all("li", {
            'class': 'cassetteitem_detail-col3'})
        # col3の中身は<div>築15年</div><div>3階建て</div>みたいな感じつまりi=0は築年数
        for x in col3:
            cols = x.find_all('div')
            for q in range(len(cols)):
                text = cols[q].find(text=True)
                for y in range(len(tbodies)):
                    if q == 0:
                        age.append(text)
                    else:
                        height.append(text)

    # 階、賃料、管理費、敷/礼/保証/敷引,償却、間取り、専有面積が入っているtableを全て抜き出し

        # 階
        floors = cassetteitems[i].select(".js-cassette_link")
        for include_value in floors:
            tds = include_value.find_all('td')
            floor_text = tds[2].text.replace(
                "	", "").replace("\n", "").replace("\r", "")
            floor.append(floor_text)
        # 賃料
        rents = cassetteitems[i].select('.cassetteitem_other-emphasis')
        get_informaion_about_home(rents, rent)
        # 管理費
        admins = cassetteitems[i].select(
            '.cassetteitem_price.cassetteitem_price--administration')
        get_informaion_about_home(admins, admin)
        # 敷金
        deposits = cassetteitems[i].select(
            ".cassetteitem_price.cassetteitem_price--deposit")
        get_informaion_about_home(deposits, deposit)
        # 礼金
        gratuitys = cassetteitems[i].select(
            ".cassetteitem_price.cassetteitem_price--deposit")
        get_informaion_about_home(gratuitys, gratuity)
        # 間取り
        floor_plans = cassetteitems[i].select(".cassetteitem_madori")
        get_informaion_about_home(floor_plans, floor_plan)
        # 専有面積
        areas = cassetteitems[i].select(".cassetteitem_menseki")
        get_informaion_about_home(areas, area)
    # プログラムを2秒間停止する
    #time.sleep(2)

# 各リストをシリーズ化
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
deposit = Series(deposit)
gratuity = Series(gratuity)
floor_plan = Series(floor_plan)
area = Series(area)
columns = ['名前', '住所', '立地1', '立地2', '立地3', '築年数',
           '建物の高さ', '階', '賃料', '管理費', '敷金', '礼金', '間取り', '専有面積']
# # 各シリーズをデータフレーム化#axis=1は横に結合
suumo_df = pd.concat([name, address, locations0, locations1, locations2, age,
                      height, floor, rent, admin, deposit, gratuity, floor_plan, area], axis=1)
suumo_df.columns = ['名前', '住所', '立地1', '立地2', '立地3', '築年数',
                    '建物の高さ', '階', '賃料', '管理費', '敷金', '礼金', '間取り', '専有面積']
# csvファイルとして保存
suumo_df.to_csv('suumo_oookayama_around.csv', sep='\t', encoding='utf-16')
