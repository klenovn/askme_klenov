from django.contrib import admin
from .models import Profile, Tag, Question, Answer, Like, QuestionTag


admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Like)
admin.site.register(QuestionTag)