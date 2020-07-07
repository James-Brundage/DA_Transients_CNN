'''
This script will extract 30sec matrices of the colorplots where DA transients should be found. It will also pull correct
labels for region, sex and drug. It will return a dataframe with the matrix in one column (30xOI range) and the labels
in the other.

Email: jamesnick.brundage@gmail.com with questions.
'''

import numpy as np
import scipy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

test_file = "/Users/jamesbrundage/Box/Colin's Data Funhouse/spons/demon files/RegionalCocEticSpons/CoreCocEticSpons/4.3.17.MaleC57.2.19"
files = os.listdir(test_file)
file_pths = [os.path.join(test_file,f) for f in files]

files_type_1 = "/Users/jamesbrundage/Box/Colin's Data Funhouse/spons/demon files"

# Paths for testing and extraction
test_path = '00_Nac1p_5_huge spons.tdms'
test_path_1 = '00_Nac1p_9_spons.tdms'
paths = [test_path, test_path_1]

def chunk_no_captain_chunk(tdms, oi=(230, 500), chunk_size=30, plot_me=False, labels=['Region', 'Sex', 'Drug Applied']):
    '''
    This function will chunk out a tdms file and return a list of lists that can be used by
    sns.heatmap to create image types. Should also be fit for input to a CNN.
    :param chunk_size: Size of each chunk in seconds
    :param oi: Oxidation index to be selected, default at 230 and 500
    :param plot_me: determines whether or not visualize each chunk before appending.
    :param labels: contians the label information for each chunk. Is the same for all chunks in the dataset.
    :param tdms: The path to the .tdms file that needs to be chunked.
    :return: list of 2D arrays for each chunk.
    '''

    # Imports from David's tdms Demon stuff
    from volt_analysis_funcs import read_tdms

    # Reads in the tdms. See volt_analysis_func.py for details.
    cp = read_tdms(test_path)

    # Determines appropriate chunk length to ensure uniform chunk size
    rec_length = len(cp[0])
    chunkable_time = rec_length - (rec_length % chunk_size)

    # Produces chunk arrays and adds them to chnk_lst and also cerates column for track file location (file_inf)
    chnk_lst = []
    file_inf = []
    n = 0
    m = chunk_size
    while n < chunkable_time:
        cp_w = cp[oi[0]:oi[1], n:m]
        chnk_lst.append(cp_w)
        file_inf.append(tdms + ' ' + str(m))

        # Plots the CP if you want to see the chunks.
        if plot_me == True:
            sns.heatmap(cp_w)
            plt.show()

        n = m
        m = m + chunk_size

    # Creates a dataframe containing
    df = pd.DataFrame()
    df['File Information'] = file_inf
    df['Color Plots'] = chnk_lst
    df['Labels'] = [labels] * len(df)

    return df

def chunker(paths, save=False):
    '''

    :param paths: List of .tdms file paths
    :return: df with chunks and labels
    '''

    def get_sex(path):
        if path.lower().find('female') > -1:
            return 'Female'
        else:
            return 'Male'
    def get_region(path):
        p = path.lower()
        if p.find('core') > -1:
            return 'NAcc'
        elif p.find('shell') > -1:
            return 'NAcs'
        elif p.find('ds') > -1:
            return 'DS'
        else :
            return 'No Region Found'
    def get_drug(f):

        key = f[0:3]

        if key == '00_':
            return 'Baseline'

        elif key == '01_':
            return '4AP'

        elif key == '02_':
            return 'Cocaine'

        elif key == '03_':
            return 'Eticlopride'

        else:
            return 'Drug Unknown'

    dfs_lst = []
    n = 1
    for p in paths:

        sex = get_sex(p)
        reg = get_region(p)
        drg = get_drug(p)

        dfs_lst.append(chunk_no_captain_chunk(p, labels=[reg, sex, drg]))
        print('Completed: ' + str(n) + ' ' + p)
        n = n + 1

    dff = pd.concat(dfs_lst)

    if save == True:
        dff.to_pickle('Spon_Dataset.pkl')
    print(dff)
    return dff

paths = []
for root, dirs, files in os.walk(files_type_1, topdown=False):
   for name in files:
      paths.append(os.path.join(root, name))

paths = paths[0:2]
dff = chunker(paths).reset_index()

print(dff['Color Plots'][0].shape)






