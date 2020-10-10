import numpy as np
import pandas as pd
import pickle

from collections import Counter

def predictor(embs):
    embs=embs.reshape(1,-1)
    model_0=pickle.load(open('static/data/_com0.pkl','rb'))
    model_1=pickle.load(open('static/data/_com1.pkl','rb'))
    model_2=pickle.load(open('static/data/_com2.pkl','rb'))
    pred0=model_0.predict(embs)
    pred1=model_1.predict(embs)
    pred2=model_2.predict(embs)
    pred_list=[pred0[0],pred1[0],pred2[0]]
    del model_0,model_1,model_2
    count=Counter(pred_list)
    value,con=count.most_common()[0]
    del pred0,pred1,pred2,count
    return value

def controller(embs):
    pred=predictor(embs)
    if(pred==1):
        return "positive"
    elif(pred==-1):
        return "negative"
    elif(pred==0):
        return "no"
    else:
        return "Something went wrong"