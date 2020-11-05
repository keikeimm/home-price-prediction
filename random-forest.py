import pandas as pd #pandasのインポート
from sklearn.model_selection import train_test_split #データ分割用
from sklearn.ensemble import RandomForestClassifier #ランダムフォレスト
import pandas as pd
from pandas import Series, DataFrame

df_oookayama = pd.read_csv('suumo_oookayama_for.analysis.csv', sep='\t', encoding='utf-16')

# axis=0は縦方向に連結
df = pd.concat([df_oookayama], axis=0)
# Unnamed: 0というカラムが勝手に追加されている可能性があるため取り除く。
df.drop(['Unnamed: 0'], axis=1, inplace=True)

#カテゴリー変数処理はしてあるのでdf = pd.get_dummies(df,drop_first = True)は必要ない

analysis_data = df.drop(['名前','賃料+管理費'], axis=1)
z = df['名前']
y = df['賃料+管理費']
x = analysis_data

#適当にいい感じの割合でサンプルと乱数を設定した。
x_analysis, x_test, y_analysis, y_test, z_analysis, z_test  = train_test_split(x, y, z, test_size=0.2, random_state=1)

clf = RandomForestClassifier(random_state=100)
clf.fit(x_analysis, y_analysis)
#モデルの当てはまりの良さ
print('score=', clf.score(x_test, y_test))
#ランダムに選ばれた5%の予測値をプリント
'''
print(z_test)
print(y_test)
#予測値！
print(clf.predict(x_test))
'''
#indes名を統一しないとちゃんと結合できない！
prediction=pd.Series(clf.predict(x_test), index=y_test.index)
dfprice = pd.concat([z_test, y_test, prediction], axis=1)
dfprice.columns = ['名前', '実際の値段', '予測値段']

dfprice.to_csv('home-price-prediction.csv', sep='\t', encoding='utf-16')