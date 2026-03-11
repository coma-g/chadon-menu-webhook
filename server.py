import subprocess
import os
import sys
from flask import Flask, jsonify, send_file

app = Flask(__name__)

# Script to generate HTML from CSV
GENERATE_HTML_SCRIPT = "generate_menu.py"
HTML_OUTPUT_PATH = "menu_b5.html"
PDF_OUTPUT_PATH = "menu_b5.pdf"

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Endpoint for Make.com webhook to generate and return PDF on Render."""
    try:
        print("Webhook received on Render: Starting PDF generation process...")
        
        # 1. Generate HTML
        print("Step 1: Generating HTML...")
        result_html = subprocess.run(
            ["python3", GENERATE_HTML_SCRIPT],
            capture_output=True, text=True
        )
        if result_html.returncode != 0:
            print(f"Error generating HTML:\n{result_html.stderr}")
            return jsonify({"status": "error", "message": f"HTML Generation Error: {result_html.stderr}"}), 500

        # 2. Convert HTML to PDF using installed headless Chrome
        if not os.path.exists(HTML_OUTPUT_PATH):
             return jsonify({"status": "error", "message": "HTML output file not found."}), 500

        print("Step 2: Converting HTML to PDF via headless Chrome...")
        
        # In Docker linux image, the Chrome binary is usually 'google-chrome'
        chrome_cmd = [
            "google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--print-to-pdf={PDF_OUTPUT_PATH}",
            "--print-to-pdf-no-header",
            HTML_OUTPUT_PATH
        ]
        
        result_pdf = subprocess.run(
            chrome_cmd,
            capture_output=True, text=True
        )

        if result_pdf.returncode != 0:
            print(f"Error generating PDF:\n{result_pdf.stderr}")
            return jsonify({"status": "error", "message": f"PDF Generation Error: {result_pdf.stderr}"}), 500
            
        print("Success: PDF generated successfully.")

        # 3. Return the generated PDF file
        if os.path.exists(PDF_OUTPUT_PATH):
            return send_file(
                PDF_OUTPUT_PATH,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='menu_b5.pdf'
            )
        else:
            return jsonify({"status": "error", "message": "PDF file not found after generation."}), 500

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint for Render dashboard"""
    return "Menu Webhook Server is running.", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
