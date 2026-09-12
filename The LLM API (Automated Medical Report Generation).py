import os
from openai import OpenAI

class ClinicalReportGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock-key"))

    def generate_diagnostic_summary(self, analysis_metrics: dict) -> str:
        prompt = f"""
        You are an expert clinical AI assistant for Cortex AI. 
        Generate a structured radiology draft report based on the following computer vision findings:
        - Anomaly Detected: {analysis_metrics.get('anomaly_detected')}
        - Malignancy Probability Score: {analysis_metrics.get('malignancy_probability') * 100:.2f}%
        
        Include sections: Findings, Quantitative Risk Assessment, and Recommended Follow-up Action.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a clinical decision support system producing accurate radiology reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content