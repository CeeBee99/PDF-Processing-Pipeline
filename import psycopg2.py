import psycopg2

#Connect Database



#Creating cursor - Thing that's used to command Postgre

cursor = conn.cursor()

cursor.execute(
    CREATE TABLE files(
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    file_path TEXT NOT NULL UNIQUE,
    file_size INTEGER,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_type VARCHAR(100),
    uploaded_by VARCHAR(100)
))

#Saves changes
conn.commit()


#Close
cursor.close()
conn.close()
