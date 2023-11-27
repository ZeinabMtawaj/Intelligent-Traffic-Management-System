
# import joblib
# import pickle

# MODEL1_PATH = 'myapp/app/ai/models/xgboost.joblib'
# MODEL2_PATH = 'myapp/app/ai/models/xgboost_without_weather.joblib'

# model_xgb_with_weather = joblib.load(MODEL1_PATH)
# model_xgb_without_weather = joblib.load(MODEL2_PATH)

# with open('myapp/app/ai/models/flow_prediction_model.pkl', 'rb') as file:
#     flow_prediction_model = pickle.load(file)

# scaler = joblib.load('myapp/app/ai/models/scaler.pkl')
import joblib
import pickle

MODEL1_PATH = 'myapp/app/ai/models/xgboost.joblib'
MODEL2_PATH = 'myapp/app/ai/models/xgboost_without_weather.joblib'

model_xgb_with_weather = None
model_xgb_without_weather = None
flow_prediction_model = None
scaler = None

def load_models():
    global model_xgb_with_weather, model_xgb_without_weather, flow_prediction_model, scaler

    if model_xgb_with_weather is None:
        model_xgb_with_weather = joblib.load(MODEL1_PATH)

    if model_xgb_without_weather is None:
        model_xgb_without_weather = joblib.load(MODEL2_PATH)

    if flow_prediction_model is None:
        with open('myapp/app/ai/models/flow_prediction_model.pkl', 'rb') as file:
            flow_prediction_model = pickle.load(file)

    if scaler is None:
        scaler = joblib.load('myapp/app/ai/models/scaler.pkl')
