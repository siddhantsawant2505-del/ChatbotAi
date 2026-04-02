from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

class Puzzle(models.Model):
    LEVEL_CHOICES = [(1, "Number Lock"), (2, "Maze of Math"), (3, "Cipher Wall"), (4, "Time Paradox"), (5, "AI Battle")]

    level = models.IntegerField(choices=LEVEL_CHOICES)
    question = models.TextField()
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    correct_option = models.IntegerField()  # Store the correct option (1-4)

    def __str__(self):
        return f"Level {self.level}: {self.question}"

class PlayerProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_level = models.IntegerField(default=1)  # Start at Level 1
    score = models.IntegerField(default=0)

    def advance_level(self):
        if self.current_level < 5:
            self.current_level += 1
            self.save()