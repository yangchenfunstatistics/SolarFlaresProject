#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 17:29:22 2018

@author: dufumier
"""
import os
from Preprocessing import preprocessing as preproc
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn import svm, metrics
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

path = '/n/midland/w/dufumier/Documents/BlueSky/TimeSeriesAnalysis'
path_data = os.path.join(path, 'Dataset')

pos_ts = preproc.get_timeseries(path_data, 'timeseries_pos')
neg_ts = preproc.get_timeseries(path_data, 'timeseries_neg')

def tss_metric(y_true, y_pred):
    fp = sum((1 - y_true )*y_pred)
    tn = sum((1 - y_true)*(1 - y_pred))
    recall = metrics.recall_score(y_true, y_pred)
    tss = recall - fp/(fp + tn)
    return tss

def compute_metrics(y_true, y_pred):
    y_true = np.array(y_true, dtype=np.bool)
    y_pred = np.array(y_pred, dtype=np.bool)
    f1 = metrics.f1_score(y_true, y_pred)
    precision = metrics.precision_score(y_true, y_pred)
    recall = metrics.recall_score(y_true, y_pred)
    hss = recall * (2 - 1/precision)
    acc = metrics.accuracy_score(y_true, y_pred)
    tss = tss_metric(y_true, y_pred)
    return [acc, f1, precision, recall, hss, tss]

def print_metrics(y_true, y_pred):
    acc, f1, precision, recall, hss, tss = compute_metrics(y_true, y_pred)
    print(' acc = {} \n f1 = {} \n precision = {} \n recall = {} \n hss = {} \n tss = {}'.\
          format(acc, f1, precision, recall, hss, tss))

assert np.shape(pos_ts)[1:] == np.shape(neg_ts)[1:]

(_, nb_features, nb_frames) = np.shape(pos_ts)

dataset = np.concatenate((pos_ts, neg_ts))
y_true = np.concatenate((np.ones(len(pos_ts)), np.zeros(len(neg_ts))))
test_size = 0.2
# 1st feature: SIZE
X1 = dataset[:,0,:]
# 2nd feature: SIZE_ACR (active region' size)
X2 = dataset[:,1,:]
# 3rd feature: NACR (nb of pixels)
X3 = dataset[:,2,:]

p1 = plt.plot(pos_ts[:,2, -1], 'r.', label='flare level > C9')
p2 = plt.plot(neg_ts[:,2, -1], 'b.', label='flare level < C1')
plt.title('Scatterplot of the number of active pixels in a patch')
plt.legend()
plt.show()
p1 = plt.plot(pos_ts[:,1, -1], 'r.', label='flare level > C9')
p2 = plt.plot(neg_ts[:,1, -1], 'b.', label='flare level < C1')
plt.title('Scatterplot of the active region size')
plt.legend()
plt.show()


X1_training, X1_testing, y1_training, y1_testing = train_test_split(X1, y_true, test_size=test_size, random_state = 20)
X2_training, X2_testing, y2_training, y2_testing = train_test_split(X2, y_true, test_size=test_size, random_state = 20)
X3_training, X3_testing, y3_training, y3_testing = train_test_split(X3, y_true, test_size=test_size, random_state = 20)



fig, ax = plt.subplots(figsize=(10, 10))
bp_pos = plt.boxplot([pos_ts[:,1,0], pos_ts[:,1,45], pos_ts[:,1,-1]], positions=[2,5,7], widths=0.6)
bp_neg = plt.boxplot([neg_ts[:,1,0],neg_ts[:,1,45],neg_ts[:,1,-1]], positions=[1,4,8], widths=0.6)
plt.setp(bp_pos["boxes"], color='blue')
plt.setp(bp_neg["boxes"], color='red')

ax.legend([bp_pos["boxes"][0], bp_neg["boxes"][0]], ['flare level > C9', 'flare level < C1'], loc='upper right')
ax.set_xticklabels(['12 min', '9h', '18h'])
ax.set_xlabel('Time before eruption')
ax.set_title('Active Region size')
plt.show()

fig, ax = plt.subplots(figsize=(10, 10))
bp_pos = plt.boxplot([pos_ts[:,2,0], pos_ts[:,2,45], pos_ts[:,2,-1]], positions=[2,5,7], widths=0.6)
bp_neg = plt.boxplot([neg_ts[:,2,0],neg_ts[:,2,45],neg_ts[:,2,-1]], positions=[1,4,8], widths=0.6)
plt.setp(bp_pos["boxes"], color='blue')
plt.setp(bp_neg["boxes"], color='red')

ax.legend([bp_pos["boxes"][0], bp_neg["boxes"][0]], ['flare level > C9', 'flare level < C1'], loc='upper right')
ax.set_xticklabels(['12 min', '9h', '18h'])
ax.set_xlabel('Time before eruption')
ax.set_title('Number of active pixels in patch')
plt.show()




time_i = 89
frame_to_extract = -1 # the last one
dataset_1_frame = dataset[:,:,frame_to_extract] # nb_vids x nb_features
X_training, X_testing, y_training, y_testing = train_test_split(dataset_1_frame, y_true, test_size=test_size, random_state=20)

# GRADIENT BOOSTING

params = {'learning_rate' : 0.05, 'n_estimators' : 200, 'max_depth': 4, 'subsample':0.6}
metrics_ = []
for k in range(1000):
    X2_training, X2_testing, y2_training, y2_testing = train_test_split(X2, y_true, test_size=test_size)
    clf = GradientBoostingClassifier(**params)
    clf.fit(X2_training[:,89:], y2_training)
    metrics_ += [compute_metrics(y2_testing, clf.predict(X2_testing[:,89:]))]


print_metrics(y2_testing, clf.predict(X2_testing[:,89:]))
plt.xlabel('iteration')
plt.ylabel('Training loss')
plt.title('Training loss by considering just one frame 18h before eruption')
plt.plot(clf.train_score_)
plt.show()
plt.xlabel('Features')
plt.xticklabels()
plt.ylabel('Relative importance')
plt.plot(clf.feature_importances_, '+')
plt.show()
plt.xlabel('Nb of frames considered (time points)')
plt.ylabel('Accuracy')





# SVM (rbf kernel)
scaler = StandardScaler()
scaler.fit(X2_training)
# Best performance (acc, tss) for X_train: gamma = 7, kernel = rbf, C = 50
# Best performance (tss) for X2_train: gamma = 0.037, C = 24
clf = svm.SVC(C = 24, kernel='rbf', gamma =  0.037, tol = 1e-10)
clf.fit(scaler.transform(X2_training), y2_training)
scaler.fit(X2_testing)
print_metrics(y2_testing, clf.predict(scaler.transform(X2_testing)))




















