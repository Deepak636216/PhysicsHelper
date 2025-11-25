# JEE-Helper Setup Guide

## Prerequisites

- Python 3.10 or higher
- Google AI API Key (Get from [Google AI Studio](https://aistudio.google.com/))
- Git

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Deepak636216/JEE-Helper.git
cd JEE-Helper
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Test API Connection

```bash
cd backend
python test_gemini_connection.py
```

You should see:
```
✅ GOOGLE_API_KEY found
✅ Genai client initialized successfully
✅ API call successful!
✅ All checks passed! You're ready to proceed.
```

### 5. Index Problem Bank (if you have existing problems)

```bash
# Place your problem JSON files in backend/data/problems/
python scripts/index_problems.py
```

This will generate `backend/data/extracted/problems_index.json`

## Next Steps

- [Architecture Overview](ARCHITECTURE.md)
- [Running the Backend](../backend/README.md)
- [API Documentation](API.md)

## Troubleshooting

### API Key Issues
- Ensure you've created a valid API key at [Google AI Studio](https://aistudio.google.com/)
- Check that the `.env` file is in the `backend/` directory
- Verify no extra spaces in the API key

### Import Errors
- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
- Try creating a virtual environment first

### Python Version
- This project requires Python 3.10+
- Check version: `python --version`
