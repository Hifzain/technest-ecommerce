from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff, login_url='accounts:login')(view_func)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff