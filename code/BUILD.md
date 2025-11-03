# Building and Running the Application

This application uses Flask as the backend and a React frontend. The React app is built once and then served by Flask, so you don't need Node.js running in production.

## Initial Setup (One-time)

### 1. Build the React Frontend

First, you need to build the React app into static files that Flask can serve:

```bash
cd code/frontend
npm install
npm run build
```

This will create a `dist` folder with all the static files that Flask will serve.

### 2. Run Flask

Once the React app is built, you only need to run Flask:

```bash
cd code
python kg_web_interface.py
```

The Flask server will:
- Serve the built React app for all routes (except `/api/*`)
- Handle all API requests at `/api/*`
- Automatically fallback to the original HTML template if the React build doesn't exist

Visit `http://localhost:5000` to use the application.

## Development Mode (Optional)

If you want to make changes to the React frontend and see them instantly:

1. **Terminal 1** - Run Flask backend:
   ```bash
   cd code
   python kg_web_interface.py
   ```

2. **Terminal 2** - Run React dev server:
   ```bash
   cd code/frontend
   npm run dev
   ```

Visit `http://localhost:5173` for the React dev server (which proxies API calls to Flask on port 5000).

## Production Deployment

For production:

1. Build the React app:
   ```bash
   cd code/frontend
   npm run build
   ```

2. Run Flask (no Node.js needed):
   ```bash
   cd code
   python kg_web_interface.py
   ```

That's it! Flask serves everything.

## Updating the Frontend

If you make changes to the React code:

1. Rebuild the frontend:
   ```bash
   cd code/frontend
   npm run build
   ```

2. Restart Flask (if needed):
   ```bash
   cd code
   python kg_web_interface.py
   ```

## Notes

- The `frontend/dist` folder contains the built React app
- Flask automatically serves files from `frontend/dist`
- All API routes are prefixed with `/api`
- The React app is a Single Page Application (SPA), so Flask serves `index.html` for all non-API routes

