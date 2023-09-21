import os
import secrets
from dotenv import load_dotenv
from PIL import Image
from flask import Flask, abort, render_template, url_for, flash, redirect, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, RecipeForm, CommentForm, ProfileForm
from models import db, User, Recipe, Comment

def save_picture(form_picture):
    # Create a random hex for our picture filename to avoid any naming conflicts
    random_hex = secrets.token_hex(8)
    
    # Split the filename and its extension, we only need the extension
    _, file_extension = os.path.splitext(form_picture.filename)
    
    # Construct our new filename
    picture_filename = random_hex + file_extension
    
    # Set our picture path
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    
    # Resize the image before saving
    output_size = (125, 125)  # adjust the dimensions as needed
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.getcwd(), "recipes.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    query = request.args.get('query')
    if query:
        recipes = Recipe.query.filter(Recipe.title.contains(query) | Recipe.ingredients.contains(query)).all()
    else:
        recipes = Recipe.query.all()
    return render_template('home.html', recipes=recipes)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        steps = request.form['steps']
        author_id = 1  # For now, we'll just use 1 as the author ID
        new_recipe = Recipe(title=title, ingredients=ingredients, steps=steps, author_id=author_id)
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('add_recipe.html')

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
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, recipe_id=recipe.id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    comments = Comment.query.filter_by(recipe_id=recipe.id).order_by(Comment.timestamp.desc()).all()
    return render_template('recipe_detail.html', title=recipe.title, recipe=recipe, form=form, comments=comments)


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
    recipes = Recipe.query.filter_by(author=user).all()
    return render_template('user_profile.html', user=user, recipes=recipes)

@app.route('/user/<string:username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio

    return render_template('edit_profile.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
