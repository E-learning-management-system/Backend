from django.contrib import admin
from master.models import Course, CourseStudent, Exercise, ExerciseAnswer, Tag, User, Post, PostComment, PostLike, \
    Subject

admin.site.register(Tag)


class ExerciseInline(admin.StackedInline):
    model = Exercise


class SubjectInline(admin.StackedInline):
    model = Subject


class CourseStudentInline(admin.StackedInline):
    model = CourseStudent


class CourseStudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course']
    list_filter = ['course']
    fieldsets = (('مشخصات', {'fields': ('course', 'user')},),)


class CourseAdmin(admin.ModelAdmin):
    inlines = [SubjectInline, CourseStudentInline]
    list_display = ['title', 'teacher', 'start_date', 'end_date', 'exam_date']
    list_filter = ['teacher', 'start_date', 'end_date', 'exam_date']
    fieldsets = (('مشخصات', {'fields': ('title', 'description', 'teacher', 'end_date', 'exam_date')},),)


class UAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'type', 'university', 'photo', 'date_joined']
    list_filter = ['username', 'first_name', 'last_name', 'type', 'university', 'photo', 'date_joined']
    inlines = [CourseStudentInline]
    fieldsets = (('اطلاعات اولیه', {'fields': ('username', 'email', 'university', 'type')},),
                 ('اطلاعات تکمیلی', {'fields': ('first_name', 'last_name', 'phone', 'state', 'city', 'photo'), },))


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']
    list_filter = ['title', 'course']
    inlines = [ExerciseInline]
    fieldsets = (('مشخصات', {'fields': ('title', 'course')},),)


class LikeInline(admin.StackedInline):
    model = PostLike


class CommentInline(admin.StackedInline):
    model = PostComment


class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'date']
    list_filter = ['user', 'post', 'date']
    fieldsets = (('مشخصات', {'fields': ('user', 'post')},),)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'date']
    list_filter = ['user', 'post', 'date']
    fieldsets = (('مشخصات', {'fields': ('user', 'post')},),)


class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline, LikeInline]
    list_filter = ['poster', 'postId', 'date']
    list_display = [ 'postId','poster', 'file', 'date']


class ExerciseAnswerInline(admin.StackedInline):
    model = ExerciseAnswer


class ExerciseAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'date', 'file']
    fieldsets = (('مشخصات', {'fields': ('user', 'exercise', 'file')},),)


class ExerciseAdmin(admin.ModelAdmin):
    inlines = [ExerciseAnswerInline]
    list_display = ('title', 'course', 'subject', 'author', 'status', 'deadline')
    list_filter = ('author', 'deadline', 'status', 'subject')
    fieldsets = (
        ('اطلاعات کلی', {'fields': ('title', 'author', 'course', 'subject')},
         ),
        ('وضعیت تحویل', {'fields': ('status', 'deadline')})
    )


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(User, UAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseStudent, CourseStudentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, LikeAdmin)
admin.site.register(PostComment, CommentAdmin)
admin.site.register(ExerciseAnswer, ExerciseAnswerAdmin)