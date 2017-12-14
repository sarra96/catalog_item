-Item Catalog Project

-This is  project to develop an application that provides a list of items within a variety of           categories as well as provide a user registration and authentication system.
  Registered users will have the ability to post, edit and delete their own items.
   
   
                     -------------------------------------------------
-How to run the project :-	
	
  - Install Python 3 onto your computer.
  - Install Vagrant and VirtualBox.
  - Clone the fullstack-nanodegree-vm.
  - Start the virtual machine :
     - From your terminal, inside the vagrant subdirectory, run the command vagrant up.
     - Then run vagrant ssh to log in to your newly installed Linux VM!.
  - Extract compressed file 'catalog_item'.
  - Then cd into the vagrant directory and then cd to 'catalog_item' file 
  - Setup Database
     - use the following command 'python database_catlog.py '
     - then insert categories data by run command 'python catgories_databasesetup.py'
- Run this command 'python project_app.py'

- Access the application  using http://localhost:5000/

    
                     -------------------------------------------------

- JSON Endpoints
   - '/catalog/<int:cat_id>/items/JSON': - Displays items for a specific category.

  -  '/catalog/categries/JSON':-  Displays all categries.
                      -------------------------------------------------
 - What's included

  - project_app.py :- This is the main for the application
                               
  - database_catlog.py :- This is module contians The SQL database that includes three tables:
                            -The user table .
                            -The categories table  .
                            -The item table.
                            
 - catgories_databasesetup.py :- This is module inserts names of main categories
                                   in categories table.
- templates folder:- In Flask Application we put Html templates in  tempaltes folder.

- static folder:- In Flask Application we put CSS/JS/Images files in  static folder.