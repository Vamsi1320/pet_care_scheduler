import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petsinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    pets = db.relationship('Pet', backref='owner', lazy=True)

# Pet Model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='pet', lazy=True)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)  # Added field for task completion
# Insurance Model
class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    renewal_date = db.Column(db.Date, nullable=False)
    claims = db.Column(db.String(255), nullable=True)
    payments = db.Column(db.String(255), nullable=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', backref='insurance', uselist=False)

# Insurance Form
class InsuranceForm(FlaskForm):
    policy_number = StringField('Policy Number', validators=[DataRequired()])
    provider = StringField('Insurance Provider', validators=[DataRequired()])
    renewal_date = StringField('Renewal Date (YYYY-MM-DD)', validators=[DataRequired()])
    claims = StringField('Claims')
    payments = StringField('Payments')
    submit = SubmitField('Add Insurance')

# Model for Vaccination
class Vaccination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vaccine_name = db.Column(db.String(100), nullable=False)
    date_administered = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date, nullable=True)
    vet_clinic = db.Column(db.String(255), nullable=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration Form
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match!")])
    submit = SubmitField('Register')

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Pet Form
class PetForm(FlaskForm):
    name = StringField('Pet Name', validators=[DataRequired(), Length(min=2, max=100)])
    type = StringField('Pet Type', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Add Pet')

# Task Form
class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description')
    due_date = StringField('Due Date', validators=[DataRequired()])
    submit = SubmitField('Add Task')

# Task Filter Form for Upcoming Tasks
class TaskFilterForm(FlaskForm):
    filter = SelectField('Filter by Status', choices=[('all', 'All'), ('completed', 'Completed'), ('pending', 'Pending')], default='all')
    submit = SubmitField('Apply Filter')


# Form for Adding Vaccination
class VaccinationForm(FlaskForm):
    vaccine_name = StringField('Vaccine Name', validators=[DataRequired(), Length(min=2, max=100)])
    date_administered = StringField('Date Administered (YYYY-MM-DD)', validators=[DataRequired()])
    next_due_date = StringField('Next Due Date (YYYY-MM-DD, optional)')
    vet_clinic = StringField('Vet Clinic')
    submit = SubmitField('Add Vaccination')

# Home Route
@app.route('/')
def index():
    pets = Pet.query.all()
    return render_template('index.html', pets=pets)

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()  # Store email in lowercase
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please log in.", "danger")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(name=form.name.data, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid password. Please try again.", "danger")
        else:
            flash("User not found. Please check your email.", "danger")
    return render_template('login.html', form=form)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Add Pet Route
@app.route('/add_pet', methods=['GET', 'POST'])
@login_required
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        new_pet = Pet(name=form.name.data, type=form.type.data, age=form.age.data, owner_id=current_user.id)
        db.session.add(new_pet)
        db.session.commit()
        flash("Pet added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_pet.html', form=form)

# Add Task Route
@app.route('/add_task/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_task(pet_id):
    form = TaskForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        due_date_str = form.due_date.data

        if not title or not due_date_str:
            flash("Title and due date are required!", "danger")
            return redirect(url_for('index'))

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date < datetime.today().date():
                flash("Due date cannot be in the past!", "danger")
                return redirect(url_for('index'))
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('index'))

        new_task = Task(title=title, description=description, due_date=due_date, pet_id=pet_id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!", "success")
        return redirect(url_for('index'))

    return render_template('add_task.html', form=form, pet_id=pet_id)

# Mark Task as Completed Route
@app.route('/mark_task_complete/<int:task_id>', methods=['POST'])
@login_required
def mark_task_complete(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
        flash("Task marked as completed!", "success")
    return redirect(url_for('view_task', task_id=task_id))  # Redirect back to the task view page

# Upcoming Tasks Route with Filtering
@app.route('/upcoming_tasks', methods=['GET', 'POST'])
@login_required
def upcoming_tasks():
    form = TaskFilterForm()  # Create the form for filtering tasks
    filter_status = form.filter.data  # Get filter data from form

    if filter_status == 'completed':
        tasks = Task.query.filter_by(completed=True).all()
    elif filter_status == 'pending':
        tasks = Task.query.filter_by(completed=False).all()
    else:
        tasks = Task.query.all()  # Get all tasks if no filter is applied
    
    return render_template('upcoming_tasks.html', tasks=tasks, form=form)  # Pass the form to the template

# View Task Route
@app.route('/task/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)  # Fetch task by ID
    return render_template('view_task.html', task=task)  # Pass task to the template

# Tips Route
@app.route('/tips')
def tips():
    return render_template('tips.html')

# Export Pets to JSON
@app.route('/export_pets_to_json')
def export_pets_to_json():
    pets = Pet.query.all()
    pets_data = [{'id': pet.id, 'name': pet.name, 'type': pet.type, 'age': pet.age, 'owner_id': pet.owner_id} for pet in pets]
    return jsonify(pets_data)

# Generate Pet Report Route
@app.route('/generate_pet_report')
@login_required
def generate_pet_report():
    pets = Pet.query.filter_by(owner_id=current_user.id).all()

    report_data = [{'name': pet.name, 'type': pet.type, 'age': pet.age} for pet in pets]

    return render_template('pet_report.html', report_data=report_data)
# Delete Pet Route
@app.route('/delete_pet/<int:pet_id>', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.owner_id == current_user.id:  # Ensure the user can only delete their own pets
        db.session.delete(pet)
        db.session.commit()
        flash("Pet deleted successfully!", "success")
    else:
        flash("You do not have permission to delete this pet.", "danger")
    return redirect(url_for('index'))  # Redirect back to the home page


# Send SMS Reminders Route
@app.route('/send_sms_reminders')
def send_sms_reminders():
    return "Reminders Sent!"
# Add or View Insurance Route
@app.route('/insurance/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def insurance(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = InsuranceForm()

    # Check if the pet already has insurance
    insurance = pet.insurance

    if form.validate_on_submit():
        renewal_date_str = form.renewal_date.data
        try:
            renewal_date = datetime.strptime(renewal_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('insurance', pet_id=pet_id))

        # If no insurance exists, create new insurance record
        if not insurance:
            insurance = Insurance(policy_number=form.policy_number.data,
                                  provider=form.provider.data,
                                  renewal_date=renewal_date,
                                  claims=form.claims.data,
                                  payments=form.payments.data,
                                  pet_id=pet.id)
            db.session.add(insurance)
            db.session.commit()
            flash("Insurance details added successfully!", "success")
        else:
            # If insurance exists, update the existing record
            insurance.policy_number = form.policy_number.data
            insurance.provider = form.provider.data
            insurance.renewal_date = renewal_date
            insurance.claims = form.claims.data
            insurance.payments = form.payments.data
            db.session.commit()
            flash("Insurance details updated successfully!", "success")

        return redirect(url_for('insurance', pet_id=pet_id))  # Redirect back to the insurance page

    return render_template('insurance.html', form=form, pet=pet, insurance=insurance)
@app.route('/add_vaccination/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def add_vaccination(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = VaccinationForm()

    if form.validate_on_submit():
        date_administered_str = form.date_administered.data
        next_due_date_str = form.next_due_date.data

        try:
            date_administered = datetime.strptime(date_administered_str, "%Y-%m-%d").date()
            next_due_date = datetime.strptime(next_due_date_str, "%Y-%m-%d").date() if next_due_date_str else None
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('add_vaccination', pet_id=pet_id))

        new_vaccination = Vaccination(vaccine_name=form.vaccine_name.data,
                                      date_administered=date_administered,
                                      next_due_date=next_due_date,
                                      vet_clinic=form.vet_clinic.data,
                                      pet_id=pet.id)
        db.session.add(new_vaccination)
        db.session.commit()
        flash("Vaccination details added successfully!", "success")
        return redirect(url_for('index'))  # Redirect to the index page after adding vaccination

    return render_template('add_vaccination.html', form=form, pet=pet)
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Optional: Only allow deleting tasks of pets owned by the current user
    if task.pet.owner_id != current_user.id:
        flash("Unauthorized to delete this task.", "danger")
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully!", "success")
    return redirect(url_for('upcoming_tasks'))



# Run Application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)