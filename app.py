import os
import json
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load or initialize employee data
DATA_FILE = 'employees.json'
def load_employees():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Initialize with 12 empty employee slots
        return [{'name': f'Employee {i+1}', 'tardy': 0, 'absent': 0, 'pdf': None} for i in range(12)]

def save_employees(employees):
    with open(DATA_FILE, 'w') as f:
        json.dump(employees, f, indent=4)

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_employees')
def get_employees():
    return jsonify(load_employees())

@app.route('/update_employee', methods=['POST'])
def update_employee():
    employees = load_employees()
    name = request.form['employeeName']
    tardy = int(request.form['daysTardy'])
    absent = int(request.form['daysAbsent'])

    # Check if employee exists, update or add
    employee_found = False
    for employee in employees:
        if employee['name'].lower() == name.lower():
            employee['tardy'] = tardy
            employee['absent'] = absent
            employee_found = True
            break

    # Handle PDF upload
    pdf_filename = None
    if 'pdfFile' in request.files:
        file = request.files['pdfFile']
        if file and file.filename.endswith('.pdf'):
            pdf_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
            if employee_found:
                employee['pdf'] = pdf_filename
            else:
                employees.append({'name': name, 'tardy': tardy, 'absent': absent, 'pdf': pdf_filename})
    elif not employee_found:
        employees.append({'name': name, 'tardy': tardy, 'absent': absent, 'pdf': None})

    save_employees(employees)
    return '', 204

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


