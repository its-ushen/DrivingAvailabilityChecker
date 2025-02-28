from datetime import datetime
import os
from cloudflare_bypass import bypass_cloudflare
import json
import time

# Example GET request
def example_get():
    url = "https://myroadsafety.rsa.ie/api/v1/Availability/All/5a7cd10d-40f5-ef11-af8e-005056b9b50c/0fed074d-c2d6-e811-a2c0-005056823b22"
    
    # Optional: add authorization if needed
    headers = {
        "Authorization": "Bearer YOUR_TOKEN"
    }
    
    result = bypass_cloudflare(url, headers=headers)

    ## I want to check if there's an availaility
    available_locations = []
    for location in result:
        # Check if the 'nextAvailability' is not the default value
        if location.get('nextAvailability') and location['nextAvailability'] != '0001-01-01T00:00:00Z':
            available_locations.append(location)
    
    # If available locations found, send notification
    time = datetime.now().isoformat().replace(":", "-")
    if available_locations:
        print(f"Check RSA website tests available!!!!!")
        message = "🚨 *TEST SLOTS AVAILABLE!* 🚨\n\n"
        for location in available_locations:
            next_date = location.get('nextAvailability', 'Unknown')
            venue_name = location.get('name', 'Unknown Location')
            message += f"📍 *{venue_name}*\n"
            message += f"📅 Next Availability: {next_date}\n\n"

            with open("availability_log.txt", "a", encoding="utf-8") as log_file:
                # log the message
                log_file.write(f"{str(time)}: {message}\n")
        
    


    # I want to save the response to a file
    with open(os.path.join("responses", str(time) + ".json"), "w") as f:
        f.write(json.dumps(result, indent=2))

# Example POST request
def example_post():
    url = "https://myroadsafety.rsa.ie/api/v1/some-endpoint"
    
    data = {
        "param1": "value1",
        "param2": "value2"
    }
    
    result = bypass_cloudflare(url, method="POST", data=data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    print("Running GET example:")

    if not os.path.exists("responses"):
        os.makedirs("responses")

    while True:
        example_get()
        time.sleep(5)