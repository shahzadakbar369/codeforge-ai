# Free demonstration link and hosting

Checked 23 November 2026 against the official documentation linked below.

## Best option for this presentation: local app + temporary HTTPS tunnel

The full app needs persistent SQLite/job files, a background worker and a Docker daemon that can run PHP/Python containers. A Cloudflare Quick Tunnel can share the working laptop application without moving those components. It is a temporary demonstration link, not an always-on cloud deployment. Cloudflare documents that no account/domain is needed, links change on restart and uptime is not guaranteed.

1. Start Docker Desktop. Keep the laptop on power, awake and connected to the internet.
2. Terminal 1, from the project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\start_demo.ps1
```

3. Terminal 2:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\share_demo.ps1
```

The second script downloads the official Windows cloudflared client when missing and checks the release checksum. Share the printed HTTPS trycloudflare.com URL privately with the instructor/team. New users also need the invitation code from terminal 1 (saved only under ignored tmp/presentation/demo-invite.txt). Existing accounts sign in normally. Do not share your Groq key or personal login. The invitation gates registration, not an entire-network security perimeter.

Both terminals and the laptop must remain running. Ctrl+C in terminal 2 closes public access. Restarting it generates a different URL. Generate the link shortly before the presentation if you cannot keep the laptop running overnight. The free tunnel is suitable for a small demonstration, not load testing or permanent service. Backend Groq quotas still apply; free tunneling does not make inference unlimited.

Use -Port 8002 on both scripts if choosing another port. Stop the existing server before restarting; the app enforces one process per database. The backend trusts proxy headers only from loopback, which is where the tunnel connects. Verify signup, secure login cookie, migration, polling, history, report and download using the HTTPS link before sharing.

## Can Vercel host it?

Vercel supports both React/Vite and FastAPI. The existing backend is not a drop-in serverless deployment: it depends on local durable files, one process with an admission counter, background ThreadPoolExecutor work and sibling Docker containers. A container deployment does not automatically provide the Docker-daemon/mount setup this worker expects. Vercel's FastAPI guide recommends queue/workflow integrations for work independent of an API response.

For permanent hosting, move metadata/artifacts to durable storage, use queue-backed workers and a compatible sandbox worker host. A simpler initial deployment is one persistent Linux VM with Docker and HTTPS, serving the built React app from FastAPI. VM availability/pricing and account requirements vary; no permanent free VM is promised here.

A free Vercel frontend alone will show the interface but cannot make a shared backend appear at a visitor's localhost. Once you have a durable HTTPS backend, import frontend/react-app as a Vite project (npm run build, output dist), and proxy /api/*, /docs and /openapi.json to that backend. Same-origin cookie/CSRF behavior must be tested. No fake production hostname or placeholder deployment has been added.

## What about Render free?

Render has free web services, but its free service filesystem is ephemeral and free services do not support persistent disks. A redeploy/restart/spin-down can lose local SQLite/history/artifacts. Hosting an app container is also different from supplying the Docker worker environment required here. A translation-only version that skips execution is not the full verified demo. Do not promise the current full application as a free persistent Render deployment.

## What to say to the instructor

“We have a working HTTPS demonstration link connected to our local Docker-backed worker. It demonstrates the full workflow while our laptop is online. Permanent deployment needs a persistent worker, durable storage and operational monitoring.”

A stable, rehearsed demo makes a good impression; label the hosting arrangement accurately and keep the local app plus a saved successful report as backup.

## Official references

- Cloudflare Quick Tunnels: https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- Official client downloads: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/
- Vercel FastAPI and background work: https://vercel.com/docs/frameworks/backend/fastapi
- Render free limitations: https://render.com/docs/free
- Render persistent disks: https://render.com/docs/disks
