import requests
import os
from dotenv import load_dotenv

load_dotenv()

ADDRESS_VALIDATION_API_KEY = os.getenv("ADDRESS_VALIDATION_API_KEY")

def validate_address(address: str) -> dict:
    """
    Validates the provided address using an external API.
    Returns a dictionary with:
    {
        "valid": True/False,
        "formatted_address": "Cleaned, standardized address" (if valid),
        "message": "Error or status message"
    }
    """

    if address.strip() == "":
        return {"valid": False, "formatted_address": "", "message": "Address is empty."}

    try:
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": address,
            "apiKey": ADDRESS_VALIDATION_API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["features"]:
            properties = data["features"][0]["properties"]
            formatted_address = properties.get("formatted", address)
            return {
                "valid": True,
                "formatted_address": formatted_address,
                "message": "Address validated successfully."
            }
        else:
            return {
                "valid": False, 
                "formatted_address": "", 
                "message": "Address is not valid."
            }

    except Exception as e:
        return {
            "valid": False,
            "formatted_address": "",
            "message": f"Error validating address: {e}"
        }

"""if __name__ == "__main__":
    # CLI test
    test_address = input("Enter an address to validate: ")
    result = validate_address(test_address)
    print(result)"""