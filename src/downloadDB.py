from ast import Load
import pandas as pd
import random
import numpy as np
from datetime import datetime


def random_dates(start, end, n=10):

    start_u = start.value//10**9
    end_u = end.value//10**9

    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')


def load_df():
    df = pd.read_csv(
        'https://query.data.world/s/7ywhs3irjz3jwexgfc7idx6pmz62kl')

    # replacing index with _id for mongo
    df['_id'] = df['product_id']
    df = df.set_index('_id')

    # cleaning data
    df = df.drop(['url', 'uniq_id', 'scraped_at',
                 'availability', 'product_id'], axis=1)
    df['sku'].fillna(0, inplace=True)
    df['gtin13'].fillna(0, inplace=True)

    # randomizing some values
    df['in_stock'] = random.choices([0, 1, 2, 3], k=len(df))
    start = pd.to_datetime('2020-01-01')
    end = pd.to_datetime('2022-10-01')
    df['added_at'] = random_dates(start, end, len(df))
    # print(pd.to_datetime(df['added_at'],format='%d/%m/%Y').head())
    #df['added_at'].apply(lambda row: print(datetime.utcfromtimestamp(row.value)))
    #df['added_at'] = df['added_at'].astype(str)

    return df


if __name__ == "__main__":
    df = load_df()
    print(df.head())
    print(df.dtypes)
    df.to_csv('pdb_dataset.csv')
