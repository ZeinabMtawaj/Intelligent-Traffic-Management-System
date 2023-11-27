from myapp.app.ai.model_loader import load_models
load_models()
import numpy as np
from flask import Flask, request, render_template
from flask_ngrok import run_with_ngrok
from pymongo import MongoClient
import pickle
import json
from flask import Blueprint, render_template, request, current_app, flash, jsonify, make_response, redirect, url_for
from bson.objectid import ObjectId
import pandas as pd
import os
import math
import networkx as nx
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from random import randint
from joblib import dump, load
import sumolib



from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import KFold, train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib

import pyproj
from geopy.geocoders import Nominatim
import traci
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from tenacity import retry, wait_exponential, stop_after_attempt
