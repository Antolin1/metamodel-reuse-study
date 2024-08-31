CREATE TABLE metamodels (
	id integer primary key autoincrement,
	user TEXT NOT NULL,
	repo TEXT NOT NULL,
	repo_path TEXT NOT NULL,
	local_path TEXT,
	concepts TEXT,
	first_commit DATE,
	considered_commit DATE,
	author TEXT
);

CREATE TABLE duplicates (
    id integer primary key autoincrement,
    m1 INT NOT NULL,
    m2 INT NOT NULL,
    distance INT,
    CONSTRAINT fk_m1
        FOREIGN KEY (m1)
        REFERENCES metamodels (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_m2
        FOREIGN KEY (m2)
        REFERENCES metamodels (id)
        ON DELETE CASCADE
);