vbp_fastapi/
│
├── main.py                  # FastAPI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
│
├── api/                      # FastAPI route handlers
│   ├── term_extractor.py
│   ├── article_retriever.py
│   ├── file_manager.py
│   ├── pdf_processing.py
│   ├── search.py
│
├── services/                 # Core logic without UI dependencies
│   ├── google_scholar.py
│   ├── pubmed.py
│   ├── pdf_utils.py
│
├── utils/                    # Helper functions
│   ├── api_caller.py
│   ├── chrome_utils.py
│   ├── csv_utils.py
│
├── data/                     # Data storage
│
├── Input/                    # Input files and downloaded PDFs
│
└── tests/                    # Unit tests


install
choco install poppler
openai