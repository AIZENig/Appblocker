# Appblocker
# Website & App Blocker Setup Guide (v3)

Blocks any websites AND apps you choose (not just Roblox), using a
password only your friend knows. You never see, type, or store the
real password anywhere.

Two people are involved:
- **Friend** — controls the password and the block list. Part A.
- **You** — runs the blocker on your laptop. Part B.

---

## Part A — What your FRIEND does (not you)

### A1. Create a GitHub account (if needed)
github.com → Sign up. Must be **their** account.

### A2. Create ONE public repository with TWO files
- New repository → any name (e.g. `lockfile`) → **Public** → Create.
- Add two files inside it:
  - `hash.txt` — the password hash (steps below)
  - `sites.txt` — one website per line, e.g.:
    ```
    roblox.com
    discord.com
    youtube.com
    ```

### A3. Generate the password hash
On their own computer:
```
pip install werkzeug
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('password: ')))"
```
- Type the real password when asked.
- Copy the **entire** output line, starting with `scrypt:` — this part
  is easy to miss when copying from a terminal, double check it's there.
- Paste it into `hash.txt` on GitHub → Commit changes.

### A4. Fill in sites.txt
- One website domain per line, no `http://`, no quotes. Example:
  ```
  roblox.com
  ```
- Commit changes.

### A5. Get both raw URLs and send them to you
Click each file → click **Raw** → copy the URL. You'll get two:
```
https://raw.githubusercontent.com/THEIR_USERNAME/lockfile/main/hash.txt
https://raw.githubusercontent.com/THEIR_USERNAME/lockfile/main/sites.txt
```

### A6. To change the password or the site list later
Just edit `hash.txt` or `sites.txt` on GitHub anytime and commit. Nothing
on your side needs to change — your laptop always re-reads both files.

---

## Part B — What YOU do

### B1. Save the script
Put `blockapp_v3.py` in a folder, e.g.:
```
C:\Users\Welcome\OneDrive\Desktop\appblocker
```

### B2. Install requirements
```
pip install requests psutil werkzeug
```

### B3. Point it at your friend's real URLs
Open `blockapp_v3.py` in Notepad, edit these two lines near the top:
```
HASH_FILE_URL = "..."
SITES_FILE_URL = "..."
```
Paste in the two URLs from A5. Save.

### B4. Test the unlock manually first
```
python blockapp_v3.py --unlock
```
Wrong password → "Wrong password." Real password from your friend →
"Unlocked for 30 minutes."

### B5. Run it as Administrator (required — this is new in v3)
Editing the hosts file to block websites needs admin rights.
- Right-click Command Prompt → **Run as administrator**
- `cd` into your folder, then:
```
python blockapp_v3.py
```
If you forget this step, it will print an error and refuse to run.

### B6. Make it start automatically at login, WITH admin rights
1. Task Scheduler → Create Task (not "Create Basic Task" — use the
   full "Create Task" so you get the privileges option).
2. General tab: boring/unrelated name → check **"Run with highest privileges"**.
3. Triggers tab: New → **At log on**.
4. Actions tab: New → Program/script: full path to `pythonw.exe` →
   Add arguments: full path to `blockapp_v3.py`.
5. Save.

### B7. When you want access (ask your friend first)
```
python blockapp_v3.py --unlock
```
30 minutes, then it locks itself again — websites blocked and target
apps closed automatically.

### B8. To re-lock early yourself
```
del state.json
```
(from the same folder)

---

## Honest limitation

You're still admin on your own laptop, so you can technically stop the
scheduled task or delete the folder. This isn't an unbreakable lock —
it's friction. It works because you never know the real password, and
sabotaging your own tool takes far more deliberate effort than clicking
"reinstall." For a harder version: make your own Windows account a
Standard (non-admin) user and give the admin password to your friend
too.
