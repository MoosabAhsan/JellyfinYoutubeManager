import requests
import json
import os
import shutil

# Define the URL and headers for authentication
auth_url = "http://127.0.0.1:8096/Users/authenticatebyname"
auth_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Authorization": ('MediaBrowser Client="Jellyfin Web", Device="Firefox", '
                      'DeviceId="TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0OyBydjoxMDkuMCkg'
                      'R2Vja28vMjAxMDAxMDEgRmlyZWZveC8xMTUuMHwxNzE0OTMwNjM3MzA1", Version="10.9.11"'),
    "Content-Type": "application/json",
    "Origin": "http://127.0.0.1:8096",
    "Connection": "keep-alive",
    "Cookie": "nc_sameSiteCookielax=true; nc_sameSiteCookiestrict=true"
}

# Define the JSON payload for authentication
auth_data = {
    "Username": "REDACTED",
    "Pw": "REDACTED"
}

# Step 1: Authenticate and get the Access Token
response = requests.post(auth_url, headers=auth_headers, json=auth_data)

if response.status_code == 200:
    response_json = response.json()
    access_token = response_json.get("AccessToken")
    
    if access_token:
        print("Access Token:", access_token)
        
        # Step 2: Build the Authorization header for future requests
        future_headers = {
            "Authorization": f'MediaBrowser Client="Jellyfin Web", Token="{access_token}"',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/json"
        }
        
        # Example: Make a GET request to retrieve favorite items
        get_url = "http://127.0.0.1:8096/Items?ParentId=REDACTED"  # Replace with the desired endpoint
        get_response = requests.get(get_url, headers=future_headers)
        
        if get_response.status_code == 200:
            try:
                get_response_json = get_response.json()
                favorite_items = [
                    item.get("Id") for item in get_response_json.get("Items", [])
                    if item.get("UserData", {}).get("IsFavorite", False)
                ]
                print("Favorite Item IDs:", favorite_items)
                
                # Step 3: Make a GET request for each ItemID to retrieve the Path
                for item_id in favorite_items:
                    item_url = f"http://127.0.0.1:8096/Items/{item_id}"
                    item_response = requests.get(item_url, headers=future_headers)
                    
                    if item_response.status_code == 200:
                        try:
                            item_response_json = item_response.json()
                            media_sources = item_response_json.get("MediaSources", [])
                            for source in media_sources:
                                full_path = source.get("Path")
                                if full_path:
                                    file_name = os.path.basename(full_path)  # Extract the file name
                                    print(f"ItemID: {item_id}, File Name: {file_name}")

                                    # Step 4: Copy the file to the new directory
                                    source_path = f"/home/REDACTED/Documents/jellyfin/media/youtube/{file_name}"
                                    destination_path = f"/home/REDACTED/Documents/jellyfin/media/permanent/{file_name}"
                                    
                                    try:
                                        shutil.copy(source_path, destination_path)
                                        print(f"Copied {file_name} to {destination_path}")
                                    except FileNotFoundError:
                                        print(f"File not found: {source_path}")
                                    except Exception as e:
                                        print(f"Error copying file {file_name}: {e}")
                        except json.JSONDecodeError:
                            print(f"ItemID: {item_id} - Response is not in JSON format.")
                    else:
                        print(f"Failed to retrieve item details for ItemID: {item_id} with status code {item_response.status_code}")
            except json.JSONDecodeError:
                print("Response is not in JSON format.")
                print(get_response.text)
        else:
            print(f"GET request failed with status code {get_response.status_code}:")
            print(get_response.text)
    else:
        print("Access Token not found in the response.")
else:
    print(f"Authentication failed with status code {response.status_code}: {response.text}")