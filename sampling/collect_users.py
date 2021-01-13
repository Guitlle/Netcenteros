###  CONFIGURATION  ###
#######################
import datetime

dirmuestras = "."
NOW = 1610262345 # int(datetime.datetime.now().timestamp())

#############################################
import random
import twint
import pandas as pd
import sqlite3
import time
import os
import sys

dbcon = sqlite3.connect(os.path.join(dirmuestras, "users_{now}.db".format(now = NOW)))
dbcur = dbcon.cursor()
dbcur.execute("""CREATE TABLE IF NOT EXISTS metadata (
    created TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    name VARCHAR(255)
)
""")
dbcur.execute("INSERT INTO metadata (description, name) VALUES ('running collect users script', 'users')")
dbcur.execute("""CREATE TABLE IF NOT EXISTS errors (
    created TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    exception_str TEXT,
    user_id INTEGER,
    succeed_retry BOOLEAN DEFAULT FALSE,
    retries SMALLINT DEFAULT 0
)
""")

dbcon.commit()
dbcur.close()            

users = set([])
for r,d, filenames in os.walk(dirmuestras):
    for filename in filenames:
        if filename.startswith("muestra_"):
            _dbcon = sqlite3.connect(os.path.join(dirmuestras,filename))
            dbcur = _dbcon.cursor()
            result = dbcur.execute("SELECT DISTINCT user_id FROM tweets")
            users = users.union([x[0] for x in result.fetchall()] )
            dbcur.close()
            _dbcon.close()

dbcur = dbcon.cursor()
result = dbcur.execute("SELECT DISTINCT CAST(id AS INT) FROM users")
users = users.difference([x[0] for x in  result.fetchall()] )
users = list(users)
random.shuffle(users)
n = len(users)
dbcur.close()        
print("#### Found", n, "users")

i = 0
for user in users:
    twconfig = twint.Config()
    twconfig.Hide_output = True
    twconfig.Pandas = True
    twconfig.Store_object = True
    twconfig.User_id = str(user)
        
    twint.output.panda.clean()
    twint.output.clean_lists()

    i += 1
    print("___ ", i, "/", n)
    
    try:
        twint.run.Lookup(twconfig)
        df = twint.output.panda.User_df
        if len(df) > 0:
            for col in df.columns[df.dtypes==object]:
                df[col] = df[col].astype(str)
            df["fetch_date"] = NOW
            df.set_index(["id", "fetch_date"]).to_sql(
                        name = "users", con = dbcon,
                        if_exists = "append")
            print(df.to_json())

        twconfig = twint.Config()
        twconfig.Hide_output = True
        twconfig.Pandas = True
        twconfig.Store_object = True
        twconfig.User_id = str(user)
        twconfig.Limit = 50
        twint.run.Profile(twconfig)
        
        df = twint.output.panda.Tweets_df.iloc[0:50].copy()
        print("Found ", len(df), "tweets")
        if len(df) > 0:
            for col in df.columns[df.dtypes==object]:
                df[col] = df[col].astype(str)
            df["fetch_date"] = NOW
            df.set_index(["id", "fetch_date"]).to_sql(
                        name = "tweets", con = dbcon,
                        if_exists = "append")
    except:
        e = sys.exc_info()[0]
        print("Error", e)
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO errors (exception_str, user_id) VALUES (?, ?)",
                (str(e), user))
        dbcon.commit()
        dbcur.close()
    print("...")
    time.sleep(7)

dbcon.close()
