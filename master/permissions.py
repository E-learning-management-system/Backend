from rest_framework import status, permissions


class IsExerciseAuthor(permissions.BasePermission):
    message = 'شما سازنده این تمرین نیستید.'
    status_code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        return obj.author.id == request.user.id


class IsExerciseAnswerer(permissions.BasePermission):
    message = 'این جواب تمرین را شما نداده اید'
    status_code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id
