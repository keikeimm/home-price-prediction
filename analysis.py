import pandas as pd #pandasのインポート!!!
from sklearn.model_selection import train_test_split #データ分割用
from sklearn.ensemble import RandomForestClassifier #ランダムフォレスト
from sklearn.ensemble import RandomForestRegressor #ランダムフォレスト
from sklearn.model_selection import RandomizedSearchCV
import numpy as np
from pandas import Series, DataFrame
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from tqdm import tqdm
from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import r2_score
from sklearn.neural_network import MLPRegressor

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

random_search = {'batch_size': [1000, 1500],
               'hidden_layer_sizes': [(2000, 2000), (2000, 2000, 2000)],
               'max_iter': [200, 600],
               'random_state': [0]}

model = RandomizedSearchCV(MLPRegressor(), random_search, cv=3,
                                   n_jobs=-1, scoring='r2', random_state=0)
model.fit(train_X, train_y)
#ハイパーパラメータを調整しない場合との比較
# 決定木クラスの初期化と学習

#indes名を統一しないとちゃんと結合できない！
#ランダムサーチの結果をcsvに保存
prediction = pd.Series(model.predict(test_X), index=test_y.index)
dfprice = pd.concat([test_z, test_y, prediction], axis=1)
dfprice.columns = ['名前', '実際の値段', '予測値段']

dfprice.to_csv('oookayama＿around＿prediction.csv', sep='\t', encoding='utf-16')

print(model.best_estimator_, '1')
print(r2_score(test_y, model.predict(test_X)), '2')
cvres = model.cv_results_
print(cvres, '3')
for score, params in zip(cvres['mean_test_score'], cvres['params']):
    print(score, params)

'''
# ランダムサーチ(パラメータ範囲指定)用のパラメータ 1~100
params = {'n_estimators':[i*10 for i in range(17)], 'max_depth':[i for i in range(6, 14)], "min_samples_split": [i for i in range(3, 11)], "min_samples_leaf": [i for i in range(3, 11)]}

RFC_rand = RandomizedSearchCV(estimator=RandomForestRegressor(random_state=0), param_distributions=params, \
                        scoring='r2', cv=3)

RFC_rand.fit(train_X, train_y)
print('ランダムサーチパラメータ', RFC_rand.best_params_)
print('ランダムサーチ予測値  :  %.3f' %r2_score(test_y, RFC_rand.predict(test_X)))
print('ランダムサーチ元データ  :  %.3f' %r2_score(train_y, RFC_rand.predict(train_X)))
'''