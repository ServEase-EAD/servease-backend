from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email",)

class CustomUserChangeForm(UserChangeForm):  # Fixed: should inherit from UserChangeForm
    class Meta:
        model = CustomUser
        fields = ("email",)        