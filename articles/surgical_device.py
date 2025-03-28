from .base import ArticleAnalyzer
from utils import csv_utils
from run_analysis import run_openai_analysis
from settings import BASE_DIR
import os
path = os.path.join(BASE_DIR, "data", "surgical_file.csv")


class SurgicalDeviceAnalyzer(ArticleAnalyzer):
    def analyze_surgical_device(self, pdf_file, device_name, technique):
        temp_pdf_path = os.path.join(BASE_DIR, "data", "temp.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        # Extract text from PDF
        text = self.extract_text_from_pdf(temp_pdf_path)
        cleaned_text = self.remove_unwanted_sections(text)

        # Run OpenAI analysis
        analysis_result = run_openai_analysis(cleaned_text, device_name, technique)
        print(analysis_result)

        # Parse the response and save to CSV
        data = csv_utils.parse_response(analysis_result, pdf_file.name)
        data["Device"] = device_name
        data["Technique"] = technique
        fieldsname = [
            "Reference", "Device", "Technique", "n", "Sural Nerve", "wound infection", "Superficial Infection",
            "Deep Infection", "rerupture", "AOFAS", "wound dehiscence",
            "Debridement", "Keloid Scars", "Hypertrophic Scars",
            "Average VAS Pain", "VAS Satisfaction Average Scores",
            "Load Failure", "ATRS Score 3 months", "ATRS Score 6 months",
            "ATRS Scores Post 2 Years", "OR Time (hours)",
            "Recovery Time (months)", "Time to Load Bearing",
            "Weeks to Rehabilitation", "Base Recovery Sporting",
            "Sport Recovery Time (months)", "Discontinued Previous Sport",
            "Short term Elongation Impairment", "Incision", "Hospital Stay"
        ]
        csv_utils.write_data_to_csv(data, path, fieldsname)
        print(f"Returning output from Surgical Device file.")

        return analysis_result