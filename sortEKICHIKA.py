# 必要なライブラリをインポート
import pandas as pd
import numpy as np
#numpyは必要ないと思いましたが念のため入れときました。

df_oookayama = pd.read_csv('suumo_oookayama_data.csv', sep='\t', encoding='utf-16')

# axis=0は縦方向に連結
df = pd.concat([df_oookayama], axis=0)
# Unnamed: 0というカラムが勝手に追加されている可能性があるため取り除く。
df.drop(['Unnamed: 0'], axis=1, inplace=True)

for x in range(len(df)):
    if not df['徒歩2'][x] is None:
        if df['徒歩1'][x] > df['徒歩2'][x]:
            df['徒歩1'][x], df['路線1'][x], df['駅1'][x], df['徒歩2'][x], df['路線2'][x], df['駅2'][x] = df['徒歩2'][x], df['徒歩2'][x], df['駅2'][x], df['徒歩1'][x], df['路線1'][x], df['駅1'][x]
        
    if not df['徒歩3'][x] is None:
        if df['徒歩1'][x] > df['徒歩3'][x]:
            df['徒歩1'][x], df['路線1'][x], df['駅1'][x], df['徒歩3'][x], df['路線3'][x], df['駅3'][x] = df['徒歩3'][x], df['徒歩3'][x], df['駅3'][x], df['徒歩1'][x], df['路線1'][x], df['駅1'][x]
        
df.to_csv('suumo_oookayama_data2.csv', sep='\t', encoding='utf-16')

df = df.drop(["住所","区","市町村","路線1","駅1","路線2","駅2",
    "徒歩2","路線3","駅3","徒歩3","賃料","管理費","敷金","礼金"], axis=1)

df.to_csv('suumo_oookayama_for.analysis.csv', sep='\t', encoding='utf-16')
