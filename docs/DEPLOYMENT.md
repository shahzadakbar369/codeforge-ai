# A running link: Vercel and the Docker worker

Checked against official Vercel documentation on 2026-11-16. No deployment was created.

## Can we use Vercel?

Yes for the React frontend. Vercel also supports FastAPI and custom OCI container images, so saying it cannot host Python or containers would be incorrect. However, the current backend is not a drop-in Vercel deployment: it writes job files under the application directory, uses a process-local ThreadPoolExecutor after returning the request, and launches sibling PHP/Python containers via a Docker daemon. Hosting an app in a container does not by itself provide the Docker daemon/mount semantics this code expects.

Official FastAPI guidance uses queue-backed workers for tasks that outlive an API request. Vercel instances can scale down. This implementation needs persistent job state/artifacts and a compatible execution worker before hosting all stages there. A translation-only deployment that silently skips Docker would not be the full working demo.

## Least disruptive complete setup

Use a dedicated Linux VM with Docker for FastAPI, its job files and the verification worker. Either serve the built React app from that same FastAPI service behind HTTPS, or put React on Vercel and proxy /api/* to the backend's HTTPS address. The single-server option preserves the current same-origin routing with fewer moving parts.

Before external access, implement authentication/access restriction and request/job limits; the current service is explicitly a loopback, single-user prototype. Keep GROQ_API_KEY only on the backend. Never add it to VITE_ variables, the React bundle or public Git files. Use a private class-demo audience before considering public access. Docker runtime access belongs on the worker host, never in the browser.

## Vercel frontend settings (after a reachable backend exists)

- Import the GitHub repository into Vercel.
- Root directory: frontend/react-app.
- Framework preset: Vite.
- Build command: npm run build.
- Output directory: dist.
- Add a rewrite from /api/:path* to the chosen HTTPS backend's /api/:path*. Preserve job and download paths. Configure /docs separately if you want its header link to work; Swagger also needs /openapi.json.
- Keep requests on the frontend origin through the rewrite, or explicitly configure backend CORS if using direct browser requests. A Vercel frontend cannot reach a visitor's localhost server as a shared hosted backend.
- Test create, polling, report and ZIP download from the deployed frontend. A page loading is not proof that migration works.

The actual backend hostname, hosting account and access policy are not configured yet, so no placeholder production rewrite or misleading live link has been added.

## Before the morning presentation

The verified local app is the dependable full demo. Keep Docker Desktop and the local server running; use http://127.0.0.1:8001. A cloud link needs the backend hosting work above. Avoid a last-minute full serverless rewrite if the goal is a reliable presentation.

## Official references

- FastAPI support and background work: https://vercel.com/docs/frameworks/backend/fastapi
- Function lifecycle, duration and payload constraints: https://vercel.com/docs/functions/limitations
- Custom OCI containers and scale-down behavior: https://vercel.com/docs/functions/runtimes/container
