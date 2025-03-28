from articles import surgical_device as s_d, diagnostic as dia


class ApiCaller:
    def __init__(self):
        self.analyzer_surgical = s_d.SurgicalDeviceAnalyzer()
        self.analyzer_diagnostic = dia.DiagnosticAnalyzer()

    def analyze_surgical_device(self, uploaded_file, device_name, technique):
        return self.analyzer_surgical.analyze_surgical_device(uploaded_file, device_name, technique)

    def analyze_diagnostic(self, uploaded_file, test_name, technique, sample_type, diagnostic_type):
        return self.analyzer_diagnostic.analyze_diagnostic(uploaded_file, test_name, technique, sample_type, diagnostic_type)
