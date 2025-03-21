import unittest
from config import app, db

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/mydatabase'
        self.client = self.app.test_client()

        # Create the database and test user
        with self.app.app_context():
            db.create_all()  # Create all tables
            new_user = User(username='testuser', email='testuser@example.com')
            new_user.set_password('password123')
            db.session.add(new_user)
            db.session.commit()

    def test_login(self):
        response = self.client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Drop all tables after tests

if __name__ == '__main__':
    unittest.main()
