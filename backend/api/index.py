import sys
import os

# Insert both backend folder and workspace root to ensure absolute package resolving works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from main import app
from mangum import Mangum

handler = Mangum(app)