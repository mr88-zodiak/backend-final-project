import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt

data = pd.read_excel('data.xlsx')


print(data.head())