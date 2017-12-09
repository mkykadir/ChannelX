import app
import unittest

class ChannelxSignupTestCase(unittest.TestCase):
    def setUp(self):
        self.db = app.db
        app.app.testing = True
        self.app = app.app.test_client()
        self.db.session.close()
        self.db.drop_all()
        self.db.create_all()

    def signup(self, username, name, email, phone, password):
        return self.app.post('/signup', data=dict(
            username=username,
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm=password,
            accept_terms='y'
        ), follow_redirects=True)

    def test_signup_fields_filled(self):
        rv = self.signup('testuser2', 'Test User2', 'testuser2@mail.com', '5551117788', '1234')
        self.assertIn(b'Thanks for registering', rv.data)

    def test_signup_fields_empty(self):
        rv = self.signup('', '', '', '', '')
        self.assertIn(b'field is required', rv.data)

class ChannelxVerifyTestCase(unittest.TestCase):
    def setUp(self):
        self.db = app.db
        app.app.testing = True
        self.app = app.app.test_client()
        self.db.session.close()
        self.db.drop_all()
        self.db.create_all()
        self.app.post('/signup', data=dict(
            username='testuser2',
            name='Test User2',
            email='testuser2@mail.com',
            phone='5554443322',
            password='1234',
            confirm='1234',
            accept_terms='y'
        ), follow_redirects=True)

    def verify(self, username):
        url_path = '/verify?username=' + username
        return self.app.get(url_path, follow_redirects=True)

    def test_verify_signedup_user(self):
        rv = self.verify('testuser2')
        self.assertIn(b'Your E-Mail verified', rv.data)

    def test_verify_nonsignedup_user(self):
        rv = self.verify('nonregistered')
        self.assertIn(b'Non-registered', rv.data)

class ChannelxLoginTestCase(unittest.TestCase):
    def setUp(self):
        self.db = app.db
        app.app.testing = True
        self.app = app.app.test_client()
        self.db.session.close()
        self.db.drop_all()
        self.db.create_all()
        self.app.post('/signup', data=dict(
            username='testuser2',
            name='Test User2',
            email='testuser2@mail.com',
            phone='5554443322',
            password='1234',
            confirm='1234',
            accept_terms='y'
        ), follow_redirects=True)
        self.app.post('/signup', data=dict(
            username='notverified',
            name='Not Verified',
            email='notverified@mail.com',
            phone='5554443311',
            password='1234',
            confirm='1234',
            accept_terms='y'
        ), follow_redirects=True)
        self.app.get('/verify?username=testuser2', follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(inputUsername=username,
                            inputPassword=password), follow_redirects=True)

    def test_login_signedup_verified(self):
        rv = self.login('testuser2', '1234')
        self.assertIn(b'Panel', rv.data)

    def test_login_signedup_notverified(self):
        rv = self.login('notverified', '1234')
        self.assertIn(b'non-verified', rv.data)

    def test_login_nonsignedup(self):
        rv = self.login('notrefistered', '1234')
        self.assertIn(b'Wrong credentials', rv.data)

if __name__ == '__main__':
    unittest.main()
