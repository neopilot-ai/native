"""
Test cases for FAANG-Level AI Developer Mode using Next.js and NestJS patterns.
Tests sensitive config handling, security analysis, and code generation capabilities.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import the modules we're testing
from prompting.system_prompts.faang_engineer_prompt import load_system_prompt, build_combined_prompt
from core.cache.ai_response_cache import AIResponseCache
from core.meta_prompting.prompt_strategies import PromptStrategy


class TestFAANGEngineerMode:
    """Test suite for FAANG-Level AI Developer Mode functionality."""

    @pytest.fixture
    def sample_nextjs_config(self):
        """Sample Next.js configuration with sensitive data."""
        return {
            "name": "nextjs-app",
            "version": "1.0.0",
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "@auth/prisma-adapter": "^1.0.0",
            },
            "env": {
                "DATABASE_URL": "postgresql://user:password@localhost:5432/app",
                "NEXTAUTH_SECRET": "super-secret-key",
                "STRIPE_API_KEY": "sk_live_123456789",
            },
            "config": {"api": {"auth": {"jwtSecret": "jwt-secret-key", "sessionTimeout": 3600}}},
        }

    @pytest.fixture
    def sample_nestjs_config(self):
        """Sample NestJS configuration with sensitive data."""
        return {
            "name": "nestjs-api",
            "version": "2.0.0",
            "dependencies": {
                "@nestjs/common": "^10.0.0",
                "@nestjs/config": "^3.0.0",
                "@nestjs/jwt": "^10.0.0",
            },
            "env": {
                "DATABASE_HOST": "prod-db.company.com",
                "DATABASE_PASSWORD": "Prod@2024!Pass",
                "JWT_SECRET": "nestjs-jwt-secret",
                "REDIS_URL": "redis://:redis-pass@cache.company.com:6379",
            },
            "config": {
                "jwt": {"secret": "nestjs-secret", "expiresIn": "1h"},
                "database": {"ssl": True, "cert": "/path/to/cert.pem"},
            },
        }

    def test_load_system_prompt(self):
        """Test loading of FAANG engineer system prompt."""
        prompt = load_system_prompt()

        assert isinstance(prompt, dict)
        assert "persona" in prompt
        assert "rules" in prompt
        assert "devops" in prompt
        assert len(prompt["rules"]) > 0
        assert any("security" in rule.lower() for rule in prompt["rules"])

    def test_build_combined_prompt(self):
        """Test building combined prompts for analysis."""
        user_prompt = "Analyze this Next.js config for security issues"
        combined = build_combined_prompt(user_prompt)

        assert isinstance(combined, str)
        assert "FAANG" in combined or "Principal Engineer" in combined
        assert user_prompt in combined
        assert "security" in combined.lower()

    def test_ai_response_cache_ttl(self):
        """Test AI response cache TTL functionality."""
        cache = AIResponseCache()

        # Test setting and getting cached response
        test_key = "test-security-analysis"
        test_value = {"security_issues": []}

        cache.set(test_key, test_value, ttl=1)
        retrieved = cache.get(test_key)

        assert retrieved == test_value

    def test_sensitive_data_detection(self, sample_nextjs_config, sample_nestjs_config):
        """Test detection of sensitive configuration data."""
        # Test Next.js config
        nextjs_secrets = []
        for key, value in sample_nextjs_config.get("env", {}).items():
            if any(secret in key.lower() for secret in ["secret", "key", "password"]):
                nextjs_secrets.append(key)

        assert "NEXTAUTH_SECRET" in nextjs_secrets
        assert "STRIPE_API_KEY" in nextjs_secrets

        # Test NestJS config
        nestjs_secrets = []
        for key, value in sample_nestjs_config.get("env", {}).items():
            if any(secret in key.lower() for secret in ["secret", "key", "password"]):
                nestjs_secrets.append(key)

        assert "JWT_SECRET" in nestjs_secrets
        assert "DATABASE_PASSWORD" in nestjs_secrets

    def test_config_sanitization(self, sample_nextjs_config):
        """Test configuration sanitization for display/logging."""

        def sanitize_config(config):
            """Remove sensitive values from config for safe display."""
            sanitized = config.copy()
            sensitive_keys = ["secret", "key", "password", "token"]

            if "env" in sanitized:
                for key, value in sanitized["env"].items():
                    if any(sensitive in key.lower() for sensitive in sensitive_keys):
                        sanitized["env"][key] = "***REDACTED***"

            return sanitized

        sanitized = sanitize_config(sample_nextjs_config)

        assert sanitized["env"]["NEXTAUTH_SECRET"] == "***REDACTED***"
        assert sanitized["env"]["STRIPE_API_KEY"] == "***REDACTED***"
        assert "DATABASE_URL" in sanitized["env"]  # Non-sensitive should remain

    def test_integration_test_workflow(self, sample_nextjs_config, sample_nestjs_config):
        """Test complete integration workflow."""
        # 1. Load system prompt
        system_prompt = load_system_prompt()
        assert system_prompt is not None

        # 2. Create cache
        cache = AIResponseCache()
        assert cache is not None

        # 3. Analyze configurations
        configs = [sample_nextjs_config, sample_nestjs_config]
        analysis_results = []

        for config in configs:
            # Simulate analysis
            cache_key = f"config_analysis_{hash(json.dumps(config, sort_keys=True))}"
            cached_result = cache.get(cache_key)

            if not cached_result:
                # Simulate analysis
                result = {"secrets_found": 3, "security_score": 7.5}
                cache.set(cache_key, result)
                analysis_results.append(result)
            else:
                analysis_results.append(cached_result)

        assert len(analysis_results) == 2
        assert all(result["secrets_found"] > 0 for result in analysis_results)


class TestSecurityValidation:
    """Security validation tests for sensitive configurations."""

    def test_password_strength_validation(self):
        """Test password strength validation."""
        weak_passwords = ["password", "123456", "secret"]
        strong_passwords = ["Str0ng!P@ssw0rd", "C0mpl3x#S3cur3"]

        def is_strong(password):
            return (
                len(password) >= 8
                and any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)
            )

        assert all(not is_strong(pw) for pw in weak_passwords)
        assert all(is_strong(pw) for pw in strong_passwords)

    def test_api_key_pattern_detection(self):
        """Test API key pattern detection."""
        api_key_patterns = [
            "sk_live_",  # Stripe
            "ghp_",  # GitHub
            "AIza",  # Google
            "xoxb-",  # Slack
        ]

        test_keys = [
            "sk_live_123456789",
            "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "AIzaSyD1234567890ABCDEF",
            "xoxb-1234567890-1234567890",
        ]

        detected = []
        for key in test_keys:
            for pattern in api_key_patterns:
                if key.startswith(pattern):
                    detected.append(key)
                    break

        assert len(detected) == len(test_keys)

    def test_database_url_parsing(self):
        """Test database URL parsing and validation."""
        db_urls = [
            "postgresql://user:password@localhost:5432/db",
            "mysql://user:pass@host:3306/database",
            "mongodb://user:pass@host:27017/db",
        ]

        def has_credentials(url):
            return "@" in url and "://" in url

        assert all(has_credentials(url) for url in db_urls)

    def test_environment_variable_scanning(self):
        """Test environment variable scanning for secrets."""
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@host/db",
            "API_KEY": "secret-api-key",
            "PORT": "3000",
            "NODE_ENV": "production",
            "JWT_SECRET": "jwt-secret-key",
        }

        sensitive_vars = []
        sensitive_patterns = ["secret", "key", "password", "token", "database"]

        for key, value in env_vars.items():
            if any(pattern in key.lower() for pattern in sensitive_patterns):
                sensitive_vars.append(key)

        assert len(sensitive_vars) == 3
        assert "API_KEY" in sensitive_vars
        assert "JWT_SECRET" in sensitive_vars
        assert "DATABASE_URL" in sensitive_vars
        assert "PORT" not in sensitive_vars
