# Deployment Guide

This guide explains how to deploy the Knowledge Graph Explorer application to a production server.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Node.js and npm - only needed to build the React frontend

## Step 1: Build the React Frontend

Before deploying, you need to build the React application into static files:

```bash
cd code/frontend
npm install
npm run build
```

This creates a `dist` folder with all the static files Flask will serve.

## Step 2: Install Python Dependencies

On your server, install all required Python packages:

```bash
cd code
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Run the Application

### Development Mode

For testing or development:

```bash
cd code
python kg_web_interface.py
```

The app will be available at `http://localhost:5000`

### Production Mode with Gunicorn (Recommended)

For production deployment, use a WSGI server like Gunicorn:

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Run the application:**
   ```bash
   cd code
   gunicorn -w 4 -b 0.0.0.0:5000 kg_web_interface:app
   ```
   
   Options:
   - `-w 4`: Use 4 worker processes
   - `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
   - Adjust the worker count based on your server's CPU cores

### Production Mode with Waitress (Windows-friendly)

Waitress works on all platforms:

1. **Install Waitress:**
   ```bash
   pip install waitress
   ```

2. **Run the application:**
   ```bash
   cd code
   waitress-serve --host=0.0.0.0 --port=5000 kg_web_interface:app
   ```

## Step 4: Using a Reverse Proxy (Recommended for Production)

For production, use a reverse proxy like Nginx or Apache in front of your Flask app:

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service (Linux)

Create `/etc/systemd/system/kg-web.service`:

```ini
[Unit]
Description=Knowledge Graph Web Interface
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/phd-phase1/code
Environment="PATH=/path/to/phd-phase1/code/venv/bin"
ExecStart=/path/to/phd-phase1/code/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 kg_web_interface:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kg-web
sudo systemctl start kg-web
```

## Environment Variables (Optional)

You can configure the application using environment variables:

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
```

## File Structure

Make sure your deployment has this structure:

```
code/
├── kg_web_interface.py      # Main Flask application
├── requirements.txt          # Python dependencies
├── phase1_kg_starter.py     # KG builder
├── classes/
│   └── class_scientific_kg.py
├── data/                     # Knowledge graph JSON files
│   └── wave_kg.json
├── frontend/
│   └── dist/                 # Built React app (must exist!)
│       ├── index.html
│       └── assets/
└── venv/                     # Virtual environment (if used)
```

## Troubleshooting

### React app not loading
- Make sure you've run `npm run build` in `frontend/`
- Check that `frontend/dist/index.html` exists
- Verify file permissions allow Flask to read the files

### API routes not working
- Ensure Flask can access the `data/` directory
- Check that knowledge graph files have proper permissions
- Look at Flask logs for error messages

### CORS errors (if accessing from different domain)
- The app includes CORS support via flask-cors
- If issues persist, check firewall/proxy settings

## Security Considerations

1. **Never run Flask in debug mode in production:**
   - Remove `debug=True` from `app.run()`

2. **Use environment variables for secrets:**
   - Don't hardcode API keys or passwords

3. **Set proper file permissions:**
   - Restrict write access to `data/` directory
   - Only allow Flask process to modify KG files

4. **Use HTTPS:**
   - Configure SSL certificates with your reverse proxy

5. **Keep dependencies updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

