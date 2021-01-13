###  CONFIGURATION  ###
#######################
import datetime

topic_search = "guatemala"
from_date = datetime.date(2020,11,1)
to_date = datetime.date(2020,11,30)
twhour = 50

#############################################
import random
import twint
import pandas as pd
import sqlite3
import time

twconfig = twint.Config()
twconfig.Search = "guatemala"
twconfig.Limit = twhour
twconfig.Hide_output = True
twconfig.Pandas = True

dbname = 'muestra_{topic}_{from_date}_to_{to_date}.db'.format(
    topic = topic_search.replace(" ", "-"),
    from_date = str(from_date),
    to_date = str(to_date)
)
dbcon = sqlite3.connect(dbname)
dbcur = dbcon.cursor()
dbcur.execute("""
CREATE TABLE IF NOT EXISTS twint_queries (
    created TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    twintconfig TEXT,
    nrows INTEGER,
    name VARCHAR(255),
    since VARCHAR(100)
)
""")
dbcur.execute("""
CREATE TABLE IF NOT EXISTS metadata (
    created TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    name VARCHAR(255)
)
""")
dbcur.execute("\
INSERT INTO metadata (description, name) VALUES (\
    'Muestra de tweets para tema \"{topic}\"',\
    '{dbname}'\
) \
".format(dbname = dbname, topic = topic_search.replace("'", "\\'")))
dbcon.commit()
dbcur.close()

dayi = from_date
oneday = datetime.timedelta(days=1)
while dayi < to_date:
    for hour in range(24):
        minute = random.randint(0,50)
        since = dayi.strftime("%Y-%m-%d {hour}:{minute}:00".format(
                    hour = str(hour).rjust(2, "0"),
                    minute = str(minute).rjust(2,"0")
                ))
        dbcur = dbcon.cursor()
        results = dbcur.execute("SELECT COUNT(*) as nrows FROM twint_queries WHERE since LIKE ?", 
                (since[0:-5]+"%",) 
            )
        nrows = results.fetchone()[0]
        dbcur.close()
        if nrows > 0:
            print("FOUND data for day", dayi, " hour", hour, ". Skipping.")
            continue

        twconfig.Since = since
        twconfig.Until = twconfig.Since[0:-5] + str(minute+9).rjust(2,"0") + ":00"
        print("*********\nTWINT CONFIG: ", twconfig)
        
        twint.run.Search(twconfig)
        df = twint.output.panda.Tweets_df

        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO twint_queries (twintconfig, nrows, name, since) "+
                    "VALUES (?,?,?,?)", (str(twconfig), len(df), "tweets_hourly_sample", since) )
        dbcon.commit()
        dbcur.close()
        if len(df) == 0:
            continue
        
        for col in df.columns[df.dtypes==object]:
            df[col] = df[col].astype(str)
        df.set_index("id").to_sql(
                    name = "tweets", con = dbcon,
                    if_exists = "append")
        
                
        print("\tFOUND", len(df), "tweets")
        time.sleep(10)
    dayi += oneday

dbcon.close()