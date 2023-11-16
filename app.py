import os
import secrets
import cloudinary.uploader
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from functools import wraps
from flask import Flask, abort, render_template, url_for, flash, redirect, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, RecipeForm, CommentForm, ProfileForm, RatingForm, AdminEditRecipeForm
from models import db, User, Recipe, Comment, Rating

def save_picture(form_picture, old_image_id=None):
    try:
        # Check if the old image ID is not the default one before attempting to delete
        if old_image_id and old_image_id != 'default_k2ay8t':
            # Delete the old image from Cloudinary before uploading a new one
            cloudinary.uploader.destroy(old_image_id)
        
        # Proceed with uploading the new image and getting the new public ID
        upload_result = cloudinary.uploader.upload(
            form_picture,
            folder='profile_pics/'
        )
        
        # Save the new public ID and URL in the database
        new_image_id = upload_result['public_id']
        new_image_url = upload_result['url']

    except Exception as e:
        # Handle the exception, e.g., log it and return None or re-raise
        print(f"An error occurred: {e}")
        return None, None
    
    # Return both the public ID and the URL
    return new_image_id, new_image_url


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

FLASK_ENV = os.environ.get('FLASK_ENV')

if FLASK_ENV == 'dev':
    # Use SQLite for local development
    DATABASE_URI = f'sqlite:///{os.path.join(os.getcwd(), "recipes.db")}'
else:
    # Use PostgreSQL on Heroku for production
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    DATABASE_URI = DATABASE_URL

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Cloudinary
app.config['CLOUDINARY_CLOUD_NAME'] = os.environ.get('CLOUDINARY_CLOUD_NAME')
app.config['CLOUDINARY_API_KEY'] = os.environ.get('CLOUDINARY_API_KEY')
app.config['CLOUDINARY_API_SECRET'] = os.environ.get('CLOUDINARY_API_SECRET')

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have admin access.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    query = request.args.get('query')
    per_page = request.args.get('per_page', default=9, type=int)  # Default to 9 if per_page is not specified
    
    page = request.args.get('page', default=1, type=int)
    if query:
        pagination = Recipe.query.filter(
        Recipe.title.ilike(f"%{query}%") | 
        Recipe.ingredients.ilike(f"%{query}%")
        ).paginate(page=page, per_page=per_page, error_out=False)

    else:
        pagination = Recipe.query.paginate(page=page, per_page=per_page, error_out=False)

    recipes = pagination.items

    # Calculate the average rating for each recipe and store it in a dictionary
    avg_ratings = {}
    for recipe in recipes:
        ratings = [rating.value for rating in recipe.ratings]
        if ratings:
            avg_ratings[recipe.id] = sum(ratings) / len(ratings)

    return render_template('home.html', recipes=recipes, avg_ratings=avg_ratings, pagination=pagination, current_per_page=per_page)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()  # Create a form instance
    if form.validate_on_submit():
        title = form.title.data
        ingredients = form.ingredients.data
        steps = form.steps.data

        # Associate the recipe with the currently logged-in user
        new_recipe = Recipe(title=title, ingredients=ingredients, steps=steps, author=current_user)
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('add_recipe.html', form=form)  # Pass the form to the template


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)
    form = RecipeForm()
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.steps = form.steps.data
        try:
            db.session.commit()
            flash('Your recipe has been updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {e}', 'danger')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    elif request.method == 'GET':
        form.title.data = recipe.title
        form.ingredients.data = recipe.ingredients
        form.steps.data = recipe.steps
    return render_template('edit_recipe.html', title='Edit Recipe', form=form, recipe=recipe)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = CommentForm()  # Existing comment form
    rate_form = RatingForm()  # New rating form

    # Handle comment submission (existing logic)
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(content=form.content.data, user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    # Handle rating submission
    if rate_form.validate_on_submit() and current_user.is_authenticated:
        rating = Rating(value=rate_form.rating_value.data, user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(rating)
        db.session.commit()
        flash('Thanks for rating!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    
    # Fetching comments for the recipe (existing logic)
    comments = Comment.query.filter_by(recipe_id=recipe.id).order_by(Comment.timestamp.desc()).all()
    
    return render_template('recipe_detail.html', recipe=recipe, form=form, comments=comments, rate_form=rate_form)

@app.route('/rate_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    form = RatingForm()
    if form.validate_on_submit():
        existing_rating = Rating.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        
        if existing_rating:
            # If a rating exists, update its value
            existing_rating.value = form.rating_value.data
        else:
            # Else, create a new rating
            rating = Rating(value=form.rating_value.data, user_id=current_user.id, recipe_id=recipe_id)
            db.session.add(rating)

        db.session.commit()
        flash('Thanks for rating!', 'success')
    return redirect(url_for('recipe_detail', recipe_id=recipe_id))



@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=9, type=int)  # Default to 9 if per_page is not specified

    pagination = Recipe.query.filter_by(author=user).paginate(page=page, per_page=per_page, error_out=False)
    recipes = pagination.items

    return render_template('user_profile.html', user=user, recipes=recipes, pagination=pagination, current_per_page=per_page)


@app.route('/user/<string:username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            # If the user has a profile image ID and it's not the default,
            # pass it to save_picture to delete the old image.
            # Otherwise, pass None to not delete anything.
            old_image_id = current_user.profile_image_id if current_user.profile_image_id != 'default_k2ay8t' else None
            new_image_id, picture_url = save_picture(form.profile_picture.data, old_image_id)

            # Check if there was an error during image upload
            if new_image_id is None:
                flash('There was an issue uploading the image.', 'danger')
                return redirect(url_for('edit_profile', username=current_user.username))
            
            current_user.profile_picture = picture_url
            current_user.profile_image_id = new_image_id

        # Update other user fields
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data

        # Commit changes to the database
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        # Prepopulate form fields with current user data
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio

    # Render the profile editing template
    return render_template('edit_profile.html', form=form)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    recipes = Recipe.query.all()
    return render_template('admin_dashboard.html', users=users, recipes=recipes)

@app.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/recipes', methods=['GET', 'POST'])
@admin_required
def manage_recipes():
    recipes = Recipe.query.all()
    return render_template('admin_recipes.html', recipes=recipes)

@app.route('/admin/recipe/<int:recipe_id>/delete', methods=['POST'])
@admin_required
def admin_delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('admin_recipes'))
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully.', 'success')
    return redirect(url_for('manage_recipes'))

@app.route('/admin/recipe/<int:recipe_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    form = AdminEditRecipeForm()

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.steps = form.steps.data

        db.session.commit()
        flash('Recipe has been updated!', 'success')
        return redirect(url_for('manage_recipes'))

    elif request.method == 'GET':
        form.title.data = recipe.title
        form.ingredients.data = recipe.ingredients
        form.steps.data = recipe.steps

    return render_template('admin_edit_recipe.html', form=form, recipe=recipe)

@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html', title='Terms of Service')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html', title='Privacy Policy')

@app.route('/cookie_policy')
def cookie_policy():
    return render_template('cookie_policy.html', title='Cookie Policy')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
