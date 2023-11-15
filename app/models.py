from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='avatars/user_avatar_placeholder.jpeg', upload_to='avatars/', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

class Tag(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word

class QuestionManager(models.Manager):
    def get_best_questions(self):
        return self.order_by('-rating', '-created_at')

    def get_newest_questions(self):
        return self.order_by('-created_at')
    

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title
    
class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to '{self.question.title}'"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_like = models.BooleanField(default=True)

    def __str__(self):
        return f"Like by {self.user.username} on {self.question.title if self.question else self.answer.question.title}"
    
class QuestionTag(models.Model):
    question = question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class QuestionTagManager(models.Manager):

    def get_tags_by_question(self, question):
        return self.filter(question=question)

    
