 Project name:
  Pet Care Scheduler

Description:
This Flask application is a pet management system that allows users to register, log in, manage their pets, and create and track tasks for their pets. The app incorporates a user authentication system, pet-related data management, task creation, and notifications. It is designed with functionality for managing pets and their associated tasks, as well as an option to export data in JSON format and generate reports.

Purpose:
The purpose of this system is to provide a simple web-based platform for pet owners to manage their pets' activities and tasks. It helps users stay organized by allowing them to track pet-related tasks, mark them as completed, and view reports on their pets' status. Additionally, it enables users to register, log in, and securely manage their pet-related data.

Value:
This pet management system provides significant value by offering pet owners an organized and user-friendly platform for managing their pets and associated tasks. The system streamlines task management by allowing users to create, view, and track tasks for each pet, ensuring that pet-related responsibilities are not forgotten. Additionally, the user authentication system ensures the privacy and security of each user's data, providing a personalized experience. With the ability to filter tasks based on completion status, users can easily prioritize tasks, improving overall organization. The system also offers the convenience of exporting data in JSON format, making it easy to backup or share pet-related information. Moreover, the ability to generate custom reports gives users valuable insights into their pets' status and activities, helping them to stay informed and make better decisions for their pets' well-being

Technologies Used:

The application is built using Flask, a lightweight and flexible Python web framework that is well-suited for developing small to medium-sized applications. Flask-SQLAlchemy is utilized for database interactions, allowing seamless integration between the Python code and the SQLite database to store user and pet data. Flask-Login handles user authentication, providing secure login, logout, and session management. To protect user passwords, Werkzeug is used to securely hash passwords before storing them in the database. For building forms and ensuring security, Flask-WTF integrates with WTForms, allowing easy creation and validation of forms like registration, login, and task management forms. To prevent cross-site request forgery (CSRF) attacks, CSRFProtect is employed. SQLite serves as the database, providing a lightweight storage solution for the pet data. Jinja2, the templating engine, is used to render dynamic HTML pages, while datetime ensures proper handling and validation of dates, such as task due dates. This technology stack allows for secure, efficient, and scalable application development.
