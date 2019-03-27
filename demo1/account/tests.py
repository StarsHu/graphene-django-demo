import json

from django.contrib.auth.models import User
from django.test import Client, TestCase


class TestUserSchema(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test1', password='qwe123', email='aaa@example.com')

    def setUp(self):
        print("\n%s" % self._testMethodName)
        self.c = Client()

    def test_query_me(self):
        import base64

        _id = base64.b64encode(f'User:{self.user.id}'.encode('utf-8')).decode()

        query = f'''
        query {{
            me {{
                id
                username
            }}
        }}
        '''

        response1 = self.c.post('/graphql/', data=json.dumps({'query': query}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        result1 = response1.json()

        self.assertIsNone(result1.get('errors'))

        data1 = result1.get('data', {}).get('me')
        self.assertIsNone(data1)

        self.c.login(username='test1', password='qwe123')
        response2 = self.c.post('/graphql/', data=json.dumps({'query': query}), content_type='application/json')
        self.assertEqual(response2.status_code, 200)
        result2 = response2.json()

        self.assertIsNone(result2.get('errors'))

        data2 = result2.get('data', {}).get('me', {})
        self.assertEqual(data2.get('id'), _id)
        self.assertEqual(data2.get('username'), self.user.username)

    def test_query_user(self):
        import base64

        _id = base64.b64encode(f'User:{self.user.id}'.encode('utf-8')).decode()

        query = f'''
        query {{
            user (id : "{_id}") {{
                id
                username
            }}
        }}
        '''

        response1 = self.c.post('/graphql/', data=json.dumps({'query': query}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        result1 = response1.json()

        self.assertIsNone(result1.get('errors'))

        data1 = result1.get('data', {}).get('user', {})
        self.assertEqual(data1.get('id'), _id)
        self.assertEqual(data1.get('username'), self.user.username)

    def test_query_users_1(self):
        User.objects.create_user(username='test2', password='qwe123', email='bbb@example.com', is_active=False)

        import base64

        _id = base64.b64encode(f'User:{self.user.id}'.encode('utf-8')).decode()

        # 1
        query1 = f'''
        query {{
            users {{
                id
                username
            }}
        }}
        '''

        response1 = self.c.post('/graphql/', data=json.dumps({'query': query1}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        result1 = response1.json()

        self.assertIsNone(result1.get('errors'))

        data1 = result1.get('data', {}).get('users', [])
        self.assertEqual(len(data1), 2)

    def test_query_users_2(self):
        User.objects.create_user(username='test2', password='qwe123', email='bbb@example.com', is_active=False)

        import base64

        _id = base64.b64encode(f'User:{self.user.id}'.encode('utf-8')).decode()

        # 1
        query1 = f'''
        query {{
            users (isActive: true){{
                id
                username
            }}
        }}
        '''

        response1 = self.c.post('/graphql/', data=json.dumps({'query': query1}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        result1 = response1.json()

        self.assertIsNone(result1.get('errors'))

        data1 = result1.get('data', {}).get('users', [])
        self.assertEqual(len(data1), 1)
        _data1 = data1[0]
        self.assertEqual(_data1.get('id'), _id)
        self.assertEqual(_data1.get('username'), self.user.username)

        # 2
        query2 = f'''
        query {{
            users (username : "{self.user.username}") {{
                id
                username
            }}
        }}
        '''

        response2 = self.c.post('/graphql/', data=json.dumps({'query': query2}), content_type='application/json')
        self.assertEqual(response2.status_code, 200)
        result2 = response2.json()

        self.assertIsNone(result2.get('errors'))

        data2 = result2.get('data', {}).get('users', [])
        self.assertEqual(len(data2), 1)
        _data2 = data2[0]
        self.assertEqual(_data2.get('id'), _id)
        self.assertEqual(_data2.get('username'), self.user.username)

    def test_mutate_create(self):
        query = '''
        mutation {
            createUser(username: "FF", password: "qwe123", email: "testuser2@example.com") {
                ok
            }
        }
        '''
        response1 = self.c.post('/graphql/', data=json.dumps({'query': query}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        created_user = User.objects.filter(username='FF').first()
        self.assertTrue(created_user)
        self.assertEqual(created_user.email, "testuser2@example.com")
        self.assertTrue(created_user.is_active)
        self.assertFalse(created_user.is_staff)

        self.assertTrue(created_user.check_password("qwe123"))

    def test_mutate_update(self):
        import base64
        _id = base64.b64encode(f'User:{self.user.id}'.encode('utf-8')).decode()

        query = f'''
        mutation {{
            updateUser(id: "{_id}" username: "EE" password: "qaz123" email: "newuser@example.com" isActive: false) {{
                ok
            }}
        }}
        '''
        response1 = self.c.post('/graphql/', data=json.dumps({'query': query}), content_type='application/json')
        self.assertEqual(response1.status_code, 200)

        updated_user = User.objects.filter(id=self.user.id).first()
        self.assertTrue(updated_user)
        self.assertEqual(updated_user.username, "EE")
        self.assertEqual(updated_user.email, "newuser@example.com")
        self.assertFalse(updated_user.is_active)

        self.assertTrue(updated_user.check_password("qaz123"))
