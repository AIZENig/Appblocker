"""
blocker_client.py (v2 — no server needed)

Your friend hosts NOTHING. They just create a small public GitHub repo
with one file, e.g. "hash.txt", containing a password hash they
generate themselves. You never see the plaintext password or even
help create the hash.

Usage:
  python blocker_client.py            -> runs the watcher loop forever
  python blocker_client.py --unlock   -> prompts for password, checks it
                                          against the hash on GitHub

--- Setup your friend does (not you) ---
1. They create a public GitHub repo, e.g. "myname/lockfile"
2. They generate a hash on their own machine:
     python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('password: ')))"
3. They paste that output into a file called hash.txt and push it to the repo.
4. To change the password later, they just edit hash.txt in the repo
   and commit — that's it, no redeploying, no server restarts.

--- What you do ---
Set HASH_FILE_URL below to:
  https://raw.githubusercontent.com/<their-username>/<their-repo>/main/hash.txt
"""

import sys
import time
import json
import os
import requests
import psutil
from werkzeug.security import check_password_hash

# ---- CONFIG: point this at your friend's repo file ----
HASH_FILE_URL = "https://raw.githubusercontent.com/AIZENig/Appblocker/refs/heads/main/hash.txt"
# ---------------------------------------------------------

PROCESS_NAMES = ["RobloxPlayerBeta.exe", "RobloxStudioBeta.exe"]
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
CHECK_INTERVAL_SECONDS = 15
DEFAULT_UNLOCK_MINUTES = 30

# local brute-force friction since there's no server to enforce it
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
ATTEMPTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attempts.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def is_unlocked():
    state = load_json(STATE_FILE, {"unlocked_until": 0})
    return time.time() < state.get("unlocked_until", 0)


def kill_roblox():
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] in PROCESS_NAMES:
                proc.kill()
                print(f"Blocked: killed {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def watcher_loop():
    print("Blocker running. Ctrl+C to stop (but that defeats the point).")
    while True:
        if not is_unlocked():
            kill_roblox()
        time.sleep(CHECK_INTERVAL_SECONDS)


def fetch_remote_hash():
    resp = requests.get(HASH_FILE_URL, timeout=10, headers={"Cache-Control": "no-cache"})
    resp.raise_for_status()
    return resp.text.strip()


def request_unlock():
    attempts = load_json(ATTEMPTS_FILE, {"count": 0, "locked_until": 0})
    now = time.time()
    if now < attempts.get("locked_until", 0):
        wait_min = int((attempts["locked_until"] - now) / 60) + 1
        print(f"Too many wrong tries. Locked out for {wait_min} more minute(s).")
        return

    try:
        remote_hash = fetch_remote_hash()
    except requests.RequestException as e:
        print(f"Could not fetch password file: {e}")
        return

    password = input("Enter password from your friend: ")

    if check_password_hash(remote_hash, password):
        unlocked_until = time.time() + DEFAULT_UNLOCK_MINUTES * 60
        save_json(STATE_FILE, {"unlocked_until": unlocked_until})
        save_json(ATTEMPTS_FILE, {"count": 0, "locked_until": 0})
        print(f"Unlocked for {DEFAULT_UNLOCK_MINUTES} minutes.")
    else:
        attempts["count"] = attempts.get("count", 0) + 1
        if attempts["count"] >= MAX_ATTEMPTS:
            attempts["locked_until"] = time.time() + LOCKOUT_MINUTES * 60
            attempts["count"] = 0
        save_json(ATTEMPTS_FILE, attempts)
        print("Wrong password.")


if __name__ == "__main__":
    if "--unlock" in sys.argv:
        request_unlock()
    else:
        watcher_loop()