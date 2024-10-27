from django.contrib.auth.base_user import BaseUserManager
class CustomUserManager(BaseUserManager):
    """ Custom manager for CustomUser with phone as the unique identifier """

    def create_user(self, phone, password=None, **extra_fields):
        """ Create and save a User with the given phone number and password """

        if not phone:
            raise ValueError('User must have a phone number')

        email = extra_fields.get('email')
        if email:
            extra_fields['email'] = self.normalize_email(email)

        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """ Create and save a SuperUser with the given phone number and password """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(phone, password, **extra_fields)
