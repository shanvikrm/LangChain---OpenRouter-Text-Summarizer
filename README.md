# LangChain × OpenRouter Text Summarizer

A modern web application that summarizes text using LangChain and OpenRouter's AI models, featuring real-time streaming and file upload capabilities.

<div align="center">
  <img 
    src="preview.png" 
    alt="LangChain × OpenRouter Summarizer Interface showing text summarization in action" 
    width="800"
    style="border-radius: 8px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
  />
</div>


## Features

- ✨ Real-time text summarization
- 📁 Drag & drop file upload
- 🔄 Stream processing for large texts
- 🎨 Modern, responsive UI
- 🚀 Fast async processing

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 14+ (optional, for development)
- An OpenRouter API key

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd text
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv backend/.venv
backend/.venv/Scripts/activate

# Unix/MacOS
python -m venv backend/.venv
source backend/.venv/bin/activate
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open the frontend:
- Navigate to `frontend/index.html` in your web browser
- Or serve it using a simple HTTP server:
```bash
# Python 3
python -m http.server 3000 --directory frontend
```

3. Access the application at:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

## Usage

1. **Text Summarization:**
   - Paste text directly into the textarea
   - Click "Summarize Text" for instant summary

2. **File Upload:**
   - Drag & drop a .txt file or use the file picker
   - Click "Summarize File" to process

3. **Stream Processing:**
   - For longer texts, use "Stream Summary"
   - Watch real-time progress updates


## API Endpoints

- `POST /summarize` - Basic text summarization
- `POST /summarize-file` - File summarization
- `POST /summarize-stream` - Streaming summarization
- `POST /summarize-text-stream` - Text streaming with SSE
- `POST /summarize-file-stream` - File streaming with SSE

## Development

To modify the project:

1. Backend changes:
   - Edit files in `backend/app/`
   - Server auto-reloads with changes

2. Frontend changes:
   - Modify `frontend/index.html`
   - Refresh browser to see changes

## Troubleshooting

Common issues and solutions:

1. **CORS errors:**
   - Ensure backend is running with correct host/port
   - Check CORS middleware configuration

2. **API key issues:**
   - Verify .env file exists and has correct key
   - Check OpenRouter dashboard for key status

3. **File upload fails:**
   - Ensure file is .txt format
   - Check file size (keep under 10MB)

## License

MIT License - Feel free to use and modify for your needs.
