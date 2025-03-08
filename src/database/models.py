from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy import func
Base = declarative_base()

# Email Table
class Email(Base):
    __tablename__ = 'emails'

    '''
    Structure of table :
    ID - STRING PRIMARY KEY
    SUBJECT - STRING
    SNIPPET - STRING
    SENDER - STRING
    RECIPIENT - STRING
    DATE - STRING
    BODY - STRING
    HAS_ATTACHMENT - BOOLEAN DEFAULT FALSE
    IS_READ - BOOLEAN DEFAULT FALSE
    FOLDER_NAME - STRING DEFAULT 'INBOX'
    CREATED_AT - DATETIME DEFAULT CURRENT_TIME
    ATTACHMENTS - ATTACHMENT FOREIGN KEY REFERENCES ATTACHMENTS(ID)
    '''

    id = Column(String, primary_key=True)
    subject = Column(String) # subject of the email
    snippet = Column(String) # small summary of the email
    sender = Column(String) # sender of the email
    recipient = Column(String) # recipient of the email
    date = Column(String) # date of the email
    body = Column(String) # body of the email in text
    has_attachment = Column(Boolean, default=False) # boolean value to check if the email has an attachment
    is_read = Column(Boolean, default=False)  # Track read/unread status
    folder_name = Column(String, default='INBOX')  # Track current folder/label
    created_at = Column(DateTime, default=datetime.utcnow)
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")

# Attachement Table
class Attachment(Base):
    __tablename__ = 'attachments'
    '''
    Structure of table :
    ID - INTEGER PRIMARY KEY
    EMAIL_ID - INTEGER FOREIGN KEY REFERENCES EMAILS(ID)
    MIME_TYPE - STRING
    EMAIL - EMAIL FOREIGN KEY REFERENCES EMAILS(EMAIL)
    '''
    id = Column(Integer, primary_key=True)
    email_id = Column(String, ForeignKey('emails.id'))
    mime_type = Column(String) # type of attachement ('application/pdf', 'image/jpeg',...)
    email = relationship("Email", back_populates="attachments")

# Database handler class
class EmailDatabase:
    def __init__(self):
        self.engine = create_engine('sqlite:///src/database/emails.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    def store_email(self, email_data):
        try:
            # try to store the email data
            email = Email(
                id=email_data['id'],
                subject=email_data['subject'],
                snippet=email_data['snippet'],
                sender=email_data['from'],
                recipient=email_data['to'],
                date=email_data['date'],
                body=email_data['body'],
                has_attachment=email_data['has_attachment'],
                is_read=email_data.get('is_read', False),  
                folder_name=email_data.get('folder_name', 'INBOX')  # Get folder name from email_data
            )

            if email_data['has_attachment']:
                for mime_type in email_data['attachment_types']:
                    attachment = Attachment(mime_type=mime_type)
                    email.attachments.append(attachment)

            self.session.merge(email)
            self.session.commit()
            return True

        except Exception as e:
            # roll back
            print(f"Error storing email: {e}") 
            self.session.rollback()
            return False
    def get_all_emails(self):
        # return all emails in descending order by date
        return self.session.query(Email).order_by(Email.date.desc()).all()
    def close(self):
        self.session.close()
    def update_email_status(self, email_id, is_read=None, folder_name=None):
        try:
            email = self.session.query(Email).filter(Email.id == email_id).first()
            if email:
                if is_read is not None:
                    email.is_read = is_read
                if folder_name is not None:
                    email.folder_name = folder_name
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating email status: {e}")
            self.session.rollback()
            return False
    
    def get_attachment_stats(self):
        try:
            # Query to count attachments by mime type
            stats = self.session.query(
                Attachment.mime_type,
                func.count(Attachment.id).label('count')
            ).group_by(Attachment.mime_type).all()
            return stats
        except Exception as e:
            print(f"Error getting attachment stats: {e}")
            return []
    def get_folder_stats(self, count=None):
        try:
            if count:
                # Get limited number of emails and their folders
                emails = self.session.query(Email).order_by(Email.date.desc()).limit(count).all()
                folder_counts = {}
                for email in emails:
                    folder_counts[email.folder_name] = folder_counts.get(email.folder_name, 0) + 1
                stats = [(folder, count) for folder, count in folder_counts.items()]
            else:
                # Original functionality for all emails
                stats = self.session.query(
                    Email.folder_name,
                    func.count(Email.id).label('count')
                ).group_by(Email.folder_name).all()
            return stats
        except Exception as e:
            print(f"Error getting folder stats: {e}")
            return []
    def get_email_timing(self):
        try:
            # Query to get all email dates
            return self.session.query(Email.date).all()
        except Exception as e:
            print(f"Error getting email timing: {e}")
            return []