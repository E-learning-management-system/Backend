from django.test import Client, TestCase
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'piazza.settings')
import django

django.setup()

import pytest
import json
from .models import *


class TestBase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def tearDown(self) -> None:
        pass


class TestCourses(TestBase):
    def test_zero_returns_nothing(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.get('/soren/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('results'), [])

    def test_view_teaching_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get('/soren/courses/')
        response_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get('title'), 'Course 1')
        self.assertEqual(response_content.get('description'), 'Nothing')

    def test_view_course_as_student(self):
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        self.client.login(email='b@gmail.com', password='abcd')
        response = self.client.get('/soren/courses/')
        response_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content.get('title'), 'Course 1')

    def test_new_course_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        user = User.objects.get(email='amir@gmail.com')
        response = self.client.post(path='/soren/newcourse/', data={'title': 'Course 1', 'description': 'Nothing',
                                                                    'teacher': user, 'start_date': '2020-05-05',
                                                                    'exam_date': '2020-05-05T05:13:10',
                                                                    'end_date': '2020-05-07'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Course 1')
        Course.objects.get(title='Course 1').delete()

    def test_new_course_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        user = User.objects.get(email='b@gmail.com')
        response = self.client.post(path='/soren/newcourse/', data={'title': 'Course 1', 'description': 'Nothing',
                                                                    'teacher': user, 'start_date': '2020-05-05',
                                                                    'exam_date': '2020-05-05T05:13:10',
                                                                    'end_date': '2020-05-07'})
        self.assertEqual(response.status_code, 403)


class TestCourseStudents(TestBase):
    def test_add_student(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/b@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        response_2 = self.client.get(f'/soren/courses/{course.id}/students/')
        self.assertEqual(json.loads(response_2.content).get('results')[0].get('email'), 'b@gmail.com')

