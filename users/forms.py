from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser



class SignupForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('email',)

class EditForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)