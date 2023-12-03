from django.db import models
from django.contrib import admin

# Candidate
class Candidate(models.Model):
    name = models.CharField(max_length=8)
    party = models.CharField(max_length=8, blank=True, null=True)
    partner = models.CharField(max_length=8, blank=True, null=True)
    profile = models.TextField(blank=True, null=True)
    politics = models.TextField(blank=True, null=True)
    facebook = models.URLField(max_length=60, blank=True, null=True)

    def __str__(self):
        return self.name

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'party', 'partner')
    ordering = ['id']


# Gender (男 / 女 / 其他)
class Gender(models.Model):
    option = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.option

@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'option')
    ordering = ['id']


# Age (<20 / 20~29 / 30~39 / 40~49 / 50~59 / 60~69 / >70)
class Age(models.Model):
    option = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.option

@admin.register(Age)
class AgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'option')
    ordering = ['id']


# Area (北北基 / 桃竹苗 / 中彰投 / 雲嘉南 / 高屏澎 / 宜花東 / 金馬 / 其他)
class Area(models.Model):
    option = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.option

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'option')
    ordering = ['id']


# User
class User(models.Model):
    uid = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=10)
    image = models.URLField(max_length=80, blank=True, null=True)
    language = models.CharField(max_length=8)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, blank=True, null=True)
    age = models.ForeignKey(Age, on_delete=models.SET_NULL, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, blank=True, null=True)
    join = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'name', 'language', 'gender', 'age', 'area', 'vote', 'join')


# Vote
class Vote(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, related_name='candidate', blank=True, null=True)
    # # vote for 賴 / 侯 / 柯
    # option1 = models.ForeignKey(Candidate, on_delete=models.SET_NULL, related_name='option1', blank=True, null=True)
    # # vote for 賴 / 侯 / 柯 / 郭
    # option2 = models.ForeignKey(Candidate, on_delete=models.SET_NULL, related_name='option2', blank=True, null=True)
    # # not vote for 賴 / 侯 / 柯 / 郭
    # option3 = models.ForeignKey(Candidate, on_delete=models.SET_NULL, related_name='option3', blank=True, null=True)
    
    def __str__(self):
        vote = self.user.name
        if self.candidate is not None:
            vote += " / "+self.candidate.name
        # if self.option1 is not None:
        #     vote += " / "+self.option1.name
        # if self.option2 is not None:
        #     vote += " / "+self.option2.name
        # if self.option3 is not None:
        #     vote += " / "+self.option3.name
        return vote

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'candidate')
    # list_display = ('id', 'user', 'option1', 'option2', 'option3')


# Comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True, auto_now_add=False)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'candidate', 'content', 'date')


# vote history
class History(models.Model):
    date = models.DateField(auto_now=False, auto_now_add=True)
    vote = models.JSONField()

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'vote')
    ordering = ['id']

