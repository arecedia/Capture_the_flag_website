# Web Dev Project - Creation of a functioning website

The Scope of this project was to develop a web application with appropriate front and back-end technologies to implement user and session 
management, along with information retrieval and data persistance.

## Functions

A brief overview of all the important functions of the application are below:

### User Management

Program utilises JavaScript in order to collect usernames and passwords entered into the web application, before sending them back to the 
server. This then utilises JWT tokens to check if the user has entered the correct details or not, giving them a session cookie if they
have. The application also utilises similar techniques for creating user accounts, passing them a session cookie if the details entered
are valid.

### Session Management
Program generates a cookie containing a unique identifier, an expiration date, an issue time and an issuer. This is then used to make sure 
that the user is a valid user, and that they have access to the different pages of the application that they visit.

### Database Management
The application also contains a rudimentary database, which contains usernames, encrypted passwords, as well as which challenges they have 
passed. It also contains information about whether they are a base user or if they have elevated privilege, which would allow them to 
interact with different api functions.

### Testing
Application also has unittests, such that the different functions included within can be tested easily and with a multitude of different data
types, making sure that the program reacts accordingly to everything.
