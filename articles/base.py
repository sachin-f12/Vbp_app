from utils import pdf_utils


class ArticleAnalyzer:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_file):
        return pdf_utils.extract_text_from_pdf(pdf_file)

    def remove_unwanted_sections(self, text, section_to_remove="References"):
        return pdf_utils.remove_unwanted_sections(text, section_to_remove)