"""empty message

Revision ID: c10faf76f068
Revises: 6bb345b6db2e
Create Date: 2023-11-25 16:34:23.704723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c10faf76f068'
down_revision = '6bb345b6db2e'
branch_labels = None
depends_on = None


def upgrade():
    # Rename 'school' column in 'course' table
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.alter_column('school', new_column_name='school_id')

    # Rename 'student' and 'course' columns in 'enrollment' table
    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.alter_column('student', new_column_name='student_id')
        batch_op.alter_column('course', new_column_name='course_id')

    # Rename 'student' column in 'gpa' table
    with op.batch_alter_table('gpa', schema=None) as batch_op:
        batch_op.alter_column('student', new_column_name='student_id')

    # Rename 'user' column in 'school' table
    with op.batch_alter_table('school', schema=None) as batch_op:
        batch_op.alter_column('user', new_column_name='user_id')

    # Rename 'school' column in 'student' table
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('school', new_column_name='school_id')


def downgrade():
    # Reverse the column renaming in the downgrade script

    # Rename 'school_id' column back to 'school' in 'course' table
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.alter_column('school_id', new_column_name='school')

    # Rename 'student_id' and 'course_id' columns back to 'student' and 'course' in 'enrollment' table
    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.alter_column('student_id', new_column_name='student')
        batch_op.alter_column('course_id', new_column_name='course')

    # Rename 'student_id' column back to 'student' in 'gpa' table
    with op.batch_alter_table('gpa', schema=None) as batch_op:
        batch_op.alter_column('student_id', new_column_name='student')

    # Rename 'user_id' column back to 'user' in 'school' table
    with op.batch_alter_table('school', schema=None) as batch_op:
        batch_op.alter_column('user_id', new_column_name='user')

    # Rename 'school_id' column back to 'school' in 'student' table
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('school_id', new_column_name='school')

    # ### end Alembic commands ###
