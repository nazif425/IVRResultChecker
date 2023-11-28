from flask_marshmallow import Marshmallow
from database.models import db, School, Student, Course, Enrollment, Gpa


ma = Marshmallow()
def setup_serializers(app):
    ma.init_app(app)


# Marshmallow Schema
class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("email", "date_created", "_links")

    # Smart hyperlinking
    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("user_detail", values=dict(id="<id>")),
            "collection": ma.URLFor("users"),
        }
    )

class SchoolSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = School
        load_instance = True

class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True

class CourseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        load_instance = True

class EnrollmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Enrollment
        load_instance = True

class GpaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gpa
        load_instance = True