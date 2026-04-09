# 🌐 Web-LLM Agentic System - Complete Full Stack

A production-ready full-stack web application for **advanced document processing, relevance filtering, and LLM integration** with a beautiful modern frontend and powerful backend API.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Node.js](https://img.shields.io/badge/Node.js-16+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 What is This?

This is a **complete redesign of the Web-LLM Agentic System** with:

- ✨ **Beautiful React Frontend** - Modern, responsive UI built with React 18 + TypeScript
- 🚀 **FastAPI Backend** - Async REST API exposing all Python functionality  
- 📄 **Document Processing** - Handle PDFs, URLs, audio files, and text documents
- 🤖 **ML Relevance Filtering** - Intelligent content extraction and filtering
- 📊 **Data Visualization** - Interactive charts and analytics dashboards
- 🔗 **Full Integration** - Seamless integration with original Python modules

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| 📤 **File Upload** | Upload PDFs, MP3s, WAV files directly to the browser |
| 🌍 **URL Processing** | Process any web URL and extract content |
| 🔍 **Content Extraction** | Automatically extract and clean text content |
| 🎯 **Relevance Filtering** | ML-powered filtering of relevant content segments |
| 📈 **Confidence Scoring** | Understand model confidence in results |
| 📊 **Analytics Dashboard** | Beautiful charts showing data statistics |
| ⚡ **Real-time Processing** | Instant feedback and progress indicators |
| 🎨 **Modern UI/UX** | Responsive design with smooth animations |
| 🔌 **REST API** | Full-featured API for programmatic access |
| 🐳 **Docker Ready** | Docker and Docker Compose configuration included |

## 📸 Screenshots

```
┌─────────────────────────────────────────────────────────┐
│  Web-LLM Agentic System                         🔵 Connected
├─────────────────────────────────────────────────────────┤
│ [Process Document] [View Results] [Data Analysis]      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Pick how to process content:                          │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ 🔗 Process URL   │  │ 📁 Upload File   │           │
│  │ Analyze web      │  │ Process PDFs &   │           │
│  │ content          │  │ Audio files      │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  Enter URL:                                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ https://example.com                              │  │
│  └──────────────────────────────────────────────────┘  │
│  [Process URL →]                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ 
- Node.js 16+
- About 5 minutes

### Option 1: Automatic Setup (Recommended)

**Windows:**
```bash
cd web-llm-agentic-system
setup.bat
```

**macOS/Linux:**
```bash
cd web-llm-agentic-system
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

```bash
# Backend setup
cd backend
python -m venv venv
# Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Unix)
pip install -r requirements_full.txt
python app/main.py

# In another terminal: Frontend setup
cd frontend
npm install
npm run dev
```

### Option 3: Docker

```bash
docker-compose up
```

## 🌐 Access the Application

After starting both services:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Web interface |
| **Backend** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **OpenAPI** | http://localhost:8000/openapi.json | OpenAPI schema |

## 📖 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - 5-minute quick reference guide
- **[FRONTEND_SETUP.md](./FRONTEND_SETUP.md)** - Detailed setup and configuration
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and data flow diagrams

## 💻 Tech Stack

### Frontend
```
React 18 + TypeScript
├── Vite (Build)
├── Tailwind CSS (Styling)
├── Recharts (Charts)
├── Framer Motion (Animations)
├── Lucide Icons (UI Icons)
└── Axios (HTTP Client)
```

### Backend
```
FastAPI + Uvicorn
├── Pydantic (Validation)
├── CORS Middleware
├── Async/Await
└── Integrated Python Modules
    ├── crawler/ (Document loading)
    ├── agent/ (Content processing)
    └── classifier/ (ML filtering)
```

### Data & ML
```
Original Python Modules
├── PDF Processing (PyPDF2, pdfplumber)
├── Audio Processing (librosa, scipy)
├── NLP Models (transformers, torch)
├── Knowledge Graphs (networkx)
└── Data Analysis (pandas, sklearn)
```

## 🎯 Main Capabilities

### 1. **Document Processing**
- Extract text from PDFs with formatting preservation
- Process web URLs and extract clean content
- Transcribe audio files to text
- Handle various document formats

### 2. **Content Analysis**
- Split documents into semantic segments
- Filter relevant content using ML models
- Calculate relevance and confidence scores
- Extract entities and key points

### 3. **Visualization & Analytics**
- Interactive data dashboards
- Model performance comparison
- Dataset statistics and distribution
- Inference time analysis

### 4. **API Access**
- REST API for all features
- Request/response in JSON
- Full input validation
- Comprehensive error handling

## 📚 API Examples

### Process a URL
```bash
curl -X POST "http://localhost:8000/process/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Upload and Process a File
```bash
curl -X POST "http://localhost:8000/process/file" \
  -F "file=@document.pdf"
```

### Get Dataset Statistics
```bash
curl http://localhost:8000/data/dataset
```

### Get Model Comparison Summary
```bash
curl http://localhost:8000/data/model-comparison/summary
```

## 📂 Project Structure

```
web-llm-agentic-system/
│
├── backend/                          # FastAPI Server
│   ├── app/
│   │   └── main.py                  # Main API with all endpoints
│   ├── requirements.txt             # Minimal dependencies
│   ├── requirements_full.txt        # All dependencies
│   ├── Dockerfile                   # Docker image config
│   └── .gitignore
│
├── frontend/                        # React Application
│   ├── src/
│   │   ├── components/              # React Components
│   │   │   ├── Header.tsx           # Navigation & status
│   │   │   ├── ProcessingForm.tsx   # File/URL input
│   │   │   ├── ResultsView.tsx      # Results display
│   │   │   └── DataAnalysis.tsx     # Analytics dashboard
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   ├── App.tsx                 # Main app
│   │   ├── main.tsx                # Entry point
│   │   └── index.css               # Tailwind styles
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── Dockerfile
│   └── .gitignore
│
├── agent/                           # Original agent modules
├── classifier/                      # ML classification
├── crawler/                         # Document loading
├── data/                            # Data storage
├── relevance_model/                 # ML models
│
├── QUICK_START.md                   # Quick reference
├── FRONTEND_SETUP.md                # Detailed setup guide
├── ARCHITECTURE.md                  # System architecture
├── docker-compose.yml               # Docker configuration
├── setup.bat                        # Windows setup script
├── setup.sh                         # Unix setup script
├── quickstart.py                    # Auto-start script
└── README.md                        # This file
```

## 🔧 Configuration & Customization

### Change API Port
Edit `backend/app/main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Change port here
```

### Change Frontend Port
Edit `frontend/vite.config.ts`:
```typescript
server: {
  port: 3000,  // Change port here
}
```

### Adjust Processing Parameters
Edit `backend/app/main.py`:
```python
MAX_WORDS_PER_SEGMENT = 100      # Change segment size
MAX_RELEVANT_SEGMENTS = 30       # Change limit
```

### Configure CORS Origins (Production)
Edit `backend/app/main.py`:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.9+)
python --version

# Check if port 8000 is free
netstat -an | grep 8000  # Unix/Mac
netstat -an | findstr 8000  # Windows

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend can't connect to API
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS in browser console
# Delete browser cache and reload

# Check frontend .env.local has correct API URL
```

### File upload fails
- Check file format is supported (PDF, MP3, WAV, M4A, TXT)
- Verify file size is reasonable
- Ensure write permissions in data/ directory
- Check disk space available

### Slow processing
- Reduce MAX_WORDS_PER_SEGMENT for faster processing
- Close other applications to free RAM
- Use lighter models or CPU-only inference

## 🔐 Security

⚠️ **This is a development setup**. For production:

1. **CORS** - Restrict to your domain only
2. **Authentication** - Add API key or OAuth
3. **HTTPS** - Use SSL/TLS certificates
4. **Rate Limiting** - Add request rate limits
5. **Input Validation** - Already implemented with Pydantic
6. **Secrets** - Use environment variables
7. **HTTPS** - Deploy with HTTPS

## 📈 Performance Tips

### Frontend
- Use React DevTools for profiling
- Enable code splitting for large components
- Use lazy loading for routes
- Compress images and assets

### Backend
- Adjust batch sizes for GPU processing
- Use connection pooling for databases
- Enable caching for repeated requests
- Monitor memory usage for large files

## 🚀 Deployment

### Heroku
```bash
# Configure Procfile and requirements
git push heroku main
```

### AWS Lambda + API Gateway
- Package backend with requirements
- Deploy React build to S3 + CloudFront

### Google Cloud
- Deploy FastAPI to Cloud Run
- Deploy React to Cloud Storage

### Azure
- App Service for FastAPI
- Static Web Apps for React

### Vercel + Railway
- Vercel for React frontend
- Railway for FastAPI backend

See [FRONTEND_SETUP.md](./FRONTEND_SETUP.md#deployment) for detailed deployment instructions.

## 🤝 Contributing

This is a complete implementation, but you can enhance it:

1. Add authentication system
2. Implement database persistence
3. Add WebSocket support for real-time updates
4. Create more advanced visualizations
5. Add export functionality (PDF/CSV)
6. Implement multi-language support
7. Create mobile app with React Native
8. Add advanced caching mechanisms

## 📞 Support & Resources

- **API Documentation** - View at http://localhost:8000/docs
- **FastAPI Docs** - https://fastapi.tiangolo.com/
- **React Docs** - https://react.dev/
- **TypeScript** - https://www.typescriptlang.org/
- **Tailwind CSS** - https://tailwindcss.com/

## 📝 Changelog

### v1.0.0 (Current)
- ✅ Full React frontend with TypeScript
- ✅ FastAPI backend with async support
- ✅ Complete API for document processing
- ✅ Interactive data visualization
- ✅ Docker and Docker Compose support
- ✅ Comprehensive documentation
- ✅ Setup scripts for all platforms

## 📄 License

Same as the original Web-LLM Agentic System project.

## 🙏 Acknowledgments

- Original Web-LLM Agentic System developers
- FastAPI community
- React community
- Open source contributors

---

## 🎓 Next Steps

1. **Get Started** → Read [QUICK_START.md](./QUICK_START.md)
2. **Setup** → Run `setup.bat` (Windows) or `setup.sh` (Unix)
3. **Explore** → Open http://localhost:5173
4. **Learn More** → Read [FRONTEND_SETUP.md](./FRONTEND_SETUP.md)
5. **Understand** → Review [ARCHITECTURE.md](./ARCHITECTURE.md)
6. **Extend** → Customize and deploy

---

**Built with ❤️ for advanced document processing and LLM integration**

⭐ **If you find this useful, please star the repository!**
"# Web-LLM-Agentic-System" 
