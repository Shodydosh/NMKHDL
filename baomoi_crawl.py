from baomoi_urls import urls
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import urls from url.baomoi_urls

print(urls["Thế giới"])
