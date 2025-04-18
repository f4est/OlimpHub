# core/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission

class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        post_migrate.connect(create_groups, sender=self)

def create_groups(sender, **kwargs):
    # 1) группы
    student, _ = Group.objects.get_or_create(name="student")
    teacher, _ = Group.objects.get_or_create(name="teacher")
    jury,    _ = Group.objects.get_or_create(name="jury")

    # 2) «глобальные» права учителя (создание/правка своих олимпиад)
    perms = [
        "add_olympiad", "change_olympiad", "delete_olympiad",
        "add_problem",  "change_problem",  "delete_problem",
        "add_testcase", "change_testcase", "delete_testcase"
    ]
    teacher.permissions.set(Permission.objects.filter(codename__in=perms))
