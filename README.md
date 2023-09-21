# Recipe Realm

A web-based platform built with Flask where users can share, view, comment on, and manage their favorite recipes.

## Features

- **User Authentication**: Register, log in, and manage user profiles.
- **Recipe Management**: Add, edit, and delete recipes.
- **User Profiles**: View and edit user profiles, including profile pictures and bios.
- **Comments**: Users can comment on recipes.
- **User-friendly UI**: Leveraging Bootstrap for a responsive and attractive design.

## Setup and Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/nick-neely/Recipe-Realm.git
    cd Recipe-Sharing
    ```

2. **Set Up a Virtual Environment**:

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add the secret key: `SECRET_KEY=your_secret_key_here`

5. **Database Setup**:

    ```bash
    flask db upgrade
    ```

6. **Run the Application**:

    ```bash
    flask run
    ```

    The application should now be running at `http://127.0.0.1:5000/`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
