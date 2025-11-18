# Deployment Guide

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Local Installation

1. Clone the repository:
```bash
git clone https://github.com/sxtyxmm/nifty-alpha-screen.git
cd nifty-alpha-screen
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

### Streamlit Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Command Line Interface

```bash
# Analyze a single stock
python cli.py --symbol RELIANCE

# Scan all NSE stocks
python cli.py --scan --top 30

# Analyze multiple specific stocks
python cli.py --symbols RELIANCE TCS INFY HDFCBANK
```

## Cloud Deployment

### Option 1: Streamlit Cloud (Recommended - Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file path to `dashboard.py`
7. Click "Deploy"

**Pros:**
- Completely free
- Easy deployment
- Automatic updates from GitHub
- Built-in SSL

**Cons:**
- Limited to 1GB RAM
- May be slow for large datasets

### Option 2: Railway.app

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Create a `Procfile`:
```
web: streamlit run dashboard.py --server.port $PORT
```

4. Deploy:
```bash
railway up
```

**Pros:**
- $5 free credit per month
- Better performance than Streamlit Cloud
- Support for environment variables

**Cons:**
- Paid after free tier
- Requires credit card

### Option 3: Render.com

1. Create a `render.yaml`:
```yaml
services:
  - type: web
    name: nifty-alpha-screen
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0
```

2. Connect your GitHub repository at [render.com](https://render.com)
3. Deploy automatically on push

**Pros:**
- Free tier available
- Auto-deploy from GitHub
- Good performance

**Cons:**
- Free tier spins down after inactivity
- Limited free hours

### Option 4: Docker Deployment

1. Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Build and run:
```bash
docker build -t nifty-alpha-screen .
docker run -p 8501:8501 nifty-alpha-screen
```

3. Deploy to any cloud provider (AWS, GCP, Azure, DigitalOcean, etc.)

**Pros:**
- Portable across platforms
- Production-ready
- Easy scaling

**Cons:**
- Requires Docker knowledge
- Manual setup on cloud

### Option 5: Heroku

1. Create `Procfile`:
```
web: streamlit run dashboard.py --server.port $PORT --server.enableCORS false
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

**Note:** Heroku removed free tier in November 2022. Minimum $7/month.

## Performance Optimization

### For Large Datasets

1. **Enable caching** (already implemented in dashboard.py):
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
```

2. **Limit number of stocks**:
   - Use the sidebar slider to analyze fewer stocks
   - Start with 50-100 stocks for testing

3. **Disable delivery data** for faster analysis:
   - Uncheck "Include Delivery Data" in sidebar

4. **Use batch processing**:
   - The pipeline uses parallel processing (ThreadPoolExecutor)
   - Adjust `max_workers` in `data_pipeline.py` if needed

### Production Settings

For production deployment, consider:

1. **Database caching**: Store fetched data in SQLite/PostgreSQL
2. **Scheduled updates**: Use cron jobs to update data daily
3. **CDN**: Use Cloudflare for static assets
4. **Load balancing**: For high traffic scenarios

## Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# Optional: Set custom user agent
USER_AGENT="YourApp/1.0"

# Optional: Set data refresh interval (seconds)
CACHE_TTL=3600

# Optional: Limit concurrent requests
MAX_WORKERS=10
```

## Monitoring

### Streamlit Cloud
- Built-in logs and metrics at share.streamlit.io

### Railway/Render
- Built-in monitoring dashboards
- Set up alerts for errors

### Self-hosted
Consider adding:
- **Sentry** for error tracking
- **Google Analytics** for usage
- **Prometheus + Grafana** for metrics

## Troubleshooting

### Common Issues

1. **"No data available"**
   - Check internet connection
   - NSE APIs may be down (use fallback symbols)
   - Try disabling delivery data

2. **Slow performance**
   - Reduce number of stocks analyzed
   - Disable delivery data fetching
   - Check cache settings

3. **Memory errors on Streamlit Cloud**
   - Reduce dataset size
   - Increase cache TTL
   - Consider upgrading to paid tier

4. **Rate limiting from Yahoo Finance**
   - Add delays between requests
   - Reduce `max_workers`
   - Use caching aggressively

## Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** (automatic on Streamlit Cloud/Railway/Render)
4. **Rate limit** user requests if public-facing
5. **Validate user inputs** to prevent injection attacks

## Maintenance

### Regular Updates

1. **Update dependencies** monthly:
```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

2. **Monitor API changes**:
   - Yahoo Finance API
   - NSE website structure

3. **Backup data** regularly if caching to database

## Support

For issues:
1. Check GitHub Issues
2. Review logs in deployment platform
3. Test locally first with `--no-delivery` flag

## License

MIT License - Free to use and modify
