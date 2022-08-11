from django.core.validators import *
from django.test import Client, TestCase, SimpleTestCase
import os

from django.utils.crypto import get_random_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'piazza.settings')
import django

django.setup()

import pytest
import json
from .models import *
from django.urls import reverse, resolve


class TestBase(TestCase):
    def setUp(self) -> None:
        user_1 = User.objects.create_superuser(email='amir@gmail.com', password='abcd')
        user_1.type = 't'
        user_1.save()
        user_2 = User.objects.create_superuser(email='b@gmail.com', password='abcd')
        user_2.type = 's'
        user_2.name = 'Amir'
        user_2.save()
        user_3 = User.objects.create_superuser(email='a@gmail.com', password='abcd')
        user_3.type = 't'
        user_3.save()
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
                                                                    'start_date': '2020-05-05',
                                                                    'exam_date': '2020-05-05T05:13:10',
                                                                    'end_date': '2020-05-07'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Course 1')

    def test_new_course_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        user = User.objects.get(email='b@gmail.com')
        response = self.client.post(path='/soren/newcourse/', data={'title': 'Course 1', 'description': 'Nothing',
                                                                    'start_date': '2020-05-05',
                                                                    'exam_date': '2020-05-05T05:13:10',
                                                                    'end_date': '2020-05-07'})
        self.assertEqual(response.status_code, 403)

    def test_new_course_missing_parameter_title(self):
        user = User.objects.get(email='amir@gmail.com')
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.post(path='/soren/newcourse/',
                                    data={'description': 'Course 1', 'start_date': '2020-05-05',
                                          'exam_date': '2020-05-05T05:13:10',
                                          'end_date': '2020-05-07'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content.get('title'), ['این مقدار لازم است.'])

    def test_new_course_invalid_dates(self):
        user = User.objects.get(email='amir@gmail.com')
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.post(path='/soren/newcourse/',
                                    data={'title': 'Course 1', 'description': 'Course 1',
                                          'start_date': '2020-05-05',
                                          'exam_date': '2020-05-05T05:13:10',
                                          'end_date': '2020-05-04'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content.get('non_field_errors'), ['تاریخ پایان باید بعد از تاریخ آغاز باشد.'])

    def test_retrieve_course_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get(f'/soren/course-rud/{course.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('course_title'), 'Course 1')

    def test_retrieve_course_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get(f'/soren/course-rud/{course.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('course_title'), 'Course 1')
        self.assertEqual(r_content.get('description'), 'Nothing')

    def test_update_course_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.put(path=f'/soren/course-rud/{course.id}/',
                                   data={'description': 'descp', 'start_date': '2020-05-05', 'end_date': '2020-05-06',
                                         'exam_date': '2020-05-07'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_update_course_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.put(f'/soren/course-rud/{course.id}/',
                                   {
                                       "description": "put",
                                       "start_date": "2022-07-15",
                                       "end_date": "2022-07-15",
                                       "exam_date": "2022-07-15T16:03:10.215Z"
                                   })
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 415)

    def test_delete_course_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.delete(f'/soren/course-rud/{course.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_delete_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.delete(f'/soren/course-rud/{course.id}/')
        self.assertEqual(response.status_code, 204)


class TestCourseStudents(TestBase):
    def test_add_student_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/b@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        response_2 = self.client.get(f'/soren/courses/{course.id}/students/')
        self.assertEqual(json.loads(response_2.content).get('results')[0].get('email'), 'b@gmail.com')

    def test_add_student_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/b@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, {'detail': 'فقط اساتید به این عمل دسترسی دارند'})

    def test_add_teacher_as_student_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/amir@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'ایمیل وارد شده باید متعلق به یک دانشجو باشد')

    def test_add_student_in_another_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/b@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_add_student_that_is_already_there(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/b@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'این دانشجو قبلا اضافه شده است')

    def test_add_student_that_doesnt_exist(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newstudent/abc@gmail.com/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'کاربر موجود نیست. از طریق ایمیل به ایشان اطلاع داده خواهد شد')

    def test_delete_course_student_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        user = User.objects.get(email='b@gmail.com')
        course.student.add(user)
        response = self.client.get(f'/soren/student-rd/{CourseStudent.objects.get(user=user, course=course).id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)

    def test_delete_course_student(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        user = User.objects.get(email='b@gmail.com')
        course.student.add(user)
        response = self.client.delete(f'/soren/student-rd/{CourseStudent.objects.get(user=user, course=course).id}/')
        self.assertEqual(response.status_code, 204)


class TestSubjects(TestBase):
    def test_view_no_subjects(self):
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.get(f'/soren/courses/{course.id}/subjects/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('results'), [])

    def test_add_subject(self):
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.post(path=f'/soren/courses/{course.id}/newsubject/', data={'title': 'Subject 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Subject 1')

    def test_view_subjects(self):
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.get(f'/soren/courses/{course.id}/subjects/')
        r_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('id'), subject.id)
        self.assertEqual(r_content.get('title'), 'Subject 1')

    def test_add_subject_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newsubject/', data={'title': 'Subject 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, {'detail': 'فقط اساتید به این عمل دسترسی دارند'}
                         )

    def test_add_subject_to_invalid_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newsubject/', data={'title': 'Subject 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'}
                         )

    def test_view_subjects_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        Subject.objects.create(course=course, title='Sub 1')
        response = self.client.get(f'/soren/courses/{course.id}/subjects/')
        r_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('title'), 'Sub 1')

    def test_unauthorized_all_subjects_should_fail(self):
        response = self.client.get("/soren/allsubjects/")
        r_content = json.loads(response.content).get('detail')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(r_content, 'اطلاعات برای اعتبارسنجی ارسال نشده است.')

    def test_all_subjects_as_teacher_returns_empty(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results'), [])

    def test_all_subjects_as_teacher_multiple_subjects_multiple_courses(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course_1 = Course.objects.create(title='Course 1', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        sub_1 = Subject.objects.create(course=course_1, title='Sub 1')
        sub_2 = Subject.objects.create(course=course_2, title='Sub 2')
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Sub 2')

    def test_all_subjects_as_teacher_multiple_subjects_one_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        sub_1 = Subject.objects.create(course=course, title='Sub 1')
        sub_2 = Subject.objects.create(course=course, title='Sub 2')
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Sub 2')
        self.assertEqual(r_content[1].get('title'), 'Sub 1')

    def test_all_subjects_as_student_returns_empty(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content, [])

    def test_all_subjects_as_student_one_course_multiple_subjects(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        sub_1 = Subject.objects.create(course=course, title='Sub 1')
        sub_2 = Subject.objects.create(course=course, title='Sub 2')
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Sub 2')
        self.assertEqual(r_content[1].get('title'), 'Sub 1')

    def test_all_subjects_as_student_multiple_courses_multiple_subjects(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course_1 = Course.objects.create(title='Course 1', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_1.student.add(User.objects.get(email='b@gmail.com'))
        course_2.student.add(User.objects.get(email='b@gmail.com'))
        sub_1 = Subject.objects.create(course=course_1, title='Sub 1')
        sub_2 = Subject.objects.create(course=course_2, title='Sub 2')
        response = self.client.get('/soren/allsubjects/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Sub 2')

    def test_delete_subject_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course_1 = Course.objects.create(title='Course 1', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        sub_1 = Subject.objects.create(course=course_1, title='Sub 1')
        response = self.client.delete(f'/soren/subject-rd/{sub_1.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_delete_subject_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course_1 = Course.objects.create(title='Course 1', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        sub_1 = Subject.objects.create(course=course_1, title='Sub 1')
        response = self.client.delete(f'/soren/subject-rd/{sub_1.id}/')
        self.assertEqual(response.status_code, 204)


class TestPosts(TestBase):

    def test_view_posts_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.get(f'/soren/subjects/{subject.id}/posts/')
        r_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('description'), 'Post 1')

    def test_add_post_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(path=f'/soren/subjects/{subject.id}/newpost/',
                                    data={'title': 'Title 1', 'description': 'Post 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Title 1')
        self.assertEqual(r_content.get('description'), 'Post 1')

    def test_add_post_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd'
                          )
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(path=f'/soren/subjects/{subject.id}/newpost/',
                                    data={'title': 'Title 1', 'description': 'Post 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Title 1')
        self.assertEqual(r_content.get('description'), 'Post 1')

    def test_add_post_in_another_course_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(path=f'/soren/subjects/{subject.id}/newpost/',
                                    data={'title': 'Title 1', 'description': 'Post 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_view_no_posts(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.get(f'/soren/subjects/{subject.id}/posts/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results'), [])

    def test_view_posts_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get(f'/soren/subjects/{subject.id}/posts/')
        r_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('description'), 'Post 1')

    def test_add_post_in_another_course_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(f'/soren/subjects/{subject.id}/newpost/',
                                    data={'title': 'Post', 'description': 'desc'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_add_post_in_another_course_should_fail_2(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(f'/soren/subjects/{subject.id}/newpost/',
                                    data={'title': 'Post', 'description': 'desc'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_post_without_description_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        response = self.client.post(f'/soren/subjects/{subject.id}/newpost/', data={'title': 'Post'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content.get('description'), ['این مقدار لازم است.'])

    def test_save_post_unauthorized_should_fail(self):
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(f'/soren/savepost/{post.id}/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content).get('detail'), 'اطلاعات برای اعتبارسنجی ارسال نشده است.')

    def test_save_post_as_teacher_from_another_course_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(f'/soren/savepost/{post.id}/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content).get('detail'), 'یافت نشد.')

    def test_save_post_as_student_from_another_course_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(f'/soren/savepost/{post.id}/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content).get('detail'), 'یافت نشد.')

    def test_save_post_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(f'/soren/savepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content, 'ذخیره شد')

    def test_save_post_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(f'/soren/savepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content, 'ذخیره شد')

    def test_view_saved_posts(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/savedposts/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_unsave_post_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        post.savedby.add(User.objects.get(email='amir@gmail.com'))
        response = self.client.post(f'/soren/unsavepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content, 'از حالت ذخیره خارج شد')

    def test_unsave_post_as_teacher_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(f'/soren/unsavepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'شما این پست را ذخیره نکرده اید')

    def test_unsave_post_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='b@gmail.com'), description='Post 1')
        post.savedby.add(User.objects.get(email='b@gmail.com'))
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(f'/soren/unsavepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content, 'از حالت ذخیره خارج شد')

    def test_unsave_post_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='b@gmail.com'),
                                   description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(f'/soren/unsavepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'شما این پست را ذخیره نکرده اید')

    def test_delete_post(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='b@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.delete(f'/soren/post-rd/{post.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_post_should_fail(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='b@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.delete(f'/soren/post-rd/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_view_saved_posts_2(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get(f'/soren/unsavepost/{post.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)


class TestLikes(TestBase):
    def test_like_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('post_id'), post.id)

    def test_like_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('post_id'), post.id)

    def test_like_as_invalid_teacher_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_like_as_invalid_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_like_twice_as_teacher_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        like = PostLike.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'))
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'شما قبلا این پست را لایک کرده اید.')

    def test_delete_like(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        like = PostLike.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'))
        response = self.client.delete(f'/soren/removelike/{post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_like_twice_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        like = PostLike.objects.create(post=post, user=User.objects.get(email='b@gmail.com'))
        response = self.client.post(path=f'/soren/posts/{post.id}/newlike/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(r_content, 'شما قبلا این پست را لایک کرده اید.')

    def test_view_likes_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        like = PostLike.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'))
        response = self.client.get(path=f'/soren/posts/{post.id}/likes/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('post_id'), post.id)

    def test_view_likes_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        like = PostLike.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'))
        response = self.client.get(path=f'/soren/posts/{post.id}/likes/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('post_id'), post.id)


class TestComments(TestBase):
    def test_comments_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newcomment/', data={'text': 'Comment 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('post_id'), post.id)
        self.assertEqual(r_content.get('text'), 'Comment 1')

    def test_comment_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(path=f'/soren/posts/{post.id}/newcomment/', data={'text': 'Comment 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('post_id'), post.id)
        self.assertEqual(r_content.get('text'), 'Comment 1')

    def test_comment_as_invalid_teacher_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newcomment/', data={'text': 'Comment 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_comment_as_invalid_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        response = self.client.post(path=f'/soren/posts/{post.id}/newcomment/', data={'text': 'Comment 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(r_content, {'detail': 'یافت نشد.'})

    def test_view_comments_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'), text='Comment 1')
        response = self.client.get(path=f'/soren/posts/{post.id}/comments/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('post_id'), post.id)
        self.assertEqual(r_content.get('results')[0].get('text'), 'Comment 1')

    def test_view_comments_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'), text='Comment 1')
        response = self.client.get(path=f'/soren/posts/{post.id}/comments/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('post_id'), post.id)
        self.assertEqual(r_content.get('results')[0].get('text'), 'Comment 1')

    def test_delete_comment_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'), text='Comment 1')
        response = self.client.delete(f'/soren/deletecomment/{comment.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_comment_as_teacher_should_fail(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'), text='Comment 1')
        response = self.client.delete(f'/soren/deletecomment/{comment.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

    def test_delete_comment_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='b@gmail.com'), text='Comment 1')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.delete(f'/soren/deletecomment/{comment.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_comment_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(course=course, title='Subject 1')
        post = Post.objects.create(subject=subject, user=User.objects.get(email='amir@gmail.com'), description='Post 1')
        comment = PostComment.objects.create(post=post, user=User.objects.get(email='amir@gmail.com'), text='Comment 1')
        response = self.client.delete(f'/soren/deletecomment/{comment.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content, 'شما به این عمل دسترسی ندارید')

class TestSearch(TestBase):
    def test_search_course(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_3 = Course.objects.create(title='Mathematics', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get(path=f'/soren/courses/Cou/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Course 2')
        self.assertEqual((r_content[1].get('title')), 'Course 1')

    def test_search_invalid_course_should_return_empty(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_3 = Course.objects.create(title='Mathematics', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get(path=f'/soren/courses/Cou/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content, [])

    def test_search_course_2(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course_3 = Course.objects.create(title='Mathematics', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.get(path=f'/soren/courses/Cou/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Course 1')

    def test_search_course_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/courses/Cou/')
        r_content = json.loads(response.content).get('results')[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('title'), 'Course 1')

    def test_search_course_as_student_2(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        course_2.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/courses/Cou/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Course 2')
        self.assertEqual(r_content[1].get('title'), 'Course 1')

    def test_search_subject_as_teacher(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(title='Subject 1', course=course)
        subject_2 = Subject.objects.create(title='Subject 2', course=course_2)
        response = self.client.get('/soren/subjects/Sub/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Subject 1')

    def test_search_subject_as_teacher_2(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(title='Subject 1', course=course)
        subject_2 = Subject.objects.create(title='Subject 2', course=course_2)
        response = self.client.get('/soren/subjects/Sub/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Subject 2')
        self.assertEqual(r_content[1].get('title'), 'Subject 1')

    def test_search_subject_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(title='Subject 1', course=course)
        subject_2 = Subject.objects.create(title='Subject 2', course=course_2)
        course.student.add(User.objects.get(email='b@gmail.com'))
        course_2.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/subjects/Sub/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[1].get('title'), 'Subject 1')
        self.assertEqual(r_content[0].get('title'), 'Subject 2')

    def test_search_subject_as_student_2(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(title='Subject 1', course=course)
        subject_2 = Subject.objects.create(title='Subject 2', course=course_2)
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get('/soren/subjects/Sub/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('title'), 'Subject 1')

    def test_search_invalid_subjects_should_return_empty(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course_2 = Course.objects.create(title='Course 2', description='Nothing',
                                         teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                         end_date='2020-05-06', exam_date='2020-05-07')
        subject = Subject.objects.create(title='Subject 1', course=course)
        subject_2 = Subject.objects.create(title='Subject 2', course=course_2)
        response = self.client.get('/soren/subjects/Sub/')
        r_content = json.loads(response.content).get('results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content, [])

    def test_search_student_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get(f'/soren/courses/{course.id}/students/A/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(r_content.get('detail'), 'فقط اساتید به این عمل دسترسی دارند')

    def test_search_student(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get(f'/soren/courses/{course.id}/students/A/')
        r_content = json.loads(response.content).get('results')
        print(r_content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content[0].get('course_id'), course.id)
        self.assertEqual(r_content[0].get('email'), 'b@gmail.com')


class TestExercise(TestBase):
    def test_create_new_exercise(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        response = self.client.post(path=f'/soren/courses/{course.id}/newexercise/',
                                    data={'title': 'Exercise 1', 'description': 'Nothing',
                                          'deadline': '2020-05-05T05:13:10'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('title'), 'Exercise 1')
        self.assertEqual(r_content.get('description'), 'Nothing')

    def test_create_new_exercise_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        self.assertRaises(ValidationError, lambda: self.client.post(path=f'/soren/courses/{course.id}/newexercise/',
                                                                    data={'title': 'Exercise 1',
                                                                          'description': 'Nothing',
                                                                          'deadline': '2020-05-05T05:13:10'}))

    def test_create_new_exercise_as_invalid_teacher_should_fail(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        self.assertRaises(ValidationError, lambda: self.client.post(path=f'/soren/courses/{course.id}/newexercise/',
                                                                    data={'title': 'Exercise 1',
                                                                          'description': 'Nothing',
                                                                          'deadline': '2020-05-05T05:13:10'}))

    def test_view_exercises_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.get(path=f'/soren/courses/{course.id}/exercises/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('title'), exercise.title)
        self.assertEqual(r_content.get('results')[0].get('description'), exercise.description)

    def test_view_exercises_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.get(path=f'/soren/courses/{course.id}/exercises/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('title'), exercise.title)
        self.assertEqual(r_content.get('results')[0].get('description'), exercise.description)

    def test_delete_exercise_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.delete(path=f'/soren/exercise-rd/{exercise.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_exercise_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        course.student.add(User.objects.get(email='b@gmail.com'))
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        self.assertRaises(ValidationError, lambda: self.client.delete(path=f'/soren/exercise-rd/{exercise.id}/'))

    def test_view_teacher_exercise_list(self):
        self.client.login(email='amir@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='amir@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.get(f'/soren/teacherexercises/')
        self.assertEqual(response.status_code, 200)


    def test_view_exercise_answers_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        answer = Answer.objects.create(description='answer 1', exercise=exercise,
                                       user=User.objects.get(email='b@gmail.com'))
        response = self.client.get(path=f'/soren/exercises/{exercise.id}/answers/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('results')[0].get('description'), answer.description)

    def test_view_exercise_answers_as_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        answer = Answer.objects.create(description='answer 1', exercise=exercise,
                                       user=User.objects.get(email='b@gmail.com'))
        self.assertRaises(ValidationError, lambda: self.client.get(path=f'/soren/exercises/{exercise.id}/answers/'))

    def test_exercise_add_answer_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        response = self.client.post(path=f'/soren/exercises/{exercise.id}/newanswer/', data={'description': 'answer 1'})
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(r_content.get('description'), 'answer 1')

    def test_exercise_add_answer_as_stranger_student_should_fail(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        self.assertRaises(ValidationError, lambda: self.client.post(path=f'/soren/exercises/{exercise.id}/newanswer/',
                                                                    data={'description': 'answer 1'}))

    def test_exercise_add_answer_as_teacher_should_fail(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        self.assertRaises(ValidationError, lambda: self.client.post(path=f'/soren/exercises/{exercise.id}/newanswer/',
                                                                    data={'description': 'answer 1'}))

    def test_delete_exercise_answer_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        answer = Answer.objects.create(description='answer 1', exercise=exercise,
                                       user=User.objects.get(email='b@gmail.com'))
        response = self.client.delete(path=f'/soren/answer/{answer.id}/')
        self.assertEqual(response.status_code, 204)

    def test_get_exercise_answers_as_student(self):
        self.client.login(email='b@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        course.student.add(User.objects.get(email='b@gmail.com'))
        answer = Answer.objects.create(description='answer 1', exercise=exercise,
                                       user=User.objects.get(email='b@gmail.com'))
        response = self.client.get(path=f'/soren/answer/{answer.id}/')
        r_content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_content.get('description'), 'answer 1')

    def test_view_exercise_not_answer_students_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.get(path=f'/soren/notAnswerStudents/{exercise.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_exercise_answer_students_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.get(path=f'/soren/answerstudents/{exercise.id}/')
        self.assertEqual(response.status_code, 200)

    def test_view_exercise_answers_list_as_teacher(self):
        self.client.login(email='a@gmail.com', password='abcd')
        course = Course.objects.create(title='Course 1', description='Nothing',
                                       teacher=User.objects.get(email='a@gmail.com'), start_date='2020-05-05',
                                       end_date='2020-05-06', exam_date='2020-05-07')
        exercise = Exercise.objects.create(title='Exercise 1', description='Nothing',
                                           teacher=User.objects.get(email='a@gmail.com'),
                                           deadline='2020-05-05T05:13:10', course=course)
        response = self.client.get(path=f'/soren/exercise/{exercise.id}')
        self.assertEqual(response.status_code, 200)


import master.views as v


class TestUrls(SimpleTestCase):

    def test_user_signup_resolved(self):
        url = reverse('Signup')
        self.assertEqual(resolve(url).func.view_class, v.Signup)

    def test_user_signup_verification_resolved(self):
        url = reverse('Signup Verification')
        self.assertEqual(resolve(url).func.view_class, v.SVerification)

    def test_user_signin_resolved(self):
        url = reverse('Signin')
        self.assertEqual(resolve(url).func.view_class, v.Signin)

    def test_user_forgot_password_resolved(self):
        url = reverse('Forgot Password')
        self.assertEqual(resolve(url).func.view_class, v.ForgotPassword)

    def test_user_forgot_password_verification_resolved(self):
        url = reverse('Forgot Password Verification')
        self.assertEqual(resolve(url).func.view_class, v.Verification)

    def test_user_forgot_password_change_password_resolved(self):
        url = reverse('Forgot Password Change Password')
        self.assertEqual(resolve(url).func.view_class, v.FPChangePassword)

    def test_user_profile_resolved(self):
        url = reverse('Profile')
        self.assertEqual(resolve(url).func.view_class, v.Profile)

    def test_user_delete_account_resolved(self):
        url = reverse('Delete Account')
        self.assertEqual(resolve(url).func.view_class, v.DeleteAccount)

    def test_user_change_email_resolved(self):
        url = reverse('Change Email')
        self.assertEqual(resolve(url).func.view_class, v.ChangeEmail)

    def test_user_email_verification_resolved(self):
        url = reverse('Email Verification')
        self.assertEqual(resolve(url).func.view_class, v.EmailVerification)

    def test_user_change_password_resolved(self):
        url = reverse('Change Password')
        self.assertEqual(resolve(url).func.view_class, v.ChangePassword)

    def test_user_support_resolved(self):
        url = reverse('Support')
        self.assertEqual(resolve(url).func.view_class, v.Support)


class TestUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            type='t',
            university='test',
            email='ab@ab.com',
            password='12345678',
        )

    def test_user_create_successfully(self):
        sample_user = User.objects.create_user(
            type='t',
            university='test',
            email='sample@test.test',
            password='123456',
        )

        self.assertTrue(sample_user.id)

    def test_user_without_email(self):
        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            university='test',
            email='',
            password='123456'
        ))

        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            university='test',
            password='123456'
        ))

    def test_user_without_type(self):
        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='',
            university='test',
            email='sample@test.test',
            password='123456'
        ))

        self.assertRaises(ValueError, lambda: User.objects.create_user(
            university='test',
            email='sample@test.test',
            password='123456'
        ))

    def test_user_without_university(self):
        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            university='',
            email='sample@test.test',
            password='123456'
        ))

        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            email='sample@test.test',
            password='123456'
        ))

    def test_user_without_password(self):
        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            university='test',
            email='sample@test.test',
            password=''
        ))

        self.assertRaises(ValueError, lambda: User.objects.create_user(
            type='t',
            university='test',
            email='sample@test.test',
        ))

    def test_user_create_superuser_successfully(self):
        sample_user = User.objects.create_superuser(
            email='sample@test.test',
            password='123456',
        )

        self.assertTrue(sample_user.is_staff)
        self.assertTrue(sample_user.is_superuser)

    def test_user_avatar_directory_path(self):
        sample_user = User.objects.create_superuser(
            email='sample@test.test',
            password='123456',
        )
        sample_filename = 'avatar.jpg'

        expected = 'user/sample@test.test/photo/avatar.jpg'

        self.assertEqual(user_photo_directory_path(sample_user, sample_filename), expected)

    def test_SigninApiView_400_1(self):
        url = reverse('Signin')
        body = {
            "email": "aa",
            "password": "12345678"
        }

        response = self.client.post(url, body)
        self.assertEqual(response.status_code, 400)

        body['email'] = 'a@a'
        body['password'] = '123'

        response = self.client.post(url, body)
        self.assertEqual(response.status_code, 400)

    def test_support_as_logined_user(self):
        self.client.login(email='a@gmail.com', password='abcd')
        url = reverse('Support')
        body = {'email': 'a@gmail.com', 'title': 'test', 'description': 'test'}
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, 201)

    def test_support_as_another_user(self):
        url = reverse('Support')
        body = {'email': 'abcd@gmail.com', 'title': 'test', 'description': 'test'}
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, 201)

    def test_user_is_active_by_default(self):
        self.assertFalse(self.user.is_active)

    def test_user_assign_email_on_creation(self):
        self.assertEqual(self.user.email, 'ab@ab.com')

    def test_user_assign_password_on_creation(self):
        self.assertTrue(self.user.check_password('12345678'))


class TestValidators(TestCase):

    def test_validate_email_contain_at_sign(self):
        sample_email = 'example.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_multiple_at_sign(self):
        sample_email = 'A@b@c@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_no_special_char_in_local_part(self):
        sample_email = 'a”b(c)d,e:f;gi[j\k]l@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_quoted_strings(self):
        sample_email = 'abc”test”email@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_spaces_quotes_and_backslashes(self):
        sample_email = 'abc is”not\\valid@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_quotes_after_backslash(self):
        sample_email = 'abc\is\”not\\valid@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_double_dot_before(self):
        sample_email = '.test@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_double_dot_before_domain(self):
        sample_email = 'test@domain..com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_leading_space(self):
        sample_email = 'test@domain.com    '
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_trailing_space(self):
        sample_email = '    test@domain.com'
        self.assertRaises(ValidationError, lambda: validate_email(sample_email))

    def test_validate_email_valid_form(self):
        sample_email = 'test@domain.com'
        self.assertIsNone(validate_email(sample_email))
