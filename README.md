# Cultisk Backend Server

## NYP DSF1901 Year 2 Semester 2 Group Project

### Description
The backend server for Cultisk Data security toolkit

### Group:

* [Dylan](https://github.com/Dylan-Liew)
* [Joel](https://github.com/j041)
* [William](https://github.com/c0dn)
* [Kent](https://github.com/kentlow2002)
* [Cassandra](https://github.com/Cassandra-Fu)

### Technologies:
* Python > 3.7
* Flask Restx


### Developer Environment Setup
Recommended IDEs: Pycharm / Visual Studio Code  
This guide assumes you are using Bit 64 version of Windows.

* Install
  [Python](https://www.python.org/downloads/), 
  [Git](https://git-scm.com/downloads)
  
* Clone the repo and navigate to project folder
* Run `pip install -r requirements.txt` to install dependencies
* Add the following environment variable to the run configurations `OAUTHLIB_INSECURE_TRANSPORT=1`, `PYTHONPATH=<path to ./cultisk>`
* Run `flask run` to start server
