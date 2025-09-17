from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Company(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owned_company',
        verbose_name='Владелец'
    )
    name = models.CharField(max_length=255, verbose_name='Название компании')
    inn = models.CharField(max_length=12, verbose_name='ИНН', unique=True, blank=True, null=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def employees_list(self):
        """Возвращает всех сотрудников компании (включая владельца)"""
        employees = list(self.employees.all())
        owner_employee = Employee(
            user=self.owner,
            company=self,
            position='Владелец'
        )
        employees.insert(0, owner_employee)
        return employees

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'

class Storage(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='storages',
        verbose_name='Компания'
    )
    name = models.CharField(max_length=255, verbose_name='Название склада')
    address = models.TextField(verbose_name='Адрес')
    capacity = models.PositiveIntegerField(verbose_name='Вместимость')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='Пользователь'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Компания'
    )
    position = models.CharField(max_length=255, verbose_name='Должность', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активный сотрудник')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.company.name}"

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        unique_together = ('user', 'company')