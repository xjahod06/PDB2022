from ast import Load
import pandas as pd
import random
import numpy as np


def random_dates(start, end, n, unit='D', seed=None):
    if not seed:
        np.random.seed(0)

    ndays = (end - start).days + 1
    return pd.to_timedelta(np.random.rand(n) * ndays, unit=unit) + start

def load_df():
    df = pd.read_csv(
        'https://query.data.world/s/7ywhs3irjz3jwexgfc7idx6pmz62kl')
    
    #replacing index with _id for mongo
    df['_id'] = df['product_id']
    df = df.set_index('_id')
    
    #cleaning data
    df = df.drop(['url', 'uniq_id', 'scraped_at', 'availability','product_id'], axis=1)
    df['sku'].fillna(0,inplace=True)
    df['gtin13'].fillna(0,inplace=True)
    
    #randomizing some values
    df['in_stock'] = random.choices([0, 1, 2, 3], k=len(df))
    start = pd.to_datetime('2020-01-01')
    end = pd.to_datetime('2022-10-01')
    df['added_at'] = random_dates(start, end, len(df))
    
    return df


if __name__ == "__main__":
    df = load_df()
    print(df.head())
    df.to_csv('pdb_dataset.csv')
