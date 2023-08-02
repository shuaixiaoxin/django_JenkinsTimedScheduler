from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserToken(models.Model):
    token = models.CharField(max_length=255, verbose_name='Token', unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = "用户令牌"
        verbose_name_plural = verbose_name
        db_table = 'user_tokens'
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_token')
        ]

