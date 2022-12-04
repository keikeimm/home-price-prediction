# 必要なライブラリをインポート
import pandas as pd
import numpy as np

file_name = "all23.csv"
df_oookayama = pd.read_csv(file_name, sep='\t', encoding='utf-8')
# 敷金と礼金は一つ一つのデータ

# axis=0は縦方向に連結、ignore_indes=Trueは初めに与えられたindexを無視する。
df = pd.concat([df_oookayama], axis=0, ignore_index=True)
# Unnamed: 0というカラムが勝手に追加されている可能性があるため取り除く。
df.drop(['Unnamed: 0'], axis=1, inplace=True)
# 立地を「路線+駅」と「徒歩〜分」に分割
splitted1 = df['立地1'].str.split('歩', expand=True)
splitted1.columns = ['立地11', '立地12']
splitted2 = df['立地2'].str.split('歩', expand=True)
splitted2.columns = ['立地21', '立地22']
splitted3 = df['立地3'].str.split('歩', expand=True)
splitted3.columns = ['立地31', '立地32']
# 分割したカラムを結合
df = pd.concat([df, splitted1, splitted2, splitted3], axis=1)
df.drop(['立地1', '立地2', '立地3'], axis=1, inplace=True)

# 住所を「東京都」「〜区」「市町村番地」に分割
splitted6 = df['住所'].str.split('区', expand=True)
splitted6.columns = ['区', '市町村']
splitted6['区'] = splitted6['区'] + '区'
splitted6['区'] = splitted6['区'].str.replace('東京都', '')

# 立地を「路線」「駅」「徒歩〜分」に分割
splitted7 = df['立地11'].str.split('/', expand=True)
splitted7.columns = ['路線1', '駅1']
splitted7['徒歩1'] = df['立地12']
splitted8 = df['立地21'].str.split('/', expand=True)
splitted8.columns = ['路線2', '駅2']
splitted8['徒歩2'] = df['立地22']
splitted9 = df['立地31'].str.split('/', expand=True)
splitted9.columns = ['路線3', '駅3']#なんかエラー起きた
splitted9['徒歩3'] = df['立地32']

# 結合
# 記事ではsplitted6がここよりも下に存在してエラーが起きた、あれは何だったのだろうか
df = pd.concat([df, splitted6, splitted7, splitted8, splitted9], axis=1)

# 不要なカラムを削除
df.drop(['立地11', '立地12', '立地21', '立地22', '立地31', '立地32'], axis=1, inplace=True)

# 「賃料」がNAの行を削除#カラムが賃料のところからdropna()で欠陥(NaN)がある行を削除
df = df.dropna(subset=['賃料'])

# エンコードをcp932に変更しておく（これをしないと、replaceできない）
# 階すうも数値としてあつかえそう
# 記事は保証金、敷引、償却がある
df['賃料'].str.encode('cp932')
df['敷金'].str.encode('cp932')
df['礼金'].str.encode('cp932')
df['管理費'].str.encode('cp932')
df['築年数'].str.encode('cp932')
df['専有面積'].str.encode('cp932')
df['徒歩1'].str.encode('cp932')
df['徒歩2'].str.encode('cp932')
df['徒歩3'].str.encode('cp932')


# 数値として扱いたいので、不要な文字列を削除
df['賃料'] = df['賃料'].str.replace(u'万円', u'')
df['敷金'] = df['敷金'].str.replace(u'万円', u'')
df['礼金'] = df['礼金'].str.replace(u'万円', u'')
df['管理費'] = df['管理費'].str.replace(u'円', u'')
df['築年数'] = df['築年数'].str.replace(u'新築', u'0')  # 新築は築年数0年とする
df['築年数'] = df['築年数'].str.replace(u'築', u'')
df['築年数'] = df['築年数'].str.replace(u'年', u'')
df['築年数'] = df['築年数'].str.replace(u'以上', u'')
df['専有面積'] = df['専有面積'].str.replace(u'm', u'')
df['徒歩1'] = df['徒歩1'].str.replace(u'分', u'')
df['徒歩2'] = df['徒歩2'].str.replace(u'分', u'')
df['徒歩3'] = df['徒歩3'].str.replace(u'分', u'')

# 「-」を0に変換
df['管理費'] = df['管理費'].replace('-', 0)
df['敷金'] = df['敷金'].replace('-', 0)
df['礼金'] = df['礼金'].replace('-', 0)

# 文字列から数値に変換#to_nemericで数値化できる！
df['賃料'] = pd.to_numeric(df['賃料'])
df['管理費'] = pd.to_numeric(df['管理費'])
df['敷金'] = pd.to_numeric(df['敷金'])
df['礼金'] = pd.to_numeric(df['礼金'])
df['築年数'] = pd.to_numeric(df['築年数'])
df['専有面積'] = pd.to_numeric(df['専有面積'])
df['徒歩1'] = pd.to_numeric(df['徒歩1'])
df['徒歩2'] = pd.to_numeric(df['徒歩2'])
df['徒歩3'] = pd.to_numeric(df['徒歩3'])

# 単位を合わせるために、管理費以外を10000倍。
df['賃料'] = df['賃料'] * 10000
df['敷金'] = df['敷金'] * 10000
df['礼金'] = df['礼金'] * 10000

# 管理費は実質的には賃料と同じく毎月支払うことになるため、「賃料+管理費」を家賃を見る指標とする
df['賃料+管理費'] = df['賃料'] + df['管理費']

# 敷金/礼金は同じく初期費用であり、どちらかが適用されるため、合計を初期費用を見る指標とする
df['敷/礼'] = df['敷金'] + df['礼金']

# 階を数値化。地下はマイナスとして扱う
splitted10 = df['階'].str.split('-', expand=True)
splitted10.columns = ['階1', '階2']
# 「1-2階」のような表示の場合は、低い方（この場合は1階）に合わせる。このため-でスプリット
splitted10['階1'].str.encode('cp932')
splitted10['階1'] = splitted10['階1'].str.replace(u'階', u'')
splitted10['階1'] = splitted10['階1'].str.replace(u'B', u'-')
splitted10['階1'] = splitted10['階1'].str.replace(u'M2', u'')
splitted10['階1'] = pd.to_numeric(splitted10['階1'])

df = pd.concat([df, splitted10], axis=1)

# 建物高さを数値化。地下は無視。
df['建物の高さ'].str.encode('cp932')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下1地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下2地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下3地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下4地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下5地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下6地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下7地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下8地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'地下9地上', u'')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'平屋', u'1')
df['建物の高さ'] = df['建物の高さ'].str.replace(u'階建', u'')
df['建物の高さ'] = pd.to_numeric(df['建物の高さ'])

# index(行？）を振り直す（これをしないと、以下の処理でエラーが出る）
# なんでだろう？？
df = df.reset_index(drop=True)

# 間取りを「部屋数」「DK有無」「K有無」「L有無」「S有無」に分割
# 新しいカラムを作った？
df['間取りDK'] = 0
df['間取りK'] = 0
df['間取りL'] = 0
df['間取りS'] = 0
df['間取り'].str.encode('cp932')
df['間取り'] = df['間取り'].str.replace(u'ワンルーム', u'1')  # ワンルームを1に変換

# だいにんぐきっちんがあれば間取りDKのx行目に1を入れる
for x in range(len(df)):
    if 'DK' in df['間取り'][x]:
        df.loc[x, '間取りDK'] = 1
df['間取り'] = df['間取り'].str.replace(u'DK', u'')

# キッチンも同様
for x in range(len(df)):
    if 'K' in df['間取り'][x]:
        df.loc[x, '間取りK'] = 1
df['間取り'] = df['間取り'].str.replace(u'K', u'')

# リビングも同様
for x in range(len(df)):
    if 'L' in df['間取り'][x]:
        df.loc[x, '間取りL'] = 1
df['間取り'] = df['間取り'].str.replace(u'L', u'')

# Sはサービスルームらしい
for x in range(len(df)):
    if 'S' in df['間取り'][x]:
        df.loc[x, '間取りS'] = 1
df['間取り'] = df['間取り'].str.replace(u'S', u'')

# カラム「間取り」に残った部屋数を数値に変換。
df['間取り'] = pd.to_numeric(df['間取り'])

# カラムを入れ替えて、csvファイルとして出力
df = df[['名前', '住所', '区', '市町村', '間取り', '間取りDK', '間取りK', '間取りL', '間取りS', '築年数', '建物の高さ', '階1', '専有面積', '賃料+管理費', '敷/礼',
         '路線1', '駅1', '徒歩1', '路線2', '駅2', '徒歩2', '路線3', '駅3', '徒歩3', '賃料', '管理費',
                '敷金', '礼金']]
# カッコを二重にしないとデータフレームにならない(シリーズになる）

#なんでかわからないが「1戸建て・その他」に分類される住宅に欠損がある
df['階1'] = df['階1'].fillna(1)

#if　notは欠損があるやつを取り除くために入れてる。
for x in range(len(df)):
    if not df['徒歩2'][x] is None:
        if df['徒歩1'][x] > df['徒歩2'][x]:
            df['徒歩1'][x], df['路線1'][x], df['駅1'][x], df['徒歩2'][x], df['路線2'][x], df['駅2'][x] = df['徒歩2'][x], df['路線2'][x], df['駅2'][x], df['徒歩1'][x], df['路線1'][x], df['駅1'][x]
        
    if not df['徒歩3'][x] is None:
        if df['徒歩1'][x] > df['徒歩3'][x]:
            df['徒歩1'][x], df['路線1'][x], df['駅1'][x], df['徒歩3'][x], df['路線3'][x], df['駅3'][x] = df['徒歩3'][x], df['路線3'][x], df['駅3'][x], df['徒歩1'][x], df['路線1'][x], df['駅1'][x]


#suumo_oookayama_data.csvは全データ,suumo_oookayama_for.analysis.csvは分析に必要な数値データと名前だけ
df = df.drop(["住所","区","市町村","路線1","駅1","路線2","駅2",
    "徒歩2","路線3","駅3","徒歩3","賃料","管理費","敷金","礼金"], axis=1)

df.to_csv(f'preprocess_{file_name}.csv', sep='\t', encoding='utf-8', index=False)
