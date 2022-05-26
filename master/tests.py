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
                                                                    'start_date': '2020-05-05',
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
