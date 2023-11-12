from django.db import models


class UserResponse(models.Model):
    responder_name = models.CharField(max_length=100000)
    question = models.CharField(max_length=100000)
    user_answer = models.TextField()
    score = models.FloatField()  # Change from models.IntegerField() to models.FloatField()

    def __str__(self):
        return self.responder_name  # Display a meaningful string representation for your model