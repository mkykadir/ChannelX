import app
import unittest

class ChannelxUserClassTestCase(unittest.TestCase):
    def setUp(self):
        self.user = app.User('username', 'email@mail.com', '5554443322', 'User Name', '1234')

    def test_setter_getter(self):
        self.assertEqual('username', self.user.username)

    def test_salt_creator(self):
        self.assertIsNotNone(self.user.salt)

    def test_hasher(self):
        hash_result = self.user.createHash(self.user.salt, '1234')
        self.assertEqual(self.user.hashed, hash_result)

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

class ChannelxCreateChannelTestCase(unittest.TestCase):
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
        self.app.get('/verify?username=testuser2', follow_redirects=True)

    def create_channel(self, description):
        return self.app.post('/channelc', data=dict(
            inputCreateDescription=description
        ), follow_redirects=True)

    def test_channel_create_user_logged_in(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)

        rv = self.create_channel('deneme')
        self.assertIn(b'onClick="get_channel_info(this.id)"', rv.data)

    def test_channel_create_user_not_logged_in(self):
        rv = self.create_channel('deneme')
        self.assertIn(b'You should be logged in!', rv.data)

class ChannelxChannelInformationTestCase(unittest.TestCase):
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
        self.app.get('/verify?username=testuser2', follow_redirects=True)
        channel = app.Channel('test-channel', 'testuser2', 'deneme')
        self.db.session.add(channel)
        self.db.session.commit()

    def test_get_channel_info_existing(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/_channeli?chname=test-channel')
        self.assertIn(b'test-channel', rv.data)

    def test_get_channel_info_nonexisting(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/_channeli?chname=no-channel', follow_redirects=True)
        self.assertIn(b'Panel', rv.data)

class ChannelxChannelDeleteTestCase(unittest.TestCase):
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
        self.app.get('/verify?username=testuser2', follow_redirects=True)
        channel = app.Channel('test-channel', 'testuser2', 'deneme')
        self.db.session.add(channel)
        self.db.session.commit()

    def test_delete_channel_existing(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/_channeld?chname=test-channel')
        self.assertIn(b'200', rv.data)

    def test_delete_channel_nonexisting(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/_channeld?chname=no-channel')
        self.assertIn(b'404', rv.data)

class ChannelxChannelEntryTestCase(unittest.TestCase):
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
            username='testuser3',
            name='Test User3',
            email='testuser3@mail.com',
            phone='5554443310',
            password='1234',
            confirm='1234',
            accept_terms='y'
        ), follow_redirects=True)
        self.app.post('/signup', data=dict(
            username='testuser4',
            name='Test User4',
            email='testuser4@mail.com',
            phone='5554443320',
            password='1234',
            confirm='1234',
            accept_terms='y'
        ), follow_redirects=True)
        self.app.get('/verify?username=testuser2', follow_redirects=True)
        self.app.get('/verify?username=testuser3', follow_redirects=True)
        self.app.get('/verify?username=testuser4', follow_redirects=True)
        channel = app.Channel('test-channel', 'testuser2', 'deneme')
        self.db.session.add(channel)
        channel_passw = app.Channel('test-channel-pass', 'testuser2', 'deneme')
        channel_passw.setPassword('1234')
        self.db.session.add(channel_passw)
        self.db.session.commit()

    def test_channel_not_exists(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/channel/no-channel', follow_redirects=True)
        self.assertIn(b'Panel', rv.data)

    def test_nonmember_registered_user(self):
        self.app.post('/login', data=dict(inputUsername='testuser4',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/channel/test-channel', follow_redirects=True)
        self.assertIn(b'nopassform', rv.data)

    def test_member_registered_user(self):
        self.app.post('/login', data=dict(inputUsername='testuser3',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/channel/test-channel', follow_redirects=True)
        self.assertIn(b'nopassform', rv.data)

    def test_channel_creator(self):
        self.app.post('/login', data=dict(inputUsername='testuser2',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/channel/test-channel', follow_redirects=True)
        self.assertIn(b'<thead>', rv.data)

    def test_nonmember_pass_required_channel(self):
        self.app.post('/login', data=dict(inputUsername='testuser4',
                            inputPassword='1234'), follow_redirects=True)
        rv = self.app.get('/channel/test-channel-pass', follow_redirects=True)
        self.assertIn(b'loginform', rv.data)

if __name__ == '__main__':
    unittest.main()
