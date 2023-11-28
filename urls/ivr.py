import sys, os, random, base64, hashlib, secrets, random, string, requests
import json
from os import environ
from flask import Flask, request, jsonify, abort, render_template, Response, flash, redirect, url_for, session
from database.models import setup_db, db, CallSession, School, Student, Course, Enrollment, Gpa
from datetime import date, datetime


def ivr_urls(app, ses_data):
	@app.before_request
	def before_request_func():
		# Perform tasks before each request handling
		if request.values.get('isActive', None) == 0:
			clear_session_data()
			abort(200, "Session ended")
		sessionId = request.values.get('sessionId', None)
		if sessionId:
			session = CallSession.query.filter(CallSession.session_id==sessionId).first()
			if session:
				ses_data["validated"] = session.validated
				ses_data["session_id"] = session.session_id
				ses_data["student_number"] = session.student_number
				ses_data["first_name"] = session.first_name
				ses_data["last_name"] = session.last_name
				ses_data["student_id"] = session.student_id
				ses_data["data"] = session.data
			else:
				data = {
					"validated" : ses_data["validated"],
					"session_id" : request.values.get('sessionId', None),
					"student_number" : request.values.get('callerNumber', None),
				}
				ses_data.update(data)
				db.session.add(CallSession(**data))
				db.session.commit()

	@app.after_request
	def after_request_func(response):
		# Perform tasks after each request handling
		sessionId = request.values.get('sessionId', None)
		if sessionId:
			session = CallSession.query.filter(CallSession.session_id==sessionId).first()
			if session:
				session.validated = ses_data["validated"]
				session.session_id = ses_data["session_id"]
				session.student_number = ses_data["student_number"]
				session.first_name = ses_data["first_name"]
				session.last_name = ses_data["last_name"]
				session.student_id = ses_data["student_id"]
				session.data = ses_data["data"]
				db.session.commit()
		return response

	def verify_caller_id(id=None):
		if not ses_data["validated"]:
			student = Student.query.filter(
				Student.phone_number==request.values.get('callerNumber', None) | Student.link_code==id
			).first()
			if student:
				ses_data["student_id"] = student.id
				ses_data["first_name"] = student.first_name
				ses_data["last_name"] = student.last_name
				ses_data["validated"] = True
		return ses_data["validated"]

	def clear_session_data():
		ses_data["validated"] = False
		ses_data["session_id"] = ""
		ses_data["student_number"] = ""
		ses_data["first_name"] = ""
		ses_data["last_name"] = ""
		ses_data["student_id"] = ""
		ses_data["data"] = {}
		sessionId = request.values.get('sessionId', None)
		if sessionId:
			CallSession.query
			session = CallSession.query.filter(CallSession.session_id==sessionId).first()
			if session:
				db.session.delete(session)
				db.session.commit()

	def get_session(student_id):
		session_menu = ""
		enrollments = Enrollment.query.filter(Student.id==student_id)
		query = db.query(enrollments.session.distinct().label("session"))
		
		for n, row in enumerate(query.all()):
			ses_data["data"]["session_list"][n+1] = row.session
			session_menu = session_menu + "<Say>for {} session, Press {} </Say>\n".format(row.session, n+1) 
		return session_menu

	def get_semester(student_id, session):
		semester_menu = ""
		enrollments = Enrollment.query.filter(Student.id==student_id, session==session)
		query = db.query(enrollments.semester.distinct().label("semester"))
		
		for n, row in enumerate(query.all()):
			ses_data["data"]["semester_list"][n+1] = row.semester
			semester_menu = semester_menu + "<Say>for {} semester, Press {} </Say>\n".format(row.semester, n+1)
		return semester_menu

	def get_result(result_option):
		result_list = ''
		if int(result_option) == 1:
			with open('standard_responses/show_result.xml') as f:
				response = f.read()
			student = ses_data["student_id"]
			semester = ses_data["data"]["selected"]["semester"]
			session = ses_data["data"]["selected"]["session"]
			if semester and session and student:
				enrollments = Enrollment.query.filter(semester=semester, session=session, student=student, status='Enrolled')
				for record in enrollments:
					result_list = result_list + "<Say>{}, {}</Say>\n".format(record.course_id.code, record.grade)
				gpa = Gpa.query.filter(semester=semester, session=session, student=student)
				result_list = result_list + "<Say>your GPA for the semester is {}</Say>\n".format(gpa.gpa)
				response = response.format(result_list=result_list)
				return response
			else:
				return '<Response><Reject/></Response>'
		else:
			return ''

	@app.route("/welcome_handler", methods=['POST','GET'])
	def welcome_handler():
		id = request.values.get("dtmfDigits", None)
		if verify_caller_id(id):
			with open('standard_responses/welcome_menu.xml') as f:
				response = f.read()
			session_menu = get_session(ses_data["student_id"])
			response = response.format(**ses_data)
			response = response.format(session_menu=session_menu)
			return response
		if not id:
			with open('standard_responses/authentication.xml') as f:
				response = f.read()
			return response
		else:
			with open('standard_responses/failed_authentication.xml') as f:
				response = f.read()
			return response

	@app.route("/session_handler", methods=['POST'])
	def session_handler():
		digits = request.values.get("dtmfDigits", None)
		print(digits)
		if digits == '0':
			return '<Response><Reject/></Response>'
		else:
			session_list = ses_data["data"].get("session_list", None)
			if session_list:
				session = session_list[digits]
				ses_data["data"]["selected"]["session"] = session
				with open('standard_responses/semester_handler.xml') as f:
					response = f.read()
				semester_menu = get_semester(ses_data["student_id"], session)
				response = response.format(semester_menu=semester_menu)
				return response
		return '<Response><Reject/></Response>'
	@app.route("/semester_handler", methods=['POST'])
	def semester_handler():
		digits = request.values.get("dtmfDigits", None)
		print(digits)
		if digits == '0':
			return '<Response><Reject/></Response>'
		else:
			semester_list = ses_data["data"].get("semester_list", None)
			if semester_list:
				semester = semester_list[digits]
				ses_data["data"]["selected"]["semester"] = semester
				with open('standard_responses/result_handler.xml') as f:
					response = f.read()
				return response
		return '<Response><Reject/></Response>'

	@app.route("/result_handler", methods=['POST'])
	def result_handler():
		digits = request.values.get("dtmfDigits", None)
		print(digits)
		if int(digits) <= 3:
			return get_result(digits)
		else: 
			return '<Response><Reject/></Response>'