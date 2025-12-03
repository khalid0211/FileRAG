# FileRAG - Document Q&A with Google Gemini

A powerful file-based Retrieval Augmented Generation (RAG) system built with Streamlit and Google's Gemini AI platform. Upload documents, create a searchable knowledge base, and ask intelligent questions about your content.

## Features

- **Store Management**: Create and manage document stores (corpus) with Gemini File Search API
- **Document Management**: Upload, view, and delete documents from your store
- **Intelligent Q&A**: Ask questions and get accurate answers with source references
- **Query Logging**: Automatically log all queries and responses locally
- **User-Friendly Interface**: Beautiful Streamlit-based web interface

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/))

## Installation

### 1. Clone or Download the Repository

```bash
cd fileRAG
```

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

You have two options to configure your Gemini API key:

#### Option A: Using .env file (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### Option B: Enter in the UI

You can also enter your API key directly in the Streamlit sidebar when you run the application.

## Getting Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click on "Get API key" in the left sidebar
4. Click "Create API key in new project" (or select an existing project)
5. Copy the generated API key

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using FileRAG

#### 1. Store Management Tab

- **Create a Store**: Click "Create Store" to initialize your document repository
- **View Store Info**: See the number of documents and creation date
- **Delete Store**: Remove the entire store (use with caution)

#### 2. Document Management Tab

- **Upload Documents**:
  - Click "Choose files to upload"
  - Select one or multiple documents (PDF, TXT, DOC, DOCX, MD)
  - Click "Upload All" to add them to your store

- **View Documents**: See all uploaded documents in a table view

- **Delete Documents**:
  - Select a document from the dropdown
  - Click "Delete Selected" to remove it

#### 3. Ask Questions Tab

- Type your question in the chat input
- Get intelligent answers based on your documents
- View source references by expanding the "Sources" section
- Download your query history using the sidebar button

## Project Structure

```
fileRAG/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment file
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── src/                       # Source modules
│   ├── __init__.py
│   ├── gemini_client.py       # Gemini API wrapper
│   ├── store_manager.py       # Store/corpus management
│   ├── document_manager.py    # Document operations
│   └── chat_handler.py        # Query processing & logging
└── data/                      # Data directory
    ├── config.json            # Store configuration
    └── query_history.txt      # Query logs
```

## Features in Detail

### Store Management
- Automatically creates and manages Gemini corpus
- Persists configuration locally in `data/config.json`
- Validates store existence on startup

### Document Upload
- Supports multiple file formats (PDF, TXT, DOC, DOCX, MD)
- Batch upload capability
- Automatic file processing and indexing
- Real-time upload status feedback

### Intelligent Search
- Semantic search using Gemini's file search capabilities
- Returns relevant answers with source citations
- Handles "information not found" scenarios gracefully

### Query Logging
- Automatically logs all queries and responses
- Timestamped entries
- Includes source references
- Downloadable history file

## Troubleshooting

### API Key Issues
- Ensure your API key is valid and has access to Gemini API
- Check that the `.env` file is in the root directory
- Verify the key is not wrapped in quotes in the `.env` file

### File Upload Errors
- Ensure files are in supported formats
- Check file size limits (Gemini API has upload limits)
- Verify internet connection for API calls

### Store Not Found
- The store configuration is saved in `data/config.json`
- If deleted, you'll need to create a new store
- Existing stores in Gemini are linked by corpus name

## Limitations

- File upload size limited by Gemini API
- Free tier API quotas apply
- Document processing time depends on file size and complexity
- Query response time varies based on corpus size

## Privacy & Data

- Documents are uploaded to Google's Gemini platform
- Query logs are stored locally in `data/query_history.txt`
- API key should be kept secure and not committed to version control
- Review Google's Gemini terms of service for data handling

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

For issues related to:
- **Gemini API**: Visit [Google AI Studio](https://aistudio.google.com/)
- **This Application**: Create an issue in the repository

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Uses Google's Generative AI Python SDK

---

**Happy document searching!** 📚✨
