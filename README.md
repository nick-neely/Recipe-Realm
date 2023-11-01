# Recipe Realm

A web-based platform built with Flask where users can share, view, comment on, and manage their favorite recipes.

## Features

- **User Authentication**: Register, log in, and manage user profiles.
- **Recipe Management**: Add, edit, and delete recipes.
- **User Profiles**: View and edit user profiles, including profile pictures and bios.
- **Comments**: Users can comment on recipes.
- **Rating**: Users can rate recipes on a scale. The average rating for each recipe is displayed, providing insights into community preferences and recipe quality.
- **User-friendly UI**: Leveraging Bootstrap for a responsive and attractive design.

## Future Improvements
- Implement recipe categories or tags for better organization
- Allow image uploads for recipes
- Include a sharing system to easily share recipes
- Email verification and forgotten password reset
- More orientated for mobile
    
## Getting Started

Follow the instructions below to set up the environment and run this project locally.

## Setup and Installation

### Prerequisites

- Python 3.x
- pip
- virtualenv (optional but recommended)

### Local Development Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/nick-neely/Recipe-Realm.git
    ```

2. **Navigate to the project directory and create a virtual environment (optional):**

    ```bash
    cd recipe-sharing-app
    virtualenv env
    ```

3. **Activate the virtual environment:**

    - On macOS and Linux:
      ```bash
      source env/bin/activate
      ```
    - On Windows:
      ```bash
      .\env\Scripts\activate
      ```

4. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Create a `.env` file in the project root and add the following:**

    ```
    SECRET_KEY=<your-secret-key>
    DATABASE_URL=your_database_url  # Only needed if you're connecting to a remote database
    FLASK_ENV=dev
    ```
    Note: FLASK_ENV=dev ensures that the application runs in development mode and will show detailed error messages.

5. **Database Setup**:

    The application uses an SQLite database for development. To set up the database, run the following commands:
    
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

    Following the migration steps will create the recipes.db SQLite database file for you.

6. **Run the Application**:

    ```bash
    flask run
    ```

    The application should now be running at `http://127.0.0.1:5000/`.

## Deployment

For deployment on Heroku, ensure you set up a PostgreSQL database and link it with your application. The application is configured to use SQLite for local development and PostgreSQL for production.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
