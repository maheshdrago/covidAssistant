import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


#PreProcessing

data = pd.read_csv("coronaCases.csv")
data = data[['id','cases']]


x = np.array(data['id']).reshape(-1,1)
y = np.array(data['cases']).reshape(-1,1)



polyFeat = PolynomialFeatures(degree=3)
x = polyFeat.fit_transform(x)


#Training 

model = linear_model.LinearRegression()
model.fit(x,y)
accuracy = model.score(x,y)

y0 = model.predict(x)



#Prediction

def track_covid(days):
    
    value = (model.predict(polyFeat.fit_transform([[400+days]])))
    
    return value[0][0]



