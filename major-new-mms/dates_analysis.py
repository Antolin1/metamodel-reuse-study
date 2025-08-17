import pandas as pd
import matplotlib.pyplot as plt

repos_to_ignore = ['lucianoMarchezan/dataSTest', 'tue-mdse/ocl-dataset']

df = pd.read_csv('ecore_metadata_final.csv')
df = df[~df['repo_name'].isin(repos_to_ignore)]


print(df.columns)

print(df.head(5))

df['year'] = pd.to_datetime(df['file_last_commit_date']).dt.year

# Plot histogram
plt.figure(figsize=(8, 5))
df['year'].hist(bins=range(df['year'].min(), df['year'].max() + 2), edgecolor='black')
plt.title("Histogram of File Last Commit Years")
plt.xlabel("Year")
plt.ylabel("Frequency")
plt.xticks(range(df['year'].min(), df['year'].max() + 1))
plt.grid(axis='y')
plt.tight_layout()
plt.show()


df['year'] = pd.to_datetime(df['file_creation_date']).dt.year
# Plot histogram
plt.figure(figsize=(8, 5))
df['year'].hist(bins=range(df['year'].min(), df['year'].max() + 2), edgecolor='black')
plt.title("Histogram of File First Commit Years")
plt.xlabel("Year")
plt.ylabel("Frequency")
plt.xticks(range(df['year'].min(), df['year'].max() + 1))
plt.grid(axis='y')
plt.tight_layout()
plt.show()

distinct_repos = set(df['repo_name'])


distinct_repos = df.drop_duplicates(subset='repo_name')[['repo_name', 'repo_creation_date']]
distinct_repos['year'] = pd.to_datetime(distinct_repos['repo_creation_date']).dt.year

print("Number of distinct repos", len(distinct_repos))

# Plot histogram of repo creation years
plt.figure(figsize=(8, 5))
distinct_repos['year'].hist(bins=range(distinct_repos['year'].min(), distinct_repos['year'].max() + 2), edgecolor='black')
plt.title("Histogram of Repository Creation Years")
plt.xlabel("Year")
plt.ylabel("Number of Repositories")
plt.xticks(range(distinct_repos['year'].min(), distinct_repos['year'].max() + 1))
plt.grid(axis='y')
plt.tight_layout()
plt.show()

metamodel_counts = df['repo_name'].value_counts().reset_index()
metamodel_counts.columns = ['repo_name', 'num_metamodels']

# Merge with original df to get creation dates (drop duplicates to avoid repetition)
repo_creation_dates = df[['repo_name', 'repo_creation_date']].drop_duplicates()

# Merge counts with creation dates
metamodel_counts_with_dates = pd.merge(metamodel_counts, repo_creation_dates, on='repo_name')

# Display top 10
metamodel_counts_with_dates_top10 = metamodel_counts_with_dates.head(20)
print(metamodel_counts_with_dates_top10.head(20))

df['year'] = pd.to_datetime(df['repo_creation_date']).dt.year
print(df[df["path"].str.contains("bin/") & (df["year"] > 2023)])
print(df[df["path"].str.contains("impl/") & (df["year"] > 2023)])
print(df[df["path"].str.contains("src-gen/") & (df["year"] > 2023)])

print(df[df["path"].str.contains("bin/") ])
print(df[df["path"].str.contains("impl/") ])
print(df[df["path"].str.contains("src-gen/")])
