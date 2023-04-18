from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin

from users.models import User
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from products.models import Basket
from common.views import TitleMixin


class UserRegistrationView(TitleMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:login')
    success_message = 'Вы успещно зарегестрировались!'
    title = 'Store - Регистрация'


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm


class UserProfileView(TitleMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    title = 'Store - Личный кабинет'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        baskets = Basket.objects.filter(user=self.request.user)

        context = super(UserProfileView, self).get_context_data()
        context['baskets'] = baskets
        context['total_sum'] = sum(basket.sum() for basket in baskets)
        context['total_quantity'] = baskets.aggregate(Sum('quantity')).get('quantity__sum')
        return context
