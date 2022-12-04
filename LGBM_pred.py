import pandas as pd  # pandasのインポート
import lightgbm as lgb
import optuna
from sklearn.model_selection import KFold, cross_validate


class lgbm_:
    def __init__(self, x_train, y_train, x_test):
        """

        Args:
            x_train (DataFrame): 学習データのデータフレーム
            y_train (Series): 正解ラベルのシリーズ
            x_test (DataFrame): テストデータのデータフレーム
        """
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test

    def objective(self, trial):
        """

        Args:
            trial (): ハイパーパラメータをチューニンングするためのインスタンス

        Returns:
            array: チューニングした値のROCAUC
        """
        # パラメータを設定
        params = {
            "objective": "regression",
            "metric": "rmse",
            "verbosity": -1,
            "boosting_type": "gbdt",
            "num_leaves": trial.suggest_int("num_leaves", 10, 200),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_loguniform("learning_rate", 1e-8, 1.0),
            "reg_alpha": trial.suggest_loguniform("reg_alpha", 1e-5, 1.0),
            "reg_lambda": trial.suggest_loguniform("reg_lambda", 1e-5, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 80),
            "random_state": 8,
        }
        # モデルにチューニングしたパラメータを渡す
        model = lgb.LGBMRegressor(**params, n_estimators=1000)
        # KFold分割し、評価を行う
        kf = KFold(n_splits=4, shuffle=True, random_state=8)
        scores = cross_validate(
            model, X=self.x_train, y=self.y_train, scoring="neg_mean_squared_error", cv=kf
        )
        return scores["test_score"].mean()

    def pred(self, search=False):
        """_summary_

        Args:
            search (bool, optional): ハイパーパラメータをチューニンングするかどうか. Defaults to False.
        Returns:
            array : 予測値を返すnumpyの配列
        """
        # チューニングする場合
        if search:
            study = optuna.create_study(direction="maximize")
            study.optimize(self.objective, timeout=600)

            # サーチしたパラメータの表示
            best_params = study.best_params
            params = {
                "objective": "regression",
                "metric": "rmse",
                "verbosity": -1,
                "boosting_type": "gbdt",
                "num_leaves": best_params["num_leaves"],
                "max_depth": best_params["max_depth"],
                "learning_rate": best_params["learning_rate"],
                "reg_alpha": best_params["reg_lambda"],
                "reg_lambda": best_params["reg_lambda"],
                "min_child_samples": best_params["min_child_samples"],
                "random_state": 42,
            }
            print(params)
        # 調整したハイパーパラメータを渡す
        else:
            params = {
                "objective": "regression",
                "metric": "rmse",
                "verbosity": -1,
                "boosting_type": "gbdt",
                "num_leaves": 200,
                "max_depth": 8,
                "random_state": 42,
            }

        model2 = lgb.LGBMRegressor(**params, n_estimators=1000)
        model2.fit(self.x_train, self.y_train)
        pred = model2.predict(self.x_test, num_iteration=model2.best_iteration_)
        return pred  # 各モデルの平均


file_name = "all23"
df_23 = pd.read_csv(
    f"preprocess_{file_name}.csv",
    sep="\t",
    encoding="utf-16",
)

analysis_data = df_23.drop(["名前", "賃料+管理費"], axis=1)
train_z = df_23["名前"]
train_y = df_23["賃料+管理費"]
train_X = analysis_data

pfile_name = "ohimachi"
df_pred = pd.read_csv(
    f"preprocess_{pfile_name}.csv", sep="\t", encoding="utf-16"
)

analysis_data2 = df_pred.drop(["名前", "賃料+管理費"], axis=1)
test_z = df_pred["名前"]
test_y = df_pred["賃料+管理費"]
test_X = analysis_data2

# lightGBMによる予測
model = lgbm_(train_X, train_y, test_X)
pred_price = model.pred(search=True)

# ランダムサーチの結果をcsvに保存
pred_price = pd.Series(pred_price, index=test_y.index)
dfprice = pd.concat([test_z, test_y, pred_price], axis=1)
dfprice.columns = ["名前", "実際の値段", "予測値段"]

dfprice.to_csv(f"{file_name}_prediction.csv", sep="\t", encoding="utf-16")
