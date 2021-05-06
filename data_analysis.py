 import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

#Custom Imports

#SKL Imports
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.decomposition import KernelPCA
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report

np.random.RandomState(510)
# Filepaths
PROCESSED_DATA = "C:/Users/wtspe/Documents/OpenSignals (r)evolution/files/test_data/Processed Data"
COMPILED_PROCESSED_DATA = os.path.join(PROCESSED_DATA,'compliled_processed_data.csv')
FEAT_CORR_DATA = os.path.join(PROCESSED_DATA,'intra_feature_correlations.csv')
PICS_DIRECTORY = os.path.join(PROCESSED_DATA,'grafs')
CORR_DATA_PLT = os.path.join(PICS_DIRECTORY,'corr_heatmap.jpg')

os.makedirs(PICS_DIRECTORY,exist_ok = True)

def get_filenames(folderPath:str)->list:
    """Extracts filenames from target folder.""" 
    dirList = os.listdir(folderPath)
    fileList = []
    for fileName in dirList:
        if 'processed.csv' in fileName:
            fileList.append(os.path.join(folderPath,fileName))
    #print(fileList)
    return fileList

def create_database(dataPath=PROCESSED_DATA):
    """Complies data from all trials into a single DataFrame object."""
    os.chdir(dataPath)
    tempDB = pd.DataFrame()
    fileNames = get_filenames(dataPath)
    for fileName in fileNames:
        tempDB = tempDB.append(pd.read_csv(fileName))
    tempDB.drop(['Unnamed: 0'],axis=1,inplace=True)
    tempDB.to_csv('compliled_processed_data.csv')
    return tempDB

def load_make_database(dataPath=COMPILED_PROCESSED_DATA):
    if os.path.exists(dataPath):
        print(f'Loading existing database.')
        tempDB = pd.read_csv(dataPath)
        tempDB.drop(['Unnamed: 0'],axis=1,inplace=True)
        return tempDB
    else:
        print(f'Creating existing database.')
        return create_database()
    
# Plotting Results
def create_kmeans_plot(X,y,labels,title:str='None')->None:
    """2D-Scatter w/ lables."""
    fig,ax = plt.subplots()
    for i,label in zip(np.unique(y),labels):
        res = np.where(y==i)
        ax.scatter(X[res,0], X[res,1],label=label,alpha=0.45)
    ax.set(
      xlabel = 'PC-1',
      ylabel = 'PC-2',
      title = title
    )
    ax.legend()
    ax.grid(True)
    #plt.show()
    fig.savefig(title+'.jpg')


def analysis_main(data:pd.DataFrame,tempPipe)->None:
    data['state_encoded'] = LabelEncoder().fit_transform(data['state'])
    #data['alg_state_encoded'] = LabelEncoder().fit_transform(data['alg_state'])
    X_final = data.drop(columns=['alg_state', 'subject', 'state'],axis=1)
    y_final = data.pop('state')
    subjects = np.unique(data.subject.to_numpy())
    labels = np.unique(y_final.to_numpy())
    #np.where(data.subject.to_numpy()==subject)
    # Create plots
    os.chdir(PICS_DIRECTORY)
    for subject in subjects:
        X_sub = X_final[data['subject']==subject]
        y_sub = y_final[data['subject']==subject]
        X_sub = tempPipe.fit_transform(X_sub)
        X_trans = KMeans(n_clusters = 3).fit_transform(X_sub)
        create_kmeans_plot(X_sub,y_sub.to_numpy(),labels,f'{subject.upper()} Final with True')
        create_kmeans_plot(X_trans,y_sub.to_numpy(),labels,f'{subject.upper()} Trans with True')
    # Correlation of features
    plt.close('all')
    dataCorr = data.corr()
    plt.figure(figsize=(10,10))
    ax = sns.heatmap(dataCorr, cmap = 'RdYlGn', xticklabels=dataCorr.columns, yticklabels=dataCorr.columns, annot=True)
    plt.savefig(CORR_DATA_PLT)
    plt.show()
    #dataCorr.to_csv(FEAT_CORR_DATA)

def alg_acc(data:pd.DataFrame)->None:
    def standardize_labels(x:str)->str:
        if 'use' in x:
            return 'rest'
        elif 'withdrawal' in x:
            return 'active'
        elif 'normal' in x:
            return 'base'
    algLabel = data.pop('alg_state').apply(standardize_labels)
    #print(algLabel.head())
    trueLabel = data.pop('state')
    algAccScore = accuracy_score(trueLabel,algLabel)
    baScore = balanced_accuracy_score(trueLabel,algLabel)
    print('\n\n\n')
    print(f"Opisense Alg Accuracy: {int(algAccScore*100)}%")
    print(f"Opisense Alg Balanced Accuracy: {int(baScore*100)}%")
    print(f'Classification Report\n')
    print(classification_report(trueLabel, algLabel,zero_division = 0))

def get_data_pipeline(opisenseData:pd.DataFrame,dropLabels:bool = True):
    if dropLabels:
        dtypes = opisenseData.drop(columns=['alg_state', 'subject', 'state'],axis=1).dtypes
    else:
        dtypes = opisenseData.dtypes
    
    cat_vars = []
    cont_vars = []
    for index in dtypes.index:
        if dtypes[index]=='object':
            cat_vars.append(index)
        else:
            cont_vars.append(index)

    cat_pipeline = make_pipeline(
        LabelEncoder()
    )
    cont_pipeline = make_pipeline(
        StandardScaler()
    )

    preprocessor = ColumnTransformer(
        transformers = [
            ('cont',cont_pipeline,cont_vars),
            ('cat',cat_pipeline,cat_vars)
        ]
    )
    
    pipe = make_pipeline(
        preprocessor,
        KernelPCA(n_components = 2, kernel = 'cosine', n_jobs = -1)
    )
    
    return pipe
    


if __name__ == '__main__':
    # Get the data.
    opisenseData = load_make_database()

    # Pipeline Construction
    pipe = get_data_pipeline(opisenseData)

    # Results
    # For each group member, prepare a plot of their data
    # Plot KPCA and KNN Bagged 2Ds

    analysis_main(opisenseData,pipe)
    #alg_acc(opisenseData)
