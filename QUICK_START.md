# Quick Reference Guide for Web-LLM Agentic System

## 🎯 Project Overview

This is a **complete full-stack implementation** of the Web-LLM Agentic System with:
- ✅ Modern React + TypeScript Frontend
- ✅ FastAPI Backend with Async Support
- ✅ Document Processing (PDFs, URLs, Audio)
- ✅ ML-based Relevance Filtering
- ✅ Interactive Data Visualizations
- ✅ Beautiful, Responsive UI

## 📂 What's Included

### Frontend (`/frontend`)
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Framer Motion** for animations
- **Axios** for API calls

### Backend (`/backend`)
- **FastAPI** for REST API
- **Async/Await** for performance
- **Pydantic** for validation
- **CORS** middleware
- **Integration** with original Python modules

### Documentation
- **FRONTEND_SETUP.md** - Detailed setup guide
- **ARCHITECTURE.md** - System architecture & data flow
- **This file** - Quick reference

## ⚡ Quick Start (5 Minutes)

### Option 1: Automatic Setup (Windows)
```bash
cd path/to/web-llm-agentic-system
setup.bat
```

Then in two separate terminals:
```
# Terminal 1 - Backend
cd backend
venv\Scripts\activate.bat
python app/main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Option 2: Automatic Setup (macOS/Linux)
```bash
cd path/to/web-llm-agentic-system
chmod +x setup.sh quickstart.py
./setup.sh
```

Then:
```bash
python quickstart.py
```

### Option 3: Docker
```bash
docker-compose up
```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📝 Features by Tab

### 1. PROCESS DOCUMENT Tab
- **Upload Files**: PDF, MP3, WAV, M4A, TXT, HTML
- **Process URLs**: Enter any web URL
- **Drag & Drop**: Drag files directly to upload area
- **Real-time Processing**: See status updates

### 2. VIEW RESULTS Tab
- **Relevant Segments**: List of filtered content
- **Relevance Scores**: Visual progress bars
- **Confidence Metrics**: Model confidence levels
- **Raw Text Preview**: See extracted text
- **Processing Stats**: Time and count metrics

### 3. DATA ANALYSIS Tab
- **Sample Distribution**: Pie chart of dataset
- **Model Comparison**: Bar charts comparing models
- **Time Series Analysis**: Inference time trends
- **Statistical Summaries**: Key metrics and percentages

## 🛠️ Common Tasks

### Process a Document
1. Click "Process Document" tab
2. Choose "Upload File" or "Process URL"
3. Select file or enter URL
4. Click "Process" button
5. Wait for completion
6. View results in "View Results" tab

### View Analysis
1. Click "Data Analysis" tab
2. Charts load automatically
3. Hover over charts for details
4. Check summary statistics

### Access API Directly
```bash
# Process URL
curl -X POST "http://localhost:8000/process/url?url=https://example.com"

# Upload file
curl -X POST "http://localhost:8000/process/file" \
  -F "file=@document.pdf"

# Get dataset stats
curl http://localhost:8000/data/dataset

# Get model comparison
curl http://localhost:8000/data/model-comparison/summary
```

## 📊 API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/process/url` | Process URL |
| POST | `/process/file` | Process uploaded file |
| GET | `/data/dataset` | Dataset statistics |
| GET | `/data/model-comparison` | Model comparison data |
| GET | `/data/model-comparison/summary` | Aggregated summary |
| GET | `/results` | List all results |
| GET | `/results/{id}` | Get specific result |

## 🚨 Troubleshooting

### Frontend won't connect to API
- ✅ Check backend is running: `http://localhost:8000/health`
- ✅ Check frontend API URL in `frontend/.env.local`
- ✅ Check browser console for errors
- ✅ Clear browser cache and reload

### Backend won't start
- ✅ Check Python version: `python --version` (need 3.9+)
- ✅ Check venv is activated
- ✅ Reinstall dependencies: `pip install -r requirements.txt`
- ✅ Check port 8000 is free: `netstat -an | findstr :8000`

### File upload fails
- ✅ Check file format is supported
- ✅ Check file size is reasonable
- ✅ Check disk space available
- ✅ Check backend logs for errors

### Charts not loading
- ✅ Wait for data to load (check network tab)
- ✅ Ensure dataset.json exists in data/
- ✅ Check browser console for JavaScript errors
- ✅ Try refreshing the page

## 📚 Project Structure

```
web-llm-agentic-system/
├── backend/                          # FastAPI backend
│   ├── app/main.py                  # Main API
│   ├── requirements.txt             # Minimal deps
│   └── requirements_full.txt        # All deps
├── frontend/                         # React app
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── services/api.ts          # API client
│   │   ├── App.tsx                  # Main app
│   │   └── index.css                # Styles
│   ├── package.json                 # Node deps
│   └── vite.config.ts               # Vite config
├── agent/                           # Original modules
├── classifier/                      # ML classifier
├── crawler/                         # Document loaders
├── data/                            # Data storage
├── FRONTEND_SETUP.md               # Detailed setup guide
├── ARCHITECTURE.md                 # System architecture
├── setup.bat                       # Windows setup
├── setup.sh                        # Unix setup
├── quickstart.py                   # Auto-start script
└── docker-compose.yml              # Docker config
```

## 🔧 Configuration

### Backend (main.py defaults)
```python
MAX_WORDS_PER_SEGMENT = 50      # Adjust segment size
MAX_RELEVANT_SEGMENTS = 20      # Limit results
CORS origins = localhost:3000, localhost:5173
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Local Production Build
```bash
# Frontend
cd frontend
npm run build
npm run preview

# Backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Docker Production
```bash
docker-compose -f docker-compose.yml up -d
```

### Cloud Deployment
- **Frontend**: Vercel, Netlify, GitHub Pages
- **Backend**: Heroku, AWS, Google Cloud, Azure

## 🔐 Security Notes

⚠️ **Development Mode** - CORS allows all origins
- Change CORS settings in `backend/app/main.py` for production
- Validate all user inputs (already done with Pydantic)
- Use HTTPS in production
- Store secrets in environment variables

## 📞 API Response Examples

### Process URL Success
```json
{
  "source": "https://example.com",
  "source_type": "url",
  "raw_text": "...",
  "total_segments": 25,
  "relevant_segments": [
    {
      "id": "seg_0",
      "text": "...",
      "is_relevant": true,
      "relevance_score": 0.95,
      "confidence": 0.87
    }
  ],
  "processing_time": 2.34
}
```

### Dataset Statistics
```json
{
  "total_samples": 5000,
  "relevant_count": 3200,
  "irrelevant_count": 1800,
  "relevant_percentage": 64.0
}
```

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Recharts](https://recharts.org/)

## 🎯 Next Steps

1. ✅ Clone/setup the project
2. ✅ Run setup script or manual setup
3. ✅ Start backend and frontend
4. ✅ Open http://localhost:5173
5. ✅ Try processing a document
6. ✅ Explore data analysis
7. ✅ Read ARCHITECTURE.md for deep dive
8. ✅ Customize and extend as needed

## 📝 Need Help?

Check these files:
- **Setup Issues**: See FRONTEND_SETUP.md Troubleshooting
- **Architecture**: See ARCHITECTURE.md
- **API Usage**: See FRONTEND_SETUP.md API Endpoints
- **Code Examples**: See component files in `frontend/src/components/`

## ⭐ Key Features

- 🎨 Beautiful modern UI with Tailwind CSS
- ⚡ Fast async backend with FastAPI
- 📊 Interactive charts with Recharts
- 🎬 Smooth animations with Framer Motion
- 📱 Responsive design for all devices
- 🔍 Real-time document processing
- 🤖 ML-based relevance filtering
- 📈 Comprehensive data analysis

---

**Built with ❤️ for advanced document processing and LLM integration**
