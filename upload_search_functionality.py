from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from whoosh.index import create_in, open_dir, exists_in

from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser

import PyPDF2

import time


import psycopg2
import psycopg2.pool

import os

#Note: with blocks are used to close the file after use which frees up memory.

#File Uploading

app = FastAPI()

#DATA_DIR = "data/pdfs"
#INDEX_DIR = "indexdir"


#Above can cause mixed inconsistent slashes so instead use this:

# Get the directory where this script is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build paths relative to script location
DATA_DIR = os.path.join(BASE_DIR, "data", "pdfs")
INDEX_DIR = os.path.join(BASE_DIR, "indexdir")


os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)



DB_CONFIG = {
    "host": "localhost",
    "database": "pfd",
    "port": 9999,
    "user": "postgres",
    "password": "Nihongo1@"
}

def init_database():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            file_size INTEGER,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content_type VARCHAR(100),
            uploaded_by VARCHAR(100)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

init_database()


db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,  # min and max connections
    **DB_CONFIG
)

#Define schema
schema = Schema(path=ID(stored=True),
                filename = TEXT(stored=True),
                upload_time = NUMERIC(stored=True),
                size = NUMERIC(stored=True),
                content = TEXT)


#Create or open index
if not exists_in(INDEX_DIR):
    ix = create_in(INDEX_DIR, schema)
else:
    ix = open_dir(INDEX_DIR)




@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):

    """Upload a PDF file and index its content"""


    file_path = os.path.join(DATA_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())


    #Add to search index

    writer = ix.writer()
    try:
        file_size = os.path.getsize(file_path)
        upload_timestamp = time.time()


# Extract text from PDF
        #with open(file_path, 'rb') as pdf_file:
            #pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            #content_text = ""
            #for page in pdf_reader.pages:
            #    content_text += page.extract_text()

        writer.add_document(
            path=file_path,
            filename=file.filename,
            upload_time=upload_timestamp,
            size=file_size,
            content=""  # Empty for now - extract PDF text here
        )
        writer.commit()
    except Exception as e:
        writer.cancel()
        raise e
        
   
    #Get database connection

    #conn = db_pool.getconn()
    #cursor = conn.cursor()

    #try:
        # Insert into database
        #cursor.execute("""
            #INSERT INTO files (filename, file_path, file_size)
            #VALUES (%s, %s, %s)
        #""", (file.filename, file_path, file_size))
        
        #conn.commit()
    #finally:
        #cursor.close()
        #db_pool.putconn(conn)
    

    return {
        "filename": file.filename,
        "size": file_size,
        "indexed": True
    }



@app.post("/delete/")
async def delete_f(file: UploadFile = File(...)):


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)

    writer = ix.writer()

    writer.delete_by_term('path', file_path)

    


    #Deletion from database
    

    conn = db_pool.getconn()
    cursor = conn.cursor()


    try:
        
        cursor.execute("""
            DELETE FROM files (filename, file_path, file_size)
            VALUES (%s, %s, %s)
        """, (file.filename, file_path, file_size))
        
        conn.commit()
    finally:
        cursor.close()
        db_pool.putconn(conn)

    writer.commit()
    #except Exception as e:
    writer.cancel()
    #raise e



    


@app.get("/files")
def list_files():
    """List all uploaded files"""
    files = os.listdir(DATA_DIR)
    return files

#@app.get("files/{filename}")
#def get_file(filename: str):
    #file_path = os.path.join(DATA_DIR, filename)
    #if not os.path.exists(file_path):
        #return {"error": "File not found"}, 404 
    #return FileResponse(file_path)


@app.get("/files/{filename}")
def get_file(filename: str):
    """Download a specific file"""
    print(f"=" * 50)
    print(f"get_file called with filename: '{filename}'")
    print(f"filename type: {type(filename)}")
    print(f"filename repr: {repr(filename)}")
    
    file_path = os.path.join(DATA_DIR, filename)
    print(f"Looking for file at: '{file_path}'")
    print(f"Absolute path: '{os.path.abspath(file_path)}'")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        print(f"File found! Returning FileResponse")
    if not os.path.exists(file_path):
        print(f"File NOT found!")
        print(f"Files in DATA_DIR: {os.listdir(DATA_DIR)}")
        raise HTTPException(status_code=404, detail="File not found") 

    
        #Raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)
#Search Functionality

@app.get("/search/")
def search_pdfs(q: str, limit: int = 10):
    """Search for PDFs using query string"""
    results = PDF_search(q, limit=limit)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


def PDF_search(query_str: str, limit: int = 10):
    """Search PDFs by filename and content"""
    fieldnames = ["filename", "content"]
    fieldboosts = {"filename": 2.0, "content": 1.0}
    
    with ix.searcher() as searcher:
        parser = MultifieldParser(fieldnames, ix.schema, fieldboosts=fieldboosts)
        query = parser.parse(query_str)  # FIXED: Removed quotes around query_str
        results = searcher.search(query, limit=limit)
        
        # Return results as list of dictionaries
        result_list = []
        for result in results:
            result_list.append({
                "path": result['path'],
                "filename": result['filename'],
                "score": result.score,
                "upload_time": result.get('upload_time'),
                "size": result.get('size')
            })
        
        return result_list

