from fastapi import FastAPI
from api import article_retriever, Image_extractor,csv_manager,table_extractor,combined_extractor,common_word_analysis,pdf_filter

app = FastAPI()

# Article Retrieval Module
app.include_router(article_retriever.router, prefix="/articles", tags=["Articles"])
#common word analysis module
app.include_router(common_word_analysis.router,prefix="/common-word-analysis",tags=["Common Word Analysis"])
# Recent Searches Module
app.include_router(combined_extractor.router,prefix="/extract-all",tags=["Combined Extractor"])
#table extractor module
# app.include_router(table_extractor.router,prefix="/tables",tags=["Table Extractor"])

# # Image Extraction Module
# app.include_router(Image_extractor.router, prefix="/images", tags=["Image Extractor"])
# csv  file manger Module
app.include_router(csv_manager.router, prefix="/csv-manager", tags=["CSV Manager"])
#filter pdf 
app.include_router(pdf_filter.router,prefix="/filter-pdf",tags=["pdf filter"])
@app.get("/")
def root():
    return {"message": "Welcome to VBP FastAPI Backend"}
