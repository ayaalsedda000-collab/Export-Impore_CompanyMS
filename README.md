EIMS 📊
Software Engineering

Project Description
A comprehensive system for managing employee data in companies, built using Python and Streamlit. The system provides an easy-to-use interface for managing employee records with search, filter, analysis, and export capabilities.

Main Features

1. Dashboard
   Display comprehensive employee statistics
   Total number of employees and departments
   Average salaries
   Number of active employees
2. Data Management
   View Data: Display all records in organized tables
   Search & Filter: Search data by name, department, position
   Add Records: Easily add new employees
   Edit Records: Update employee information
   Delete Records: Delete records with confirmation
3. Analytics & Charts
   Employee distribution by department
   Average salary by department
   Employee status distribution (Active/Inactive)
   Most common positions
4. Data Export
   Export data in CSV format
   Export data in Excel format
   Preview data before export
   Technologies Used
   Python 3.x: Main programming language
   Streamlit: Framework for building user interface
   SQLite: Database
   Pandas: Data processing and analysis
   Plotly: Creating interactive charts
   Requirements
   streamlit
   pandas
   plotly
   openpyxl
   Installation and Running
5. Install Requirements
   pip install -r requirements.txt
6. Run Application
   streamlit run app.py
7. Open Browser
   The application will automatically open in the browser at:

http://localhost:8501
Project Structure
.
├── app.py # Main application file
├── database.py # Database management
├── data_manager.py # Data management and analytics
├── requirements.txt # Required libraries
├── README.md # Project guide
└── company_data.db # Database (created automatically)
Sample Data
The system includes sample data for 5 employees to facilitate testing and demonstration.

Usage
Add New Employee
Select “➕ Add Data” from sidebar
Fill all required fields
Click “Add Record”
Search for Employee
Select “📋 View Data”
Use search box to search by name or department
Use filters to narrow results
Export Data
Select “📥 Export Data”
Choose desired format (CSV or Excel)
Click export button and download file
Developer
Software Engineering

License
This project is open source and available for educational and academic use.
