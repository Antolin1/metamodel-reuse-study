import sqlite3

conn_crawler = sqlite3.connect('crawler.db')

cur = conn_crawler.cursor()

query = "select full_name from repo_info"

result = cur.execute(query)

jesus = set([r[0] for r in result.fetchall()])



conn_me = sqlite3.connect('dup_network.db')

query = """SELECT user || '/' || repo AS user_repo
FROM metamodels;"""

result = conn_me.execute(query)

me = set([r[0] for r in result.fetchall()])

# compute intersection

intersection = len([f for f in me if f in jesus]) / len(jesus)

print(intersection)