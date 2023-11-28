import sys, os, random, base64, hashlib, secrets, random, string, requests
import json
from os import environ
from flask import Flask, request, jsonify, abort, render_template, Response, flash, redirect, url_for, session
from database.models import db, User, School, Student, Course, Enrollment, Gpa
from datetime import date, datetime
from database.serializers import SchoolSchema, StudentSchema, CourseSchema, EnrollmentSchema, GpaSchema
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

school_schema = SchoolSchema()
student_schema = StudentSchema()
course_schema = CourseSchema()
enrollment_schema = EnrollmentSchema()
enrollments_schema = EnrollmentSchema(many=True)
gpa_schema = GpaSchema()
QUESTIONS_PER_PAGE = 10

def get_page_item_offset(request):
    page_number = request.args.get('page', 1, type=int)
    item_start_index = (page_number - 1) * QUESTIONS_PER_PAGE
    return item_start_index

def api_urls(app, ses_data):
    @app.route('/', methods=['GET'])
    def index():
        return render_template('home/index.html')
    
    @app.route('/account/login', methods=['GET'])
    def login_page():
        return render_template('account/login.html')

    @app.route('/account/login', methods=['POST'])
    def process_login():
        print(request.json)
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        user = User.query.filter_by(username=username).one_or_none()
        if not user or not user.check_password(password):
            return jsonify("Wrong username or password"), 401

        # Notice that we are passing in the actual sqlalchemy user object here
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token)

    
     # Endpoint for getting all Schools
    @app.route('/api/v1/schools', methods=['GET'])
    @jwt_required()
    def get_schools():
        return jsonify({
            'Result': 'OK',
            'Records': school_schema.dump(School.query.all(), many=True)
        }), 200

    # Endpoint for getting a specific School by ID
    @app.route('/api/v1/schools/<int:id>', methods=['GET'])
    @jwt_required()
    def get_school(id):
        school = School.query.filter(School.id==id).one_or_none()
        if school is None:
            return jsonify({
                'Result': 'OK',
                'Records': school_schema.dump(school)
            }), 200
        else:
            return jsonify({
                'Result': 'ERROR',
                'Message': 'Record not found'
            }), 404
    
    # Endpoint for creating a new Student
    @app.route('/api/v1/schools', methods=['POST'])
    @jwt_required()
    def create_school():
        try:
            data = request.json
            # Validate input data against the schema
            errors = school_schema.validate(data)
            if errors:
                return jsonify({'Result': 'ERROR', 'Message': errors}), 400

            data['user_id'] = current_user.id
            print(data)
            new_school = School(**data)
            db.session.add(new_school)
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': school_schema.dump(new_school)}), 201
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for updating an existing Student by ID
    @app.route('/api/v1/schools/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_schools(id):
        school = School.query.filter(School.id==id).one_or_none()
        data = request.json
        print(data)
        # Validate input data against the schema
        errors = school_schema.validate(data)
        if errors:
            return jsonify({'Result': 'ERROR', 'Message': errors}), 400

        for key, value in data.items():
            setattr(school, key, value)

        try:
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': school_schema.dump(school)}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for deleting a Student by ID
    @app.route('/api/v1/schools/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_school(id):
        school = School.query.filter(School.id==id).one_or_none()
        if school is None:
            return jsonify({'Result': 'ERROR', 'Message': 'record not found'}), 404
        else:
            db.session.delete(school)
            db.session.commit()
            return jsonify({'Result': 'OK'}), 200

    # Endpoint for deleting all Students
    """
     @app.route('/api/v1/schools', methods=['DELETE'])
    def delete_all_schools():
        schools = School.query.all()
        for school in schools:
            db.session.delete(school)
        db.session.commit()
        return jsonify({'message': 'All schools deleted successfully'})
    """

# fgfgj
     # Endpoint for getting all Schools
    @app.route('/api/v1/students', methods=['GET'])
    def get_students():
        return jsonify({
            'Result': 'OK',
            'Records': student_schema.dump(Student.query.all(), many=True)
        }), 200

    # Endpoint for getting a specific School by ID
    @app.route('/api/v1/students/<int:id>', methods=['GET'])
    def get_student(id):
        student = Student.query.filter(Student.id==id).one_or_none()
        if student is None:
            return jsonify({
                'Result': 'OK',
                'Records': student_schema.dump(student)
            }), 200
        else:
            return jsonify({
                'Result': 'ERROR',
                'Message': 'Record not found'
            }), 404
    
    # Endpoint for creating a new Student
    @app.route('/api/v1/students', methods=['POST'])
    def create_student():
        try:
            data = request.json

            # Validate input data against the schema
            errors = student_schema.validate(data)
            if errors:
                return jsonify({'Result': 'ERROR', 'Message': errors}), 400

            new_student = Student(**data)
            db.session.add(new_student)
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': student_schema.dump(new_student)}), 201
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for updating an existing Student by ID
    @app.route('/api/v1/students/<int:id>', methods=['PUT'])
    def update_student(id):
        student = Student.query.filter(Student.id==id).one_or_None()
        data = request.json

        # Validate input data against the schema
        errors = student_schema.validate(data)
        if errors:
            return jsonify({'Result': 'ERROR', 'Message': errors}), 400

        for key, value in data.items():
            setattr(student, key, value)

        try:
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': student_schema.dump(student)}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

        db.session.commit()

    # Endpoint for deleting a Student by ID
    @app.route('/api/v1/students/<int:id>', methods=['DELETE'])
    def delete_student(id):
        student = Student.query.filter(Student.id==id).one_or_none()
        if student is None:
            return jsonify({'Result': 'ERROR', 'Message': 'record not found'}), 404
        try:
            db.session.delete(student)
            db.session.commit()
            return jsonify({'Result': 'OK'}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 200

    """
        # Endpoint for deleting all Students
        @app.route('/api/v1/students', methods=['DELETE'])
        def delete_all_students():
            students = Student.query.all()
            for student in students:
                db.session.delete(student)
            db.session.commit()
            return jsonify({'message': 'All students deleted successfully'})
    """
        # Endpoint for getting all Courses
    @app.route('/api/v1/courses', methods=['GET'])
    def get_courses():
        return jsonify({
            'Result': 'OK',
            'Records': course_schema.dump(Course.query.all(), many=True)
        }), 200

    # Endpoint for getting a specific Course by ID
    @app.route('/api/v1/courses/<int:id>', methods=['GET'])
    def get_course(id):
        course = Course.query.filter_by(Course.id==id).one_or_none()
        if course is not None:
            return jsonify({
                'Result': 'OK',
                'Records': course_schema.dump(course)
            }), 200
        else:
            return jsonify({
                'Result': 'ERROR',
                'Message': 'Record not found'
            }), 404

    # Endpoint for creating a new Course
    @app.route('/api/v1/courses', methods=['POST'])
    def create_course():
        try:
            data = request.json

            # Validate input data against the schema
            errors = course_schema.validate(data)
            if errors:
                return jsonify({'Result': 'ERROR', 'Message': errors}), 400

            new_course = Course(**data)
            db.session.add(new_course)
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': course_schema.dump(new_course)}), 201
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for updating an existing Course by ID
    @app.route('/api/v1/courses/<int:id>', methods=['PUT'])
    def update_course(id):
        course = Course.query.filter_by(Course.id==id).one_or_none()
        data = request.json

        # Validate input data against the schema
        errors = course_schema.validate(data)
        if errors:
            return jsonify({'Result': 'ERROR', 'Message': errors}), 400

        for key, value in data.items():
            setattr(course, key, value)

        try:
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': course_schema.dump(course)}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for deleting a Course by ID
    @app.route('/api/v1/courses/<int:id>', methods=['DELETE'])
    def delete_course(id):
        course = Course.query.filter_by(Course.id==id).one_or_none()
        if course is None:
            return jsonify({'Result': 'ERROR', 'Message': 'Record not found'}), 404
        else:
            db.session.delete(course)
            db.session.commit()
            return jsonify({'Result': 'OK'}), 200

    # Endpoint for getting all Enrollments
    @app.route('/api/v1/enrollments', methods=['GET'])
    def get_enrollments():
        return jsonify({
            'Result': 'OK',
            'Records': enrollment_schema.dump(Enrollment.query.all(), many=True)
        }), 200

    # Endpoint for getting a specific Enrollment by ID
    @app.route('/api/v1/enrollments/<int:id>', methods=['GET'])
    def get_enrollment(id):
        enrollment = Enrollment.query.filter_by(Enrollment.id==id).one_or_none()
        if enrollment is not None:
            return jsonify({
                'Result': 'OK',
                'Records': enrollment_schema.dump(enrollment)
            }), 200
        else:
            return jsonify({
                'Result': 'ERROR',
                'Message': 'Record not found'
            }), 404

    # Endpoint for creating a new Enrollment
    @app.route('/api/v1/enrollments', methods=['POST'])
    def create_enrollment():
        try:
            data = request.json

            # Validate input data against the schema
            errors = enrollment_schema.validate(data)
            if errors:
                return jsonify({'Result': 'ERROR', 'Message': errors}), 400

            new_enrollment = Enrollment(**data)
            db.session.add(new_enrollment)
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': enrollment_schema.dump(new_enrollment)}), 201
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for updating an existing Enrollment by ID
    @app.route('/api/v1/enrollments/<int:id>', methods=['PUT'])
    def update_enrollment(id):
        enrollment = Enrollment.query.filter_by(Enrollment.id==id).one_or_none()
        data = request.json

        # Validate input data against the schema
        errors = enrollment_schema.validate(data)
        if errors:
            return jsonify({'Result': 'ERROR', 'Message': errors}), 400

        for key, value in data.items():
            setattr(enrollment, key, value)

        try:
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': enrollment_schema.dump(enrollment)}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for deleting an Enrollment by ID
    @app.route('/api/v1/enrollments/<int:id>', methods=['DELETE'])
    def delete_enrollment(id):
        enrollment = Enrollment.query.filter_by(Enrollment.id==id).one_or_none()
        if enrollment is None:
            return jsonify({'Result': 'ERROR', 'Message': 'Record not found'}), 404
        else:
            db.session.delete(enrollment)
            db.session.commit()
            return jsonify({'Result': 'OK'}), 200
    
     # Endpoint for getting all GPAs
    @app.route('/api/v1/gpas', methods=['GET'])
    def get_gpas():
        return jsonify({
            'Result': 'OK',
            'Records': gpa_schema.dump(Gpa.query.all(), many=True)
        }), 200

    # Endpoint for getting a specific GPA by ID
    @app.route('/api/v1/gpas/<int:id>', methods=['GET'])
    def get_gpa(id):
        gpa = Gpa.query.filter_by(Gpa.id==id).one_or_none()
        if gpa is not None:
            return jsonify({
                'Result': 'OK',
                'Records': gpa_schema.dump(gpa)
            }), 200
        else:
            return jsonify({
                'Result': 'ERROR',
                'Message': 'Record not found'
            }), 404

    # Endpoint for creating a new GPA
    @app.route('/api/v1/gpas', methods=['POST'])
    def create_gpa():
        try:
            data = request.json

            # Validate input data against the schema
            errors = gpa_schema.validate(data)
            if errors:
                return jsonify({'Result': 'ERROR', 'Message': errors}), 400

            new_gpa = Gpa(**data)
            db.session.add(new_gpa)
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': gpa_schema.dump(new_gpa)}), 201
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for updating an existing GPA by ID
    @app.route('/api/v1/gpas/<int:id>', methods=['PUT'])
    def update_gpa(id):
        gpa = Gpa.query.filter_by(Gpa.id==id).one_or_none()
        data = request.json

        # Validate input data against the schema
        errors = gpa_schema.validate(data)
        if errors:
            return jsonify({'Result': 'ERROR', 'Message': errors}), 400

        for key, value in data.items():
            setattr(gpa, key, value)

        try:
            db.session.commit()
            return jsonify({'Result': 'OK', 'Record': gpa_schema.dump(gpa)}), 200
        except Exception as e:
            return jsonify({'Result': 'ERROR', 'Message': str(e)}), 500

    # Endpoint for deleting a GPA by ID
    @app.route('/api/v1/gpas/<int:id>', methods=['DELETE'])
    def delete_gpa(id):
        gpa = Gpa.query.filter_by(Gpa.id==id).one_or_none()
        if gpa is None:
            return jsonify({'Result': 'ERROR', 'Message': 'Record not found'}), 404
        else:
            db.session.delete(gpa)
            db.session.commit()
            return jsonify({'Result': 'OK'}), 200
