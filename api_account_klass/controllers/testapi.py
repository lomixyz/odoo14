import requests
from pprint import pprint
# Base URL of your Odoo instance
BASE_URL = 'http://localhost:8069'  # Change this to your Odoo instance URL
API_KEY = 'KROJER!@!123KROJER'  # Change this to your actual API key


def test_get_invoices():
    """Test the /api/invoices endpoint."""
    url = f"{BASE_URL}/api/invoices"
    headers = {'X-Api-Key': API_KEY}
    
    response = requests.get(url, headers=headers)
    pprint(response.json())


test_get_invoices()
