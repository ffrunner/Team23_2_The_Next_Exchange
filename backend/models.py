from config import db
import DateTime
from werkzeug.security import generate_password_hash, check_password_hash

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_json(self):
        return{
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
        }


#Class based off of users table in db
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50),nullable = False )
    password_hash = db.Column(db.String(150),nullable = False)
    role = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    date_created = db.Column(db.DateTime, nullable = False)
    last_login = db.Column(db.DateTime)

    #Function that sets password and will hash it
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #Function that checks input password to password in db
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# Model for Activity Logs
class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Model for Listings
class Listings(db.Model):
    __tablename__ = "listings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    claimed_by = db.Column(db.Integer, db.ForeignKey('users.id'))

#Model for claims
class Claims(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    lister_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the users table
    claimer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the users table
    pickup_details = db.Column(db.Text)  # Details about the pickup
    claim_status = db.Column(db.String(50), default='pending', nullable=False)  # Default status set to 'pending'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Log creation time

# Model for Disputes
class Dispute(db.Model):
    __tablename__ = "disputes"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)  # Linking to listings
    lister_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Linking to users
    claimer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Pending, resolved, etc.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)  # Nullable for unresolved disputes

# Model for Items
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    is_claimed = db.Column(db.Boolean, default=False)  # Default to False
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    title = db.Column(db.String, nullable=False)  # Title cannot be null
    description = db.Column(db.Text, nullable=True)  # Description can be null
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # Foreign key
    is_active = db.Column(db.Boolean, default=True)  # Default active
    lister_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key
    claimer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Foreign key for claimer, can be null

class ListingPhoto(db.Model):
    __tablename__ = 'listing_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)  # Assuming item_id refers to items
    photo_url = db.Column(db.Text, nullable=False)  # Ensure that a URL is always provided

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key reference to users
    message = db.Column(db.Text, nullable=False)  # Ensure that a message is always provided
    is_read = db.Column(db.Boolean, default=False)  # Default to False, indicating unread
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Timestamp for when created

# Model for Reports
class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    generated_at = db.Column(db.DateTime, server_default=db.func.now())
    report_data = db.Column(db.JSON)  # Store various analytics data


# Model for Categories
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

#Model for tags
class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Ensure that a name is always provided

