import datetime

class ReportGenerator:
    """Generates print-ready HTML diagnostic reports for clinical records."""
    
    @staticmethod
    def generate_html_report(text, anonymized_text, model_name, prediction_label, confidence, tier, emotion, draft_response):
        """
        Creates a beautifully styled, print-friendly HTML document summarizing the risk analysis.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color coding for safety tiers in report
        tier_colors = {
            0: "#10b981", # Green
            1: "#3b82f6", # Blue
            2: "#f59e0b", # Orange
            3: "#ef4444"  # Red
        }
        tier_color = tier_colors.get(tier, "#6b7280")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Mental Health Risk Diagnostic Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #1f2937;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    border-bottom: 3px solid #3730a3;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1e1b4b;
                    margin: 0;
                }}
                .meta-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                .meta-table td {{
                    padding: 8px;
                    border: 1px solid #e5e7eb;
                }}
                .meta-table td.label {{
                    font-weight: bold;
                    background-color: #f9fafb;
                    width: 25%;
                }}
                .section-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #3730a3;
                    border-bottom: 1px solid #e5e7eb;
                    margin-top: 25px;
                    padding-bottom: 5px;
                }}
                .risk-badge {{
                    display: inline-block;
                    padding: 5px 12px;
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    background-color: {tier_color};
                }}
                .text-box {{
                    background-color: #f3f4f6;
                    border-left: 4px solid #6b7280;
                    padding: 15px;
                    font-style: italic;
                    margin: 10px 0;
                }}
                .draft-box {{
                    background-color: #eef2ff;
                    border-left: 4px solid #4f46e5;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .disclaimer {{
                    font-size: 11px;
                    color: #6b7280;
                    margin-top: 40px;
                    border-top: 1px solid #e5e7eb;
                    padding-top: 10px;
                }}
                @media print {{
                    body {{ padding: 0; }}
                    .disclaimer {{ position: fixed; bottom: 0; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Mental Health Risk Assessment Report</div>
                <div style="color: #6b7280; font-size: 13px;">System Diagnostic Log & Clinical Support Record</div>
            </div>

            <table class="meta-table">
                <tr>
                    <td class="label">Date & Time</td>
                    <td>{timestamp} (Local System Time)</td>
                    <td class="label">Assigned Model</td>
                    <td>{model_name}</td>
                </tr>
                <tr>
                    <td class="label">Predicted Tier</td>
                    <td><span class="risk-badge">Tier {tier}: {prediction_label}</span></td>
                    <td class="label">Confidence Score</td>
                    <td>{(confidence * 100):.2f}%</td>
                </tr>
                <tr>
                    <td class="label">Dominant Emotion</td>
                    <td>{emotion.upper()}</td>
                    <td class="label">Anonymization Mode</td>
                    <td>PII Auto-Mask Filter ACTIVE</td>
                </tr>
            </table>

            <div class="section-title">Anonymized Post Content</div>
            <div class="text-box">
                "{anonymized_text}"
            </div>

            <div class="section-title">Suggested Clinical Action Path & Guidelines</div>
            <ul>
                <li>Active Listening & Validation (Reflective statements regarding distress).</li>
                <li>Encourage connection to emergency/support networks (friends, family, trusted resources).</li>
                <li>Provide direct helpline information.</li>
            </ul>

            <div class="section-title">Empathy Draft Template Response (Non-Prescriptive)</div>
            <div class="draft-box">
                {draft_response}
            </div>

            <div class="disclaimer">
                <strong>SYSTEM DISCLAIMER:</strong> This report is generated by an automated Natural Language Processing system for research and decision-support purposes. It does not constitute a formal clinical diagnosis, medical opinion, or treatment plan. The assessment relies on linguistic heuristics which may produce errors (false positives or false negatives). For immediate psychological emergencies, please contact your local emergency response team or a national crisis helpline.
            </div>
        </body>
        </html>
        """
        return html_content

if __name__ == "__main__":
    report_html = ReportGenerator.generate_html_report(
        "I feel hopeless about school and want to end it.",
        "I feel hopeless about school and want to end it.",
        "BERT Classifier",
        "Moderate Risk",
        0.75,
        2,
        "sadness",
        "I'm sorry you are feeling this way. Please reach out to 988 for support."
    )
    print("HTML Report Generated, length:", len(report_html))
