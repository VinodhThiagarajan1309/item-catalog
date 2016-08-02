# Item Catalog Application

## Applicationb Demo Link

  [Demo Link - Hosted using PythonAnyWhere.com](http://vinfosys9677.pythonanywhere.com/)
  
## About the application

  This is a simple application built using the following tools and technologies,
  
  * Python 2.5
  * Bootstrap CSS framework
  * Jinja2 Template Engine
  * Flask Framework
  * OAuth 2.0
  * Virtual Box ( During development)
  * [Hosted in PythonAnywhere.com](https://www.pythonanywhere.com)

## To Run the Application

  * Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/)
  * Clone this [repository](https://github.com/VinodhThiagarajan1309/item-catalog)
  * Launch the Vagrant VM
  * Login into the Virtual Machine as user 'vagrant'
  * Once logged in run the following command to setup the database,
      
      ```python
      python database_setup.py
      ```
  * This will create the sqllite DB that is required for the application to build.
  * Oauth 2.0  - Using Google Developer Console ,follow the link to create a unique client id for your application and
  download the client_secrets.json file from the resulting link.
  https://developers.google.com/adwords/api/docs/guides/authentication. 
  Replace that with the project's client_secrets.json file.
  * Next run the following command to start the Flask application on port 10000 ( You can change the port number)
      
      ```python
      python project.py
      ```

  * The application will now be up running in the following link [http://localhost:10000](http://localhost:10000)

## Screenshots

![IMAGE ALT TEXT HERE](https://s20.postimg.org/enzlazvnx/image.jpg)
![IMAGE ALT TEXT HERE](https://s20.postimg.org/6tyzplnv1/image.jpg)
![IMAGE ALT TEXT HERE](https://s20.postimg.org/v977qnmrx/image.png)
![IMAGE ALT TEXT HERE](https://s20.postimg.org/7tpalb30t/image.png)
![IMAGE ALT TEXT HERE](https://s20.postimg.org/lyqi9dmod/image.png)
![IMAGE ALT TEXT HERE](https://s20.postimg.org/bne5gpuz1/image.png)


    
