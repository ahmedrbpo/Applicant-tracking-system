# Applicant-tracking-system

1. Prepare your code & environment

•	Save your Python script (for example, app.py) with the code you posted.
•	Make sure your code doesn’t rely on web-only features or paths.

2. Set up Python environment

Make sure each machine has:
•	Python installed (preferably Python 3.7 or higher).
•	Streamlit and other dependencies installed.

You can create a requirements.txt file to list dependencies:

streamlit
python-docx
PyPDF2

3. Installing dependencies

Users can run this command in their terminal/command prompt to install required packages:
pip install -r requirements.txt

If they don’t have pip, they’ll need to install Python from python.org which includes pip by default on recent versions.

4. Running the app locally

Once dependencies are installed, to run the Streamlit app:
streamlit run app.py

This command will start the Streamlit development server and open the app in a browser window on localhost, e.g., http://localhost:8501.

5. Notes:

•	Make sure your file reading code works well locally by testing it on some sample .docx and .pdf files.
•	If there are any issues with PyPDF2’s text extraction, consider alternative libraries like pdfplumber.
•	Users need to have an internet browser to view the Streamlit app interface.
•	If you want to share the app within a local network, Streamlit supports running with --server.address option.

Example to run on local network IP:

streamlit run app.py --server.address=0.0.0.0

Summary:

•	Save your script (e.g., app.py) and requirements.txt.
•	Install Python + dependencies on each machine.
•	Run via streamlit run app.py.
•	Use a browser locally to interact.

If you want more help creating an installer or packaging this app for easy distribution let me know!
