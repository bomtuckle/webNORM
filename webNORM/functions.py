import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import base64
from pyrolite.mineral.normative import CIPW_norm


oxides = ['SiO2', 'TiO2', 'Al2O3', 'Fe2O3', 'FeO', 'MnO', 'MgO', 'CaO',
              'Na2O', 'K2O', 'P2O5']

minor_trace = [        
    "CO2",
    "SO3",
    "F",
    "Cl",
    "S",
    "Ni",
    "Co",
    "Sr",
    "Ba",
    "Rb",
    "Cs",
    "Li",
    "Zr",
    "Cr",
    "V"
    ]

def major_sum(data):
    return data[oxides].sum(axis=1)

def summation_warning(data, threshold):
    return len(data[data[oxides].sum(axis=1) < threshold])


def load_data(file):
    if file is not None:
        if 'csv' in file.name:
            data = pd.read_csv(file)
        elif 'xlsx' in file.name:
            data = pd.read_excel(file)
        else:
            data = None
    else:
        data = None
    return data



@st.cache
def download_df(df):
    xlsx = df.to_csv(index=False)
    b64 = base64.b64encode(
        xlsx.encode()
    ).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="normative_mineralogy.csv">Download results as csv file</a>'

def download_template():
    template = pd.DataFrame(columns=oxides+minor_trace)

    xlsx = template.to_csv(index=False)
    b64 = base64.b64encode(
        xlsx.encode()
    ).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="template.csv">Click here to download an example template</a>'


def highlight_greaterthan(s, threshold, column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] >= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]

def highlight_lessthan(s, threshold, column):
    is_max = pd.Series(data=False, index=s.index)
    is_max[column] = s.loc[column] <= threshold
    return ['background-color: yellow' if is_max.any() else '' for v in is_max]


def fe_correction(df, constant=None, specified_column=None):
    """
        Adjusts FeO Fe2O3 ratio using a constant value specified
    """

    df = df.copy(deep=True)

    # replace str values from df with 0
    def unique_strings(df, col):
        return df[col][df[col].map(type) == str].unique().tolist()

    # replace nans with 0

    df.fillna(0, inplace=True)

    
    df['total_Fe_as_FeO'] = (df['Fe2O3'] / 1.11134) + df['FeO']
    
    
    fe_adjustment_factor = constant

    df['adjusted_Fe2O3'] = df['total_Fe_as_FeO'] * (1 - fe_adjustment_factor) * 1.11134

    df['adjusted_FeO'] = df['total_Fe_as_FeO'] * fe_adjustment_factor

    df['Fe2O3'] = df['adjusted_Fe2O3']
    df['FeO'] = df['adjusted_FeO']

    return df[['FeO', 'Fe2O3']]


def calculate_norms(df, fe_correction_method, fe_correction_type=None, fe_constant=None):

    if fe_correction_method == 'Le Maitre':
        norms = CIPW_norm(df=df, Fe_correction='LeMaitre', Fe_correction_mode=fe_correction_type, adjust_all_Fe=True, return_free_components=True, rounding=3)
    
    elif fe_correction_method == 'Middlemost':
        norms = CIPW_norm(df=df, Fe_correction='Middlemost', Fe_correction_mode=fe_correction_type, adjust_all_Fe=True, return_free_components=True, rounding=3)
    else:
        norms = CIPW_norm(df=df)
    

    only_endmembers = ['quartz', 'zircon', 'potassium metasilicate', 'anorthite',
       'sodium metasilicate', 'acmite', 'thenardite', 'albite', 'orthoclase',
       'perovskite', 'nepheline', 'leucite', 'dicalcium silicate',
       'kaliophilite', 'apatite', 'fluroapatite', 'fluorite', 'pyrite',
       'chromite', 'ilmenite', 'calcite', 'corundum', 'rutile', 'magnetite',
       'hematite', 'forsterite', 'fayalite', 'clinoferrosilite',
       'clinoenstatite', 'ferrosilite', 'enstatite', 'titanite',
       'wollastonite', 'halite',
       'cancrinite', 'FREE_O', 'FREE_CO2',
       'FREE_OXIDES']

    norms['Sum'] = norms[only_endmembers].sum(axis=1) - norms['FREE_DEFSIO2']

    return norms