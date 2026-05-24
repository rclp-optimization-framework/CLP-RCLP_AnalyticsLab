# Common Path and Routing Errors

- **Database URL**: Must use environment variables for Supabase; do not hardcode the URL with special characters like `@` or `$` without URL encoding or using separate fields.
- **Stats route conflict**: The old backend had overlapping GET routes `/cache/bateria/stats/{bateria_id}` and `/cache/bateria/graph/{bateria_id}`. Ensure routes are ordered: specific paths before parameterized ones.
- **Frontend API base**: The `.env` in frontend must define `VITE_API_BASE_URL` so the Vite build includes the correct backend URL.
- **CORS setup**: FastAPI apps should include `CORSMiddleware` with wildcard origins for dev environments; production needs tighter controls.
- **TypeScript config split**: Vite projects need `tsconfig.app.json` for app code and `tsconfig.node.json` for Vite config; both must include necessary lib fields.
- **Recharts with D3**: The charting library depends on D3 types that need `Iterable` and `IterableIterator`; these come from the DOM lib, not ES2020 alone.
- **Docker image for backend**: Must include `minizinc` system package in Python images; FastAPI runs on uvicorn.
- **Frontend Nginx config**: Use `try_files $uri $uri/ /index.html` to support React Router client-side navigation.
