from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create an SQLite database engine
engine = create_engine('sqlite:///my_database.db', echo=True)

# Create a base class for our database models
Base = declarative_base()

# Define a database model for the User
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    county = Column(String(20))
    town = Column(String(20))
    contact_number = Column(String)
    level_of_education = Column(String(100), nullable=True)  
    profession = Column(String(100), nullable=True)         
    marital_status = Column(String(20), nullable=True)       
    religion = Column(String(50), nullable=True)             
    ethnicity = Column(String(50), nullable=True) 
    self_description = Column(String(100), nullable=True)
     
      
    # Define the relationship with the Message model
    messages_sent = relationship("Message", foreign_keys='Message.from_user_id', backref='from_user', lazy=True)
    messages_received = relationship("Message", foreign_keys='Message.to_user_id', backref='to_user', lazy=True)

# Define a database model for the Message
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id')) 
    to_user_id = Column(Integer, ForeignKey('users.id'))
    body = Column(String(500))


Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)


session = Session()
