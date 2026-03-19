import pytest
from fastapi.testclient import TestClient
from upload_search_functionality import app, PDF_search, ix
import os
import tempfile
from io import BytesIO



# Create a test client
client = TestClient(app)

class TestFileUpload:
    """Tests for PDF upload functionality"""
    
    def test_upload_pdf_success(self):
        """Test successful PDF upload"""
        # Create a fake PDF file
        file_content = b"PDF content here"
        files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
        
        response = client.post("/upload/", files=files)
        
        assert response.status_code == 200
        assert response.json() == {"filename": "test.pdf", "size": len(file_content), "indexed": True}
    
    def test_upload_multiple_files(self):
        """Test uploading multiple files"""
        files = [
            ("report.pdf", b"Report content"),
            ("invoice.pdf", b"Invoice content"),
            ("summary.pdf", b"Summary content")
        ]
        
        for filename, content in files:
            file_data = {"file": (filename, BytesIO(content), "application/pdf")}
            response = client.post("/upload/", files=file_data)
            assert response.status_code == 200
            assert response.json()["filename"] == filename
    
    def test_upload_no_file(self):
        """Test upload without file should fail"""
        response = client.post("/upload/")
        assert response.status_code == 422  # Unprocessable Entity


class TestFileRetrieval:
    """Tests for file listing and retrieval"""
    
    def test_list_files(self):
        """Test listing all uploaded files"""
        response = client.get("/files")

        print(f"Status code: {response.status_code}")
        print(f"Response body: {response.json()}")
        print(f"Response type: {type(response.json())}")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_existing_file(self):
        file_content = b"Test PDF content"
        file_data_1 = {"file": ("retrieve_test.pdf", BytesIO(file_content), "application/pdf")}
        
        upload_response = client.post("/upload/", files=file_data_1)
        print(f"Upload status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.json()}")
        
        # Check if file actually exists on disk
        file_path = os.path.join("data/pdfs", "retrieve_test.pdf")
        print(f"File exists? {os.path.exists(file_path)}")
        print(f"Files in directory: {os.listdir('data/pdfs')}")
        
        # Then retrieve it
        response = client.get("files/retrieve_test.pdf")
        print(f"Retrieve status: {response.status_code}")
        #print(f"Retrieve response: {response.json()}")
        
        assert response.status_code == 200

    def test_get_nonexistent_file(self):
        """Test retrieving a file that doesn't exist"""
        response = client.get("/files/nonexistent.pdf")
        assert response.status_code == 404


class TestSearch:
    """Tests for search functionality"""
    
    def test_search_returns_results(self):
        """Test that search function runs without errors"""
        # This is a basic test - PDF_search currently just prints
        # In a real app, you'd modify it to return results
        try:
            PDF_search("python")
            assert True  # If no exception, test passes
        except Exception as e:
            pytest.fail(f"Search failed with error: {e}")
    
    def test_search_with_empty_query(self):
        """Test search with empty string"""
        try:
            PDF_search("")
            assert True
        except Exception as e:
            pytest.fail(f"Search with empty query failed: {e}")
    
    def test_search_with_special_characters(self):
        """Test search with special characters"""
        try:
            PDF_search("python AND programming")
            assert True
        except Exception as e:
            pytest.fail(f"Search with special chars failed: {e}")


class TestIndexCreation:
    """Tests for Whoosh index"""
    
    def test_index_exists(self):
        """Test that index was created"""
        assert ix is not None
    
    def test_index_has_correct_schema(self):
        """Test that index has all expected fields"""
        schema_fields = list(ix.schema.names())
        expected_fields = ["path", "filename", "upload_time", "size", "content"]
        
        for field in expected_fields:
            assert field in schema_fields, f"Field {field} missing from schema"


class TestDeletion:

    def test_if_file_exists(self):

        file_content = b"PDF content here"
        files = {"file": ("example.pdf", BytesIO(file_content), "application/pdf")}
        
        response = client.post("/upload/", files=files)

        client.delete("/files/example.pdf")


        response = client.get("/files/exmaple.pdf")
        assert response.status_code == 404

    

# Run tests with: pytest test_upload_search.py -v
# Or with coverage: pytest test_upload_search.py --cov=upload_search_functionality