from .base import ArticleAnalyzer
from utils import csv_utils
from run_analysis import run_openai_analysis_for_Influenza_diagnostic, run_openai_analysis_for_sars_diagnostic
from settings import BASE_DIR
import os


class DiagnosticAnalyzer(ArticleAnalyzer):
    def analyze_diagnostic(self, pdf_file, test_name, technique, sample, diagnostic_type):
        temp_pdf_path = os.path.join(BASE_DIR, "data", "temp.pdf")
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        # Extract text from PDF
        text = self.extract_text_from_pdf(temp_pdf_path)
        cleaned_text = self.remove_unwanted_sections(text)

        if diagnostic_type == "Influenza":
            path = os.path.join(BASE_DIR, "data", "flu.csv")
            # Run OpenAI analysis
            analysis_result = run_openai_analysis_for_Influenza_diagnostic(cleaned_text, test_name, technique, sample)
            fieldsname = [
                "Reference",
                "Test Name",
                "Technique",
                "Sample",
                "n",
                "InfluenzaABSympNAPositives",
                "InfluenzaABAsympPositives",
                "InfluenzaABPositives",
                "InfluenzaABNegatives",
                "InfluenzaBSympNAPositives",
                "InfluenzaBPositives",
                "InfluenzaBNegatives",
                "All True Positive Samples",
                "Negative Samples",
                "Influenza A Sensitivity/ PPA",
                "Influenza A Specificity/ NPA",
                "Influenza B Sensitivity/ PPA",
                "Influenza B Specificity/ NPA",
                "Influenza A/B (LDT) Ct Value Positive Threshold",
                "# Multiplex Differential Diagnoses Per Run",
                "Pathogen Sample Time to Result Hours",
                "Hands on Time (Instrument only) Hours",
                "Number of Steps Instrument only",
                "Percent who easily understood the user manual",
                "Percent of patients who found the test easy to use (as expected)",
                "Percent of patients who found the test very easy to use",
                "Percent who correctly interpreted the results",
                "Percent who were confident they could use the test at home"
            ]
        else:
            path = os.path.join(BASE_DIR, "data", "sars.csv")
            analysis_result = run_openai_analysis_for_sars_diagnostic(cleaned_text, test_name, technique, sample)
            fieldsname = [
                "Reference",
                "Test Name",
                "Technique",
                "Sample",
                "n",
                "COVIDSympNAPositives",
                "COVIDAsympPositives",
                "COVIDPositives",
                "COVIDNegatives",
                "SARS-CoV-2 Positive Percent Agreement",
                "SARS-CoV-2 Negative Percent Agreement",
                "SARS-CoV-2 Ct Value Positive Detection Cutoff",
                "SARS-CoV-2 Asymptomatic Sensitivity",
                "SARS-CoV-2 Symptomatic Sensitivity",
                "SARS-CoV-2 Asymptomatic Specificity",
                "SARS-CoV-2 Symptomatic Specificity",
                "SARS-CoV-2 Days Past Infection/Symptom Onset Sensitivity Day 0/2/6/10",
                "# Multiplex Differential Diagnoses Per Run",
                "Pathogen Sample Time to Result Hours",
                "Hands on Time (Instrument only) Hours",
                "Number of Steps Instrument only",
                "Percent who easily understood the user manual",
                "Percent of patients who found the test easy to use (as expected)",
                "Percent of patients who found the test very easy to use",
                "Percent who correctly interpreted the results",
                "Percent who were confident they could use the test at home"
            ]
        # Parse the response and save to CSV
        data = csv_utils.parse_response(analysis_result, pdf_file.name)
        data["Test Name"] = test_name
        data["Technique"] = technique
        data["Sample"] = sample
        csv_utils.write_data_to_csv(data, path, fieldsname)
        print(f"Returning output from Diagnostic file.")
        return analysis_result
