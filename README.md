# macOS Cloud App Pacemaker (Zero-Cost Keep-Alive System)

A lightweight, robust, and zero-cost architectural solution to eliminate cold starts on cloud-hosted application platforms (like Streamlit Community Cloud) and managed database clusters (like Supabase free tier). 

Instead of paying for expensive dedicated enterprise tiers to keep portfolio and demo projects active, this project leverages local, energy-efficient Apple Silicon hardware (macOS launchd) combined with headless browser automation (Playwright) to simulate organic user traffic and keep cloud infrastructure hot 24/7.

---

## System Architecture

The application is structured to follow a "no accidental architecture" philosophy—relying strictly on low-level OS utilities and isolated execution layers for maximum resiliance.
```
[ macOS Launchd Agent ]  <--- (Guarantees persistence, self-healing, & boot execution)
         │
         ▼
[ python -u keep_alive.py ] <-- (Unbuffered execution layer running in isolated venv)
         │
         ├───► [ Playwright Headless Chromium ] ───► Simulates active web traffic
         │                                                    │
         │                                                    ▼
         │                                         ┌───────────────────────────┐
         │                                         │ o Live App Target 1       │
         │                                         │ o Live App Target 2       │
         │                                         │ o Supabase Database Tier  │
         │                                         └───────────────────────────┘
         │                                                    │
         │                                                    ▼
         │                                         (Triggers runtime & DB handshakes)
         │
         ├───► [ macOS Notification Center ] ───► Native push alert on status change
```


---

## Key Engineering Highlights

* Resilience via OS Integration (launchd): Regulated via a dedicated macOS User LaunchAgent. By implementing <key>KeepAlive</key><true/>, the operating system actively monitors the process thread. If the Python script is terminated or crashes, launchd instantly auto-restarts it.
* True Client Simulation: Modern Single Page Applications (SPAs) like Streamlit cannot be kept awake using primitive HTTP GET requests (e.g., curl), as they require a JavaScript runtime to fire up WebSockets. This engine uses a headless Chromium layer to execute the full page lifecycle.
* Database Keep-Alive: By triggering the web application's initial load lifecycle (wait_until="load"), the underlying database layer (e.g., Supabase PostgreSQL) is forced to run its initial queries, preventing automated cloud project pausing due to inactivity.
* Unbuffered Session Logs (python -u): Utilizing unbuffered binary I/O flags prevents Python from holding log buffers in memory. All outputs are instantly flushed into keep_alive.log for reliable real-time tracking.
* Injection-Safe Shell Interaction: System notifications are channeled to the native macOS Notification Center using Python's subprocess pipeline. Isolating the arguments as strict list variables ensures special string characters (like // or .) in app titles do not break the shell boundary.

---

## Installation & Configuration

### 1. Clone & Setup Virtual Environment
``` git clone https://github.com/besserschmitt/mac-cloud-pacemaker.git
cd mac-cloud-pacemaker 
```

# Create and activate isolated environment
``` python3 -m venv venv
source venv/bin/activate 
```

# Install automated browser dependencies
``` pip install -r requirements.txt
playwright install chromium 
```

### 2. Configure Your App Targets
``` Open keep_alive.py and add your target URLs to the TARGET_APPS array:
TARGET_APPS = [
    "https://your-app-1.streamlit.app/",
    "https://your-app-2.streamlit.app/"
]
```

### 3. Deploy to macOS LaunchAgents
1. Copy the template plist file into your system's LaunchAgents directory:
```  cp config/com.username.keepalive.plist.example ~/Library/LaunchAgents/com.besserschmitt.keepalive.plist 
```
   
2. Open the file and replace YOUR_MACOS_USERNAME with your actual macOS shortname:
```   nano ~/Library/LaunchAgents/com.besserschmitt.keepalive.plist ```
   
3. Load and register the agent with the OS:
```   launchctl load ~/Library/LaunchAgents/com.besserschmitt.keepalive.plist ```

---

## Operations & Verification

The agent resets and spins up a fresh session log upon initialization. You can inspect the unbuffered stream at any time:

``` cat keep_alive.log ```

### Expected Output Structure:
``` 
--- Starting Keep-Alive Session: 2026-07-08 11:00:55 ---
Navigating to: https://your-app-1.streamlit.app/
Successfully pinged! App Title: 'Production Dashboard'
--- Session Finished. Sleeping for 12 hours... --- 
```

Whenever a keep-alive cycle concludes, a native macOS notification banner will trigger, signaling whether all target systems have successfully responded or if a timeout occurred.

## License
MIT License. Free for personal and commercial portfolio optimizations.