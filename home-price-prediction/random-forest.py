import pandas as pd #pandasのインポート
from sklearn.model_selection import train_test_split #データ分割用
from sklearn.ensemble import RandomForestClassifier #ランダムフォレスト
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
from pandas import Series, DataFrame
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from tqdm import tqdm
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import r2_score

df_23ku = pd.read_csv('suumo_23ku_for.analysis.csv', sep='\t', encoding='utf-16')
# axis=0は縦方向に連結
df = pd.concat([df_23ku], axis=0)
# Unnamed: 0というカラムが勝手に追加されている可能性があるため取り除く。
df.drop(['Unnamed: 0'], axis=1, inplace=True)
#カテゴリー変数処理はしてあるのでdf = pd.get_dummies(df,drop_first = True)は必要ない
analysis_data = df.drop(['名前','賃料+管理費'], axis=1)
train_z = df['名前']
train_y = df['賃料+管理費']
train_X = analysis_data

df_ooo = pd.read_csv('suumo_oookayama_around_for.analysis.csv', sep='\t', encoding='utf-16')
# axis=0は縦方向に連結
df2 = pd.concat([df_ooo], axis=0)
# Unnamed: 0というカラムが勝手に追加されている可能性があるため取り除く。
df2.drop(['Unnamed: 0'], axis=1, inplace=True)

#カテゴリー変数処理はしてあるのでdf = pd.get_dummies(df,drop_first = True)は必要ない
analysis_data2 = df2.drop(['名前','賃料+管理費'], axis=1)
test_z = df2['名前']
test_y = df2['賃料+管理費']
test_X = analysis_data2
'''
print(np.where(np.isnan(train_X)))
print(np.where(np.isnan(train_y)))

#適当にいい感じの割合でサンプルと乱数を設定した。
train_X, test_X, train_y, test_y, train_z, test_z = train_test_split(x, y, z, test_size=0.2, random_state=1)
'''
# ランダムサーチ(パラメータ範囲指定)用のパラメータ 1~100
paramR = {'n_estimators':np.arange(120), 'criterion':["gini", "entropy"], "min_samples_split": [i for i in range(2, 11)], "min_samples_leaf": [i for i in range(1, 11)]}

RFC_rand = RandomizedSearchCV(estimator=RandomForestClassifier(random_state=0), param_distributions=paramR, \
                        scoring='r2', cv=3)
RFC_rand.fit(train_X, train_y)

print('ランダムサーチn_estimators  :  %d'  %RFC_rand.best_estimator_.n_estimators)
print(RFC_rand.best_estimator_.max_depth)
print('ランダムサーチ予測値  :  %.3f' %r2_score(test_y, RFC_rand.predict(test_X)))

#ハイパーパラメータを調整しない場合との比較
# 決定木クラスの初期化と学習
model = RandomForestClassifier(random_state=0)
model.fit(train_X,train_y)

print(r2_score(test_y, model.predict(test_X)))
#max_depthはNone
print(model.max_depth)
#indes名を統一しないとちゃんと結合できない！
#ランダムサーチの結果をcsvに保存
prediction = pd.Series(RFC_rand.predict(test_X), index=test_y.index)
dfprice = pd.concat([test_z, test_y, prediction], axis=1)
dfprice.columns = ['名前', '実際の値段', '予測値段']

dfprice.to_csv('oookayama＿around＿prediction2.csv', sep='\t', encoding='utf-16')
'''
# グリッドサーチ(パラメータ候補指定)用のパラメータ10種
paramG = {'n_estimators':[1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120],  'criterion':["gini", "entropy"], "min_samples_split": [i for i in range(2, 11)], "min_samples_leaf": [i for i in range(1, 11)]}

RFC_grid = GridSearchCV(estimator=RandomForestClassifier(random_state=0), param_grid=paramG, \
                        scoring='r2', cv=3)
RFC_grid.fit(train_X, train_y)
print('グリッドサーチn_estimators   :  %d'  %RFC_grid.best_estimator_.n_estimators)
print('グリッドサーチ予測値  :  %.3f' %r2_score(test_y, RFC_grid.predict(test_X)))
'''