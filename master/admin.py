from django.contrib import admin
from master.models import Course, CourseStudent, Exercise, Answer, User, Post, PostComment, PostLike, \
    Subject


class ExerciseInline(admin.StackedInline):
    model = Exercise


class SubjectInline(admin.StackedInline):
    model = Subject


class CourseStudentInline(admin.StackedInline):
    model = CourseStudent


class PostInline(admin.StackedInline):
    model = Post


class CourseStudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course']
    list_filter = ['course']


class CourseAdmin(admin.ModelAdmin):
    ordering = ['start_date']
    inlines = [SubjectInline, CourseStudentInline, PostInline]
    list_display = ['id', 'title', 'teacher', 'start_date', 'end_date', 'exam_date']
    list_filter = ['teacher', 'start_date', 'end_date', 'exam_date', 'student']
    search_fields = ['title', 'description']


class UAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'type', 'university', 'photo', 'date_joined']
    list_filter = ['type', 'university', 'date_joined']
    search_fields = ['username']
    inlines = [CourseStudentInline]


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course']
    list_filter = ['course']
    search_fields = ['title']
    inlines = [ExerciseInline]


class LikeInline(admin.StackedInline):
    model = PostLike


class CommentInline(admin.StackedInline):
    model = PostComment


class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'date']
    list_filter = ['user', 'post', 'date']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'date']
    list_filter = ['user', 'post', 'date']


class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline, LikeInline]
    list_filter = ['poster', 'date']
    list_display = ['id', 'poster', 'file', 'date']
    search_fields = ['id']


class AnswerInline(admin.StackedInline):
    model = Answer


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'date', 'file']


class ExerciseAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('title', 'course', 'subject', 'author', 'deadline')
    list_filter = ('author', 'deadline', 'subject')


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(User, UAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseStudent, CourseStudentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, LikeAdmin)
admin.site.register(PostComment, CommentAdmin)
admin.site.register(Answer, AnswerAdmin)
