import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime, timezone
import matplotlib.pyplot as plt

def ms_epoch_to_month(row):
    ms = row['date']
    sec = ms // 1000
    dt = datetime.fromtimestamp(sec, timezone.utc)
    return dt.strftime("%m/%Y")

def ship_to_ice(row):
    return row['ship'] / row['ice']

def ice_coverage_percent(row):
    ratio = row['ice'] / sum([row['ship'], row['ice'], row['water'], row['unknown']])
    return ratio * 100

def main():
    export_folder = 'export-data/smooth'
    export_files = [join(export_folder, f) for f in listdir(export_folder)
                    if isfile(join(export_folder, f)) and '.DS_Store' not in f]

    to_merge = []
    for file in export_files:
        print('reading ', file)
        to_merge.append(pd.read_csv(file))

    df = pd.concat(to_merge, ignore_index=True).drop_duplicates(subset=['date'])
    df = df[(df.date > 0) & (df.ship > 0) & (df.ice > 0)]
    df.drop('.geo', axis=1, inplace=True)
    df.drop('system:index', axis=1, inplace=True)
    # add human readable times
    df['time'] = df.apply(ms_epoch_to_month, axis=1)

    df = df.groupby('time').mean()

    df['ship-to-ice'] = df.apply(ship_to_ice, axis=1)
    df['ice_coverage'] = df.apply(ice_coverage_percent, axis=1)
    df = df.sort_values(by=['date']).reset_index()

    print(df)
    df.plot(x='time', y='ship-to-ice')
    plt.show()

if __name__ == '__main__':
    main()

