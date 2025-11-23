import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier
import joblib

url = "https://archive.ics.uci.edu/static/public/45/data.csv"
df = pd.read_csv(url)

cleveland_df = df.iloc[:303]

cleveland_df = cleveland_df[['age', 'sex', 'cp', 'trestbps', 'chol',
                             'fbs', 'restecg', 'thalach', 'exang',
                             'oldpeak', 'slope', 'ca', 'thal', 'num']]
df = cleveland_df.copy()
df['target'] = df['num'].apply(lambda x: 0 if x == 0 else 1)
df = df.drop(columns=['num'])

X = df[['age', 'sex', 'thalach', 'restecg']]
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

preprocessor = ColumnTransformer([
    ('passthrough', 'passthrough', X.columns)
])

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42))
])

param_grid = {
    'classifier__max_depth': [3, 5, 7],
    'classifier__n_estimators': [50, 100, 150],
    'classifier__learning_rate': [0.01, 0.1, 0.2]
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print("Cross-validated accuracy:", grid_search.best_score_)
print("Test set accuracy:", grid_search.best_estimator_.score(X_test, y_test))

joblib.dump(grid_search.best_estimator_, 'xgboost_cleveland_model.pkl')

loaded_model = joblib.load('xgboost_cleveland_model.pkl')
probs = loaded_model.predict_proba(X_test)[:, 1]
print(probs[:20])
    

print("Test set accuracy (loaded model):", loaded_model.score(X_test, y_test))
