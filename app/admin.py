from django.contrib import admin
from .models import Profile, Tag, Question, Answer, QuestionTag, QuestionReaction, AnswerReaction


admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionTag)
admin.site.register(QuestionReaction)
admin.site.register(AnswerReaction)