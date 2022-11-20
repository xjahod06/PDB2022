from ast import Load
import pandas as pd
import random
import numpy as np


def random_dates(start, end, n, unit='D', seed=None):
    if not seed:  # from piR's answer
        np.random.seed(0)

    ndays = (end - start).days + 1
    return pd.to_timedelta(np.random.rand(n) * ndays, unit=unit) + start

def load_df():
    df = pd.read_csv(
        'https://query.data.world/s/7ywhs3irjz3jwexgfc7idx6pmz62kl')
    df['in_stock'] = random.choices([0, 1, 2, 3], k=len(df))
    df = df.drop(['url', 'uniq_id', 'scraped_at', 'availability'], axis=1)
    start = pd.to_datetime('2020-01-01')
    end = pd.to_datetime('2022-10-01')
    df['added_at'] = random_dates(start, end, len(df))
    return df


if __name__ == "__main__":
    load_df().to_csv('pdb_dataset.csv')
