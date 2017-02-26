## Smart Triager Assistant for IBM (Development Phase)

# Requirements

- Python 2.7
- Python virtual environment

# Database Setup

- Create a database named ```triager_tickets``` in couchdb
- Change line:11 in ```triager/utility/CouchInterface.py```
- The address in the line is to be changed. address will be in the following format:
	- ```http://<username>:<password>@localhost:<port_number>/```

**NOTE: Use a user with administrator privileges in the database**

# Initial Data Setup

- All the required data files are to be stored in the folder triager/data
- The data files should have the following names.
	- ```Ticket_list.csv``` \- List of tickets
	- ```skills_tracker.csv``` \- The skills of employees
	- ```vacation_plan.csv``` \- The vacation plan of employees
	- ```utilization.csv``` \- Utilization report of employee
	- ```backlog_report.csv``` \- Backlog Report

# Setting up

- Clone the git repository
- Create virtual environment ```virtualenv venv```
- Activate virtual environment ```source venv/bin/activate```
- Install dependencies ```pip install -r requirements.txt```
- Go to the triager directory
- Run the driver script ```python driver.py```

**NOTE: The date is presently manually fed to the system. The date setting can be found in ```triager/driver.py``` line:54**