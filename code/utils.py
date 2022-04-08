#from __future__ import absolute_import

import ast
import csv
import datetime
import glob
import json
import time
import os
import os.path
import pandas as pd
import pickle
import numpy as np
import requests

from dotenv import load_dotenv


from csv import writer
from functools import reduce
from time import sleep
from matplotlib import pyplot as plt
from minet import multithreaded_resolve
from pandas.api.types import CategoricalDtype
from ural import get_domain_name
from ural import is_shortened_url

def import_data(file_name):

    data_path = os.path.join('.', 'data', file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df

def save_figure(figure_name):

    figure_path = os.path.join('.', 'figures', figure_name)
    plt.savefig(figure_path, bbox_inches='tight')
    print('The {} figure is saved.'.format(figure_name))

def save_data(df, file_name, append):

    file_path = os.path.join('.', 'data', file_name)

    if append == 1:
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

    print(' {} is saved.'.format(file_name))
