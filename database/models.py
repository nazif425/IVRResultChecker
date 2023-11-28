from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

# mysql+pymysql
flask_bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def setup_db(app):
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0000@localhost:5432/ivr_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = 'e12a9887c55f8cfc791adbc41ada6ced'
    jwt.init_app(app)
    db.app = app
    db.init_app(app)
    flask_bcrypt.init_app(app)
    migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    schools = db.relationship('School', back_populates='user', cascade='all, delete-orphan')
    
    def __init__(self, username, email, first_name, last_name, password):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = flask_bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        result = flask_bcrypt.check_password_hash(self.password, password)
        if result:
            return result
        elif self.password == password:
            return True
        else:
            return False
    
    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

class CallSession(db.Model):
    __tablename__ = "call_session"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), nullable=False)
    validated = db.Column(db.Boolean, nullable=True, default=False)
    student_number = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    student_id = db.Column(db.Integer)
    session_list = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f'<session id: {self.id}>'
    
class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    api_link = db.Column(db.String(200))
    address = db.Column(db.String(200))
    contact = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    user = db.relationship('User', back_populates='schools')
    students = db.relationship('Student', back_populates='school', cascade='all, delete-orphan')
    courses = db.relationship('Course', back_populates='school', cascade='all, delete-orphan')
    def __repr__(self):
        return f'<school name: {self.school_name}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    matric = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    link_code = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    school = db.relationship('School', back_populates='students')
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    gpas = db.relationship('Gpa', back_populates='student', cascade='all, delete-orphan')
    def __repr__(self):
        return f'<student: {self.first_name} {self.last_name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    instructor = db.Column(db.String(50))
    description = db.Column(db.String(200))
    credits = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    school = db.relationship('School', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<course: {self.code}>'

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    session = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    db.CheckConstraint(status.in_(['Enrolled', 'Dropped', 'Carryover']))
    
    def __repr__(self):
        return f'<enrollment status: {self.status}>'

class Gpa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    session = db.Column(db.Integer)
    semester = db.Column(db.String(20))
    gpa = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    student = db.relationship('Student', back_populates='gpas')
    
    def __repr__(self):
        return f'<GPA: {self.gpa}>'