from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class OwnerAdminAccessTest(TestCase):
    def test_anonymous_is_sent_to_admin_login(self):
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(response, reverse("admin:login") + "?next=/admin/")

    def test_staff_and_demo_accounts_cannot_enter(self):
        for username, superuser in [("regular_staff", False), ("demo_premium", True), ("demo_user", True)]:
            user = User.objects.create_user(username=username, is_staff=True, is_superuser=superuser)
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)
            self.client.logout()

    def test_owner_can_open_admin_and_user_editor(self):
        owner = User.objects.create_superuser(username="owner", email="owner@example.com", password="test-only-password")
        self.client.force_login(owner)
        self.assertContains(self.client.get(reverse("admin:index")), "Administracja upclass")
        self.assertEqual(self.client.get(reverse("admin:auth_user_change", args=[owner.pk])).status_code, 200)

    def test_inactive_owner_cannot_enter(self):
        owner = User.objects.create_superuser(username="inactive-owner", email="owner@example.com", password="test-only-password")
        owner.is_active = False
        owner.save()
        self.client.force_login(owner)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)
