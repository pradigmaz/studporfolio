# генерация аккаунта

def create_admin_student_account():
    from models import Students
    from database import db
    if db.session.query(Students).first() is None:
        if not Students.query.filter_by(username='StudentAdmin').first():
            admin_student = Students(
                surname='Студентов',
                first_name='Студент',
                middle_name='Студентович',
                username='StudentAdmin',
                phone_number='+79001234567',
                email='studentadmin@example.com',
                about='Студент администратор'
            )
            admin_student.set_password('StudAdminPass_321')
            db.session.add(admin_student)
            db.session.commit()

def create_admin_employer_account():
    from models import Employers
    from database import db
    if db.session.query(Employers).first() is None:
        if not Employers.query.filter_by(email='employeradmin@example.com').first():
            admin_employer = Employers(
                company_name='AdminCorp',
                contact_name='Employer Admin',
                email='employeradmin@example.com',
                phone_number='+79007654321'
            )
            admin_employer.set_password('EmpAdminPass123_')
            db.session.add(admin_employer)
            db.session.commit()
