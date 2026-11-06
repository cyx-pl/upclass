"""Production startup and ICE configuration without a relay service."""

import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class OptionalTurnStartupTest(SimpleTestCase):
    def start_settings(self, **overrides):
        environment = os.environ.copy()
        for key in ("TURN_CREDENTIAL", "TURN_STATIC_AUTH_SECRET", "DATABASE_URL", "REDIS_URL"):
            environment.pop(key, None)
        environment.update(
            DJANGO_SETTINGS_MODULE="tutorflow.settings",
            DEBUG="False",
            SECRET_KEY="test-only-production-startup-key",
            ALLOWED_HOSTS="localhost",
        )
        environment.update(overrides)
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "import json; from apps.meeting.turn_auth import ice_servers; "
                "print(json.dumps(ice_servers()))",
            ],
            cwd=settings.BASE_DIR,
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    def test_production_starts_without_turn_and_only_advertises_stun(self):
        result = self.start_settings()
        self.assertEqual(result.returncode, 0, result.stderr)
        servers = json.loads(result.stdout)
        self.assertTrue(servers)
        self.assertTrue(all(server["urls"].startswith("stun:") for server in servers))
        self.assertTrue(all("credential" not in server for server in servers))

    def test_configured_turn_still_works(self):
        result = self.start_settings(TURN_CREDENTIAL="test-relay-password")
        self.assertEqual(result.returncode, 0, result.stderr)
        servers = json.loads(result.stdout)
        self.assertTrue(any(server["urls"].startswith("turn:") for server in servers))

    def test_missing_secret_key_still_blocks_production(self):
        result = self.start_settings(SECRET_KEY="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SECRET_KEY environment variable must be set", result.stderr)

    def test_missing_allowed_hosts_still_blocks_production(self):
        result = self.start_settings(ALLOWED_HOSTS="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ALLOWED_HOSTS environment variable must be set", result.stderr)
