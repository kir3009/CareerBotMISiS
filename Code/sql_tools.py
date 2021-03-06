from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_repr import RepresentableBase


class SQLDataBase:
    def __init__(self, db_path="./Data/database.sqlite"):
        self.engine = None
        self.session = None
        self.Base = declarative_base(cls=RepresentableBase)

        self.User = None
        self.Resume = None
        self.Testing = None

        self.init_db(db_path)
        self.init_session()
        self.init_classes()

    def init_db(self, db_path):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=True)
        self.engine.connect()

    def init_session(self):
        self.session = sessionmaker(self.engine)()

    def init_classes(self):

        class User(self.Base):
            __tablename__ = 'users'
            id = Column(String, primary_key=True, autoincrement=False)
            first_name = Column(String)
            second_name = Column(String)
            last_name = Column(String)

        class Resume(self.Base):
            __tablename__ = 'resumes'
            id = Column(Integer, primary_key=True)
            user_id = Column(String)
            birthday = Column(String)
            full_years = Column(String)
            phone = Column(String)
            email = Column(String)
            wanted_profession = Column(String)
            work_period = Column(String)
            company_name = Column(String)
            work_exp = Column(Integer)
            profession = Column(String)
            job_responsibilities = Column(String)
            finish_education = Column(String)
            university = Column(String)
            specialty = Column(String)
            qualification = Column(String)
            finish_education_ad = Column(String)
            university_ad = Column(String)
            qualification_ad = Column(String)
            personal_skills = Column(String)
            recommendations = Column(String)

        class Testing(self.Base):
            __tablename__ = 'testing'
            id = Column(Integer, primary_key=True)
            user_id = Column(String)
            first_name = Column(String)
            second_name = Column(String)
            last_name = Column(String)
            institute = Column(String)
            group = Column(String)
            email = Column(String)

        self.User = User
        self.Resume = Resume
        self.Testing = Testing

        self.Base.metadata.create_all(self.engine)

    def check_user(self, user_id):
        return self.session.query(self.User).filter_by(id=user_id).scalar() is not None

    def add_user(self, user):
        if self.check_user(user.id):
            self.session.query(self.User).filter_by(id=user.id).delete()
            self.session.commit()
        self.session.add(user)
        self.session.commit()

    def check_resume(self, user_id):
        return self.session.query(self.Resume).filter_by(user_id=user_id).scalar() is not None

    def add_resume(self, resume):
        if self.check_resume(resume.user_id):
            self.session.query(self.Resume).filter_by(user_id=resume.user_id).delete()
            self.session.commit()
        self.session.add(resume)
        self.session.commit()

    def get_user(self, user_id):
        return self.session.query(self.User).filter_by(id=user_id).first()

    def get_resume(self, user_id):
        return self.session.query(self.Resume).filter_by(user_id=user_id).first()

    def check_testing(self, user_id):
        return self.session.query(self.Testing).filter_by(id=user_id).scalar() is not None

    def add_testing(self, testing):
        if self.check_testing(testing.user_id):
            self.session.query(self.Testing).filter_by(user_id=testing.user_id).delete()
            self.session.commit()
        self.session.add(testing)
        self.session.commit()

    def get_testing(self, user_id):
        return self.session.query(self.Testing).filter_by(user_id=user_id).first()
