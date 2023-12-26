from typing import Union, List
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st
import re


def old_filter_dataframe(df: pd.DataFrame,dataset_name:str) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # modify = st.checkbox("Add filters",key = dataset_name)

    # if not modify:
    #     return df

    df_cp = df.copy()

    # Define a regex pattern for capturing any column with the word "year"
    pattern = re.compile(r'\b\w*year\w*\b', flags=re.IGNORECASE)

    columns_with_year = [col for col in df_cp.columns if re.search(pattern, col)]

    # convert all datetime year column to object
    for i in columns_with_year:
        if not is_object_dtype(df_cp[i]):
            df_cp[i] = df_cp[i].astype(str)


    modification_container = st.container()

    # only allow categorical cols with less than 10 to be filtered
    # include both object and datetime columns
    categorical_cols= df.select_dtypes(include=["object"]).columns
    categorical_cols = [col for col in categorical_cols if df[col].nunique() < 10]
    categorical_cols.extend(columns_with_year)

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", categorical_cols)

        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_object_dtype(df[column]):
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            # elif is_numeric_dtype(df[column]):
            #     _min = float(df[column].min())
            #     _max = float(df[column].max())
            #     step = (_max - _min) / 100
            #     user_num_input = right.slider(
            #         f"Values for {column}",
            #         min_value=_min,
            #         max_value=_max,
            #         value=(_min, _max),
            #         step=step,
            #     )
            #     df = df[df[column].between(*user_num_input)]
            # elif is_datetime64_any_dtype(df[column]):
            #     user_date_input = right.date_input(
            #         f"Values for {column}",
            #         value=(
            #             df[column].min(),
            #             df[column].max(),
            #         ),
            #     )
            #     if len(user_date_input) == 2:
            #         user_date_input = tuple(map(pd.to_datetime, user_date_input))
            #         start_date, end_date = user_date_input
            #         df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def filter_dataframe(df: pd.DataFrame,dataset_name:str) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # modify = st.checkbox("Add filters",key = dataset_name)

    # if not modify:
    #     return df

    df_cp = df.copy()

    # Define a regex pattern for capturing any column with the word "year"
    pattern = re.compile(r'\b\w*year\w*\b', flags=re.IGNORECASE)

    columns_with_year = [col for col in df_cp.columns if re.search(pattern, col)]

    # convert all datetime year column to object
    for i in columns_with_year:
        if not is_object_dtype(df_cp[i]):
            df_cp[i] = df_cp[i].astype(str)


    modification_container = st.container()

    # only allow categorical cols with less than 10 to be filtered
    # include both object and datetime columns
    categorical_cols= df_cp.select_dtypes(include=["object"]).columns
    categorical_cols = [col for col in categorical_cols if df_cp[col].nunique() < 10]
    # if the elements in columns_with_year are not in categorical_cols, add them to categorical_cols
    for i in columns_with_year:
        if i not in categorical_cols:
            categorical_cols.append(i)


    with modification_container:

        # create filters dynamically depending on the number of elements in categorical_cols
        filter_list= list(st.columns(len(categorical_cols)))
        for i, col in enumerate(categorical_cols):
            options = ['All'] + list(df_cp[col].unique())
            filtered= filter_list[i].multiselect(col, options, key = f'{dataset_name}_{col}', default = 'All')

            if "All" in filtered:
                filtered = df_cp[col].unique()

            df_cp = df_cp[df_cp[col].isin(filtered)]


    return df_cp
    


