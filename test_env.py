# test_env.py
import os
from dotenv import load_dotenv

# This function will attempt to find and load the .env file
# from the current directory.
load_dotenv()

# Now, we try to read the variables
app_id = os.getenv("EBAY_PROD_APP_ID")
cert_id = os.getenv("EBAY_PROD_CERT_ID")

print("--- Testing .env file loading ---")
print(f"Value for EBAY_PROD_APP_ID is: {app_id}")
print(f"Value for EBAY_PROD_CERT_ID is: {cert_id}")
print("---------------------------------")

if app_id and cert_id:
    print("\n✅ Success! The .env file was loaded correctly.")
else:
    print("\n❌ Failure! The .env file was NOT loaded.")
    print("Please check the troubleshooting steps.")