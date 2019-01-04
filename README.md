# Logs Analysis Project -  Full Stack Nanodegree Udacity

## Project Description
Use PostgreSQL to query a database of a fictional news website and use the query results to answer the following questions:

1. Who are the most popular article authors of all time?

2. What are the most popular three articles of all time?

3. On which days did more than 1% of requests lead to errors?

## Dependencies
The following software is required:

* Python 3.6.8
* psycopg2 2.7.6
* PostgreSQL 9.5.10

To avoid dependency issues, it is recommended to use a Vagrant managed virtual machine (VM). 

To run the program on a VM will need to install:
*[Vagrant](https://www.vagrantup.com/downloads.html) - the software that configures the VM and lets you share files between your host computer and the VM's filesystem
*[VirtualBox](https://www.virtualbox.org/wiki/Downloads) - the software that actually runs the virtual machine. 
Install the VirtualBox platform package for your operating system. You do not need the extension pack or the SDK.

## Files
This project consists of the following files:

* `reports.py` - The Python program that connects to the database, executes and saves the SQL query results to file named `reports.txt`
* `newsdata.sql.zip` - The zip file containing the newsdata.sql file that will create the `news` PostgreSQL database and populate it with data
* `example_reports.txt` - An example of `reports.py` output
* `Vagrantfile` - The configuration file for Vagrant to create the VM
* `README.md` - the readme file


## Vagrant Instructions

1. Download or clone the project to a local directory

2. Open the CLI and navigate to the local directory where you downloaded the project. Cd into vagrant subdirectory.

3. Inside the vagrant subdirectory, run:
```bash
vagrant up
```
This will cause Vagrant to download the Linux operating system and install it.

Note, the first time this step it will take some time, as Vagrant will download the OS of the VM.

4. When vagrant up is finished running, run:
```bash
vagrant ssh
```
To log in to the VM!You can then log into the VM with the following command:

5. Inside the VM, find the vagrant directory
```bash
cd /vagrant
```

6. Unzip data and code to be used for creating the  `news` database:
```bash
unzip newsdata.sql.zip
```

7. Create the  `news` database and populate it with data:
```bash
psql -d news -f newsdata.sql
```

8. Run the `reports.py` program to execture PostgreSQL queries on `news` database:
```bash
python reports.py -db news
```
Where `-db` argument is the name of the database to be queried.

The `reports.py` output should now be displayed within same directory in `reports.txt`.

9. Exit and close  VM
After completing program, use `Ctrl+D` to exit VM and shut it down:
```bash
vagrant halt
```
