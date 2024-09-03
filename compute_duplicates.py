import argparse
import json
import sqlite3
from itertools import combinations

import pandas as pd
from dpu_utils.codeutils.deduplication import DuplicateDetector
from tqdm import tqdm


def register_database(duplicates, conn):
    cursor = conn.cursor()
    for group in duplicates:
        for i, j in combinations(group, 2):
            cursor.execute("INSERT INTO duplicates (m1, m2) VALUES (?, ?)", (i, j))


def main(args):
    conn = sqlite3.connect(args.db)
    # filter named elements less than 5 elements
    detector = DuplicateDetector(min_num_tokens_per_document=5)
    query = f'SELECT id, concepts FROM metamodels WHERE concepts IS NOT NULL'
    df = pd.read_sql_query(query, conn)
    for _, row in tqdm(df.iterrows(), desc='Add files'):
        detector.add_file(row['id'], json.loads(row['concepts']), language=None)
    duplicates = detector.compute_duplicates()
    detector.print_clone_set_stats(duplicates)
    num_cloned_files = sum(len(c) for c in duplicates)
    print('Number of cloned files:', num_cloned_files)
    register_database(duplicates, conn)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='./dup_network.db')
    args = parser.parse_args()
    main(args)
