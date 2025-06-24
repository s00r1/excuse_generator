import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os
import pytest

os.environ.setdefault('GORQ_API_KEY', 'dummy')

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()
