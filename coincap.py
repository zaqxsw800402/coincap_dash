from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from sqlalchemy import create_engine
import contextlib

def ce():
    return create_engine('postgresql+psycopg2://airflow:airflow@127.0.0.1:5432/postgres')


def download(filename: str = 'coins.csv'):
    url = 'https://api.coincap.io/v2/assets'
    r = requests.get(url)
    data = r.json().get('data')
    coins = pd.DataFrame(data)
    coins.to_csv(filename)
    # print(coins.head())


def read_data(filename: str = 'coins.csv'):
    coins = pd.read_csv(filename)
    coins['dt'] = pd.to_datetime(datetime.now(tz=timezone(timedelta(hours=8))))
    # coins['dt'] = pd.to_datetime(datetime.now(tz=timezone(timedelta(hours=8))), format="%m/%d/%Y, %H:%M:%S")
    # pd.to_datetime(df['Datetime'], format="%m/%d/%Y, %H:%M:%S")
    coins.rename(columns={'rank': 'coinrank', 'priceUsd': 'priceusd'}, inplace=True)
    coins['priceusd'] = coins.priceusd.round(2)
    coins_sql = coins[['id', 'coinrank', 'symbol', 'name', 'priceusd', 'dt']]
    return coins_sql


def createtable():
    sql_table = '''
    create table if not exists coins (
    id varchar,
    coinrank int, 
    symbol varchar,
    name varchar,
    priceUsd double precision,
    dt timestamp
    )
    '''
    engine = create_engine('postgresql+psycopg2://zaqxs:zxcvbnm@localhost:5433/coincap')
    con = engine.connect()
    con.execute(sql_table)
    con.close()


def loadtosql(df):
    engine = create_engine('postgresql+psycopg2://zaqxs:zxcvbnm@localhost:5433/coincap')
    df.to_sql('coins', con=engine, if_exists='append', index=False)


def first_stage():
    download()
    df = read_data()
    createtable()
    loadtosql(df)


def createdf(data):
    columns = ['id', 'coinrank', 'symbol', 'name', 'priceUsd', 'dt']
    df = pd.DataFrame(data, columns=columns)
    df.priceUsd = df.priceUsd.round(2)
    df['dt'] = df.dt.astype('datetime64[s]')
    df = df.sort_values('dt', ascending=False).reset_index(drop=True)
    df.dt = df.dt.astype('datetime64[s]')
    # df = df.sort_values('dt', ascending=False).reset_index()
    return df


def select_coins(name: str):
    # engine = create_engine('postgresql+psycopg2://zaqxs:zxcvbnm@localhost:5433/coincap')
    engine = ce()

    sql = '''
    select * from coins where id = %s
    '''

    con = engine.connect()
    res = con.execute(sql, (name,))
    con.close()
    df = createdf(res.fetchall())
    return df


def select_rankid(coinrank: int):
    # engine = create_engine('postgresql+psycopg2://zaqxs:zxcvbnm@localhost:5433/coincap')
    engine = ce()

    sql = '''
    select * from coins where coinrank = %s
    '''

    con = engine.connect()
    res = con.execute(sql, (coinrank,))
    con.close()

    df = createdf(res.fetchall())
    # df.sort_values('dt', ascending=False, inplace=True)
    return df


def select_all():
    # engine = create_engine('postgresql+psycopg2://zaqxs:zxcvbnm@localhost:5433/coincap')
    engine = ce()

    sql = '''
    select * from coins
    '''

    con = engine.connect()
    res = con.execute(sql)
    con.close()

    df = createdf(res.fetchall())
    df.sort_values('coinrank', ascending=True, inplace=True)
    return df


if __name__ == '__main__':
    # first_stage()
    all = select_all()
    all = all.sort_values('dt', ascending=False).drop_duplicates(subset=['coinrank'], keep='first').sort_values(
        'coinrank')
    print(all)
