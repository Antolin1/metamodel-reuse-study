import sqlite3

import pandas as pd
from tqdm import tqdm

FILE_DATABASE_ORIGINAL = '../../metamodel-reuse-study/dup_network.db'

FILE_DATABASE_NEW = 'dup_network.db'

CONN_ORIGINAL = sqlite3.connect(FILE_DATABASE_ORIGINAL)
CONN_NEW = sqlite3.connect(FILE_DATABASE_NEW)

CURSOR_NEW = CONN_NEW.cursor()

query = 'SELECT * from metamodels'
df_original = pd.read_sql_query(query, CONN_ORIGINAL)
df_new = pd.read_sql_query(query, CONN_NEW)

print(df_original.head())
print(df_new.head())

local_path_original = set(list(df_original['local_path']))
local_path_new = set(list(df_new['local_path']))

for l in tqdm([l for l in local_path_original if l in local_path_new]):
    # update first commit and author
    first_commit = df_original[df_original['local_path'] == l]['first_commit'].values[0]
    author = df_original[df_original['local_path'] == l]['author'].values[0]
    CURSOR_NEW.execute("UPDATE metamodels SET first_commit=?, author=? WHERE local_path=?", (first_commit, author, l))

CONN_NEW.commit()


for l in tqdm([l for l in local_path_original if l not in local_path_new]):
    # insert new row
    first_commit = df_original[df_original['local_path'] == l]['first_commit'].values[0]
    considered_commit = df_original[df_original['local_path'] == l]['considered_commit'].values[0]
    author = df_original[df_original['local_path'] == l]['author'].values[0]
    user = df_original[df_original['local_path'] == l]['user'].values[0]
    repo = df_original[df_original['local_path'] == l]['repo'].values[0]
    repo_path = df_original[df_original['local_path'] == l]['repo_path'].values[0]
    local_path = l
    CURSOR_NEW.execute("INSERT INTO metamodels (user, repo, repo_path, local_path, considered_commit, first_commit, author) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user, repo, repo_path, local_path, considered_commit, first_commit, author))

CONN_NEW.commit()

