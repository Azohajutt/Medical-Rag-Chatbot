# Medical RAG Chatbot

An intelligent medical information and symptom checking assistant powered by Retrieval-Augmented Generation (RAG).
This application leverages Google's Gemini LLM to answer medical queries utilizing a verified local medical dataset. It runs on a FastAPI backend with ChromaDB for fast vector search and a native HTML/CSS/JS frontend.

## 🌟 Features

*   **Retrieval-Augmented Generation (RAG)**: Bases its answers on the provided `dataset.xlsx`, mapping symptoms and medical conditions accurately.
*   **Urgency Classification**: Automatically detects and flags query urgency (routine, urgent, emergency).
*   **Fast & Lightweight Frontend**: Uses vanilla JavaScript, HTML, and CSS (No NodeJS required).
*   **Gemini Integration**: Utilizes Google's fast and smart `gemini-3-flash-preview` model via the `google-generativeai` SDK.
*   **Vector Search Engine**: Employs `chromadb` along with `sentence-transformers` (`all-MiniLM-L6-v2`) to perform semantic searches over the medical dataset.

## 🛠️ Project Structure

```
Medical_chatbot/
├── backend/
│   ├── .env                    # Environment variables (Google API Key)
│   ├── chroma_db/              # Local vector database (auto-generated)
│   ├── ingest.py               # Script to embed and ingest dataset.xlsx
│   ├── main.py                 # FastAPI application
│   ├── rag_pipeline.py         # RAG and Context retrieval logic
│   └── requirements.txt        # Python dependencies
├── data/
│   └── dataset.xlsx            # Source medical knowledge base
└── frontend/
    ├── app.js                  # Frontend logic
    ├── index.html              # Chat interface
    └── style.css               # UI Styling
```

## 🚀 Setup & Installation

### 1. Prerequisites 
- Python 3.10+
- A modern web browser 

### 2. Install Dependencies
Navigate into the `backend` directory and set up your python environment:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the `backend/` directory and add your Google API Key:
```ini
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 4. Data Ingestion
Before running the bot, you must embed the dataset into the vector database. In your activated environment, run:
```bash
python ingest.py
```
This will read `../data/dataset.xlsx`, chunk the contents, and store the embeddings in `chroma_db/`.

## 💻 Usage

### 1. Start the API Server
In the `backend` directory with your virtual environment active, run:
```bash
uvicorn main:app --reload
```
The server will start at `http://localhost:8000`.

### 2. Open the Frontend
Simply open `frontend/index.html` in your web browser. You can double-click the file or use an extension like Live Server. 

*(Note: Ensure the backend is running before sending messages from the frontend).*
