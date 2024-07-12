![App Screenshot](https://github.com/titopuertolara/petiscanner/blob/main/assets/logo.png)
# OSV Scanner

This Dash Plotly app scans vulnerabilities in the open source tools reported in digital infrastructure documentation.

## Getting Started

Follow these instructions to set up and run the application on your local machine.

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/titopuertolara/petiscanner.git
   cd petiscanner

2. **Create a virtual environment**
   ```bash
   python -m venv yourvirtualenv

3. **Activate the virtual environment**
   ```bash
   source yourvirtualenv/bin/activate
   ```
   Or

   ```bash
   conda activate yourvirtualenv
   ```
4. **Request an API key**
   Go to https://nvd.nist.gov/developers/request-an-api-key
  

5. **Install the requirements**
   ```bash
   pip install -r requirements.txt
6.**Configure API key**
   Go to utils.py and edit the following line
   ```bash
   header={"apiKey":"put your apikey here"}
7. **Run the application**
   ```bash
   python appen.py


Open your web browser and navigate to http://127.0.0.1:8050.



   
   


