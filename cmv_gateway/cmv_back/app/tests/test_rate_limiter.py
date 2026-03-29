"""
Tests pour le module rate_limiter.

Tests de propriété (Hypothesis) et tests unitaires pour le rate limiting.

**Validates: Requirements 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3**
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient
from hypothesis import given, settings, strategies as st, HealthCheck
from pyrate_limiter import Duration, Limiter, Rate
from pyrate_limiter.buckets.redis_bucket import RedisBucket

from app.main import app
from app.utils.rate_limiter import (
    custom_callback,
    custom_identifier,
    init_rate_limiter,
    close_rate_limiter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_async(coro):
    """Helper to run async code in sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _make_request(headers: dict | None = None, client_host: str | None = None):
    """Crée un mock Request avec les headers et client spécifiés."""
    request = MagicMock()
    request.headers = headers or {}
    if client_host is not None:
        request.client = MagicMock()
        request.client.host = client_host
    else:
        request.client = None
    return request


# Stratégie pour générer des adresses IPv4 valides
ipv4_strategy = st.tuples(
    st.integers(min_value=1, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
).map(lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}")


# ---------------------------------------------------------------------------
# Fixtures for rate-limiter integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
async def fake_redis():
    """Crée un FakeRedis pour simuler Valkey dans les tests."""
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.aclose()


@pytest.fixture()
async def login_limiter_fixture(fake_redis):
    """Crée un Limiter login (5 req/60s) avec RedisBucket sur fakeredis."""
    rate = Rate(5, Duration.MINUTE)
    bucket = await RedisBucket.init([rate], fake_redis, "test:login")
    limiter = Limiter(bucket)
    yield limiter
    limiter.close()


@pytest.fixture()
async def global_limiter_fixture(fake_redis):
    """Crée un Limiter global (60 req/60s) avec RedisBucket sur fakeredis."""
    rate = Rate(60, Duration.MINUTE)
    bucket = await RedisBucket.init([rate], fake_redis, "test:global")
    limiter = Limiter(bucket)
    yield limiter
    limiter.close()


@pytest.fixture()
async def patched_limiters(login_limiter_fixture, global_limiter_fixture):
    """Patch les limiters du module rate_limiter avec les instances fakeredis."""
    import app.utils.rate_limiter as rl

    original_login = rl.login_limiter
    original_global = rl.global_limiter
    rl.login_limiter = login_limiter_fixture
    rl.global_limiter = global_limiter_fixture
    yield
    rl.login_limiter = original_login
    rl.global_limiter = original_global


@pytest.fixture()
async def rate_limited_client(patched_limiters):
    """Client HTTP avec rate limiting actif (limiters patchés avec fakeredis)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Property 5: Identification client par IP (existing tests)
# ---------------------------------------------------------------------------

class TestClientIdentification:
    """
    Property 5: Identification client par IP

    **Validates: Requirements 6.1, 6.2**

    Pour toute requête HTTP, si l'en-tête X-Forwarded-For est présent avec
    une liste d'IPs, l'identifiant client utilisé doit être la première IP
    de cette liste. Si l'en-tête est absent, l'identifiant doit être
    request.client.host.
    """

    @settings(max_examples=100)
    @given(
        first_ip=ipv4_strategy,
        other_ips=st.lists(ipv4_strategy, min_size=0, max_size=5),
    )
    def test_x_forwarded_for_uses_first_ip(self, first_ip: str, other_ips: list[str]):
        """
        Quand X-Forwarded-For est présent, la première IP est utilisée.

        **Validates: Requirements 6.2**
        """
        all_ips = [first_ip] + other_ips
        xff_header = ", ".join(all_ips)
        request = _make_request(
            headers={"X-Forwarded-For": xff_header},
            client_host="127.0.0.1",
        )
        result = run_async(custom_identifier(request))
        assert result == first_ip

    @settings(max_examples=100)
    @given(client_ip=ipv4_strategy)
    def test_no_xff_uses_client_host(self, client_ip: str):
        """
        Sans X-Forwarded-For, request.client.host est utilisé.

        **Validates: Requirements 6.1**
        """
        request = _make_request(headers={}, client_host=client_ip)
        result = run_async(custom_identifier(request))
        assert result == client_ip

    def test_no_ip_returns_unknown(self):
        """
        Sans IP déterminable, retourne 'unknown'.

        **Validates: Requirements 6.3**
        """
        request = _make_request(headers={}, client_host=None)
        result = run_async(custom_identifier(request))
        assert result == "unknown"


# ---------------------------------------------------------------------------
# Property 1: Limitation stricte du endpoint login
# ---------------------------------------------------------------------------

class TestLoginRateLimit:
    """
    Property 1: Limitation stricte du endpoint login

    **Validates: Requirements 2.1, 2.2, 2.3**

    Pour toute adresse IP et pour tout nombre N de requêtes envoyées sur
    /api/auth/login dans une fenêtre de 60 secondes, si N > 5, alors les
    requêtes au-delà de la 5ème doivent retourner un code HTTP 429 avec un
    en-tête Retry-After contenant une valeur numérique positive.
    """

    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    @given(n_requests=st.integers(min_value=6, max_value=15))
    def test_login_rate_limit(self, n_requests: int):
        """
        Envoyer N > 5 requêtes login dans une fenêtre doit bloquer après la 5ème.

        **Validates: Requirements 2.1, 2.2, 2.3**
        """

        async def _run(n: int):
            redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                login_rate = Rate(5, Duration.MINUTE)
                login_bucket = await RedisBucket.init(
                    [login_rate], redis, "prop1:login"
                )
                login_lim = Limiter(login_bucket)

                global_rate = Rate(60, Duration.MINUTE)
                global_bucket = await RedisBucket.init(
                    [global_rate], redis, "prop1:global"
                )
                global_lim = Limiter(global_bucket)

                import app.utils.rate_limiter as rl

                orig_login, orig_global = rl.login_limiter, rl.global_limiter
                rl.login_limiter = login_lim
                rl.global_limiter = global_lim

                try:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test",
                    ) as ac:
                        statuses = []
                        for _ in range(n):
                            resp = await ac.post(
                                "/api/auth/login",
                                json={
                                    "username": "test@test.fr",
                                    "password": "wrong",
                                },
                            )
                            statuses.append(resp.status_code)

                        # First 5 must NOT be 429
                        for i, s in enumerate(statuses[:5]):
                            assert s != 429, (
                                f"Request {i+1} should not be rate-limited"
                            )

                        # Requests beyond 5 must be 429
                        for i, s in enumerate(statuses[5:], start=6):
                            assert s == 429, (
                                f"Request {i} should be 429, got {s}"
                            )

                        # Check Retry-After header on last (blocked) request
                        last_resp = await ac.post(
                            "/api/auth/login",
                            json={
                                "username": "test@test.fr",
                                "password": "wrong",
                            },
                        )
                        assert last_resp.status_code == 429
                        retry_after = last_resp.headers.get("Retry-After")
                        assert retry_after is not None, "Missing Retry-After"
                        assert int(retry_after) > 0, "Retry-After must be positive"
                finally:
                    rl.login_limiter = orig_login
                    rl.global_limiter = orig_global
                    login_lim.close()
                    global_lim.close()
            finally:
                await redis.flushall()
                await redis.aclose()

        run_async(_run(n_requests))


# ---------------------------------------------------------------------------
# Property 2: Limitation globale des endpoints API
# ---------------------------------------------------------------------------

class TestGlobalRateLimit:
    """
    Property 2: Limitation globale des endpoints API

    **Validates: Requirements 3.1, 3.2**

    Pour toute adresse IP et pour tout endpoint sous /api, si le nombre de
    requêtes dépasse 60 dans une fenêtre de 60 secondes, les requêtes
    excédentaires doivent retourner un code HTTP 429.
    """

    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    @given(n_extra=st.integers(min_value=1, max_value=5))
    def test_global_rate_limit(self, n_extra: int):
        """
        Envoyer plus de 60 requêtes globales doit bloquer les excédentaires.

        **Validates: Requirements 3.1, 3.2**
        """

        async def _run(extra: int):
            redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                # No login limiter — only global
                global_rate = Rate(60, Duration.MINUTE)
                global_bucket = await RedisBucket.init(
                    [global_rate], redis, "prop2:global"
                )
                global_lim = Limiter(global_bucket)

                import app.utils.rate_limiter as rl

                orig_login, orig_global = rl.login_limiter, rl.global_limiter
                rl.login_limiter = None  # disable login limiter
                rl.global_limiter = global_lim

                try:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test",
                    ) as ac:
                        total = 60 + extra

                        # Use /api/auth/refresh — a simple GET endpoint
                        statuses = []
                        for _ in range(total):
                            resp = await ac.get("/api/auth/refresh")
                            statuses.append(resp.status_code)

                        # First 60 must NOT be 429
                        for i, s in enumerate(statuses[:60]):
                            assert s != 429, (
                                f"Request {i+1} should not be rate-limited, got {s}"
                            )

                        # Requests beyond 60 must be 429
                        for i, s in enumerate(statuses[60:], start=61):
                            assert s == 429, (
                                f"Request {i} should be 429, got {s}"
                            )
                finally:
                    rl.login_limiter = orig_login
                    rl.global_limiter = orig_global
                    global_lim.close()
            finally:
                await redis.flushall()
                await redis.aclose()

        run_async(_run(n_extra))


# ---------------------------------------------------------------------------
# Property 3: Priorité des limites spécifiques sur la limite globale
# ---------------------------------------------------------------------------

class TestSpecificLimitPriority:
    """
    Property 3: Priorité des limites spécifiques sur la limite globale

    **Validates: Requirement 3.3**

    Un client atteignant la limite spécifique de login (5 req/60s) doit être
    bloqué sur login même s'il n'a pas atteint la limite globale (60 req/60s).
    """

    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    @given(n_requests=st.integers(min_value=6, max_value=10))
    def test_specific_limit_priority(self, n_requests: int):
        """
        Le login est bloqué à 5 req même si la limite globale (60) n'est pas atteinte.

        **Validates: Requirement 3.3**
        """

        async def _run(n: int):
            redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                login_rate = Rate(5, Duration.MINUTE)
                login_bucket = await RedisBucket.init(
                    [login_rate], redis, "prop3:login"
                )
                login_lim = Limiter(login_bucket)

                global_rate = Rate(60, Duration.MINUTE)
                global_bucket = await RedisBucket.init(
                    [global_rate], redis, "prop3:global"
                )
                global_lim = Limiter(global_bucket)

                import app.utils.rate_limiter as rl

                orig_login, orig_global = rl.login_limiter, rl.global_limiter
                rl.login_limiter = login_lim
                rl.global_limiter = global_lim

                try:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test",
                    ) as ac:
                        # Send n login requests (n > 5)
                        login_statuses = []
                        for _ in range(n):
                            resp = await ac.post(
                                "/api/auth/login",
                                json={
                                    "username": "test@test.fr",
                                    "password": "wrong",
                                },
                            )
                            login_statuses.append(resp.status_code)

                        # Login should be blocked after 5
                        assert login_statuses[5] == 429, (
                            f"6th login request should be 429, got {login_statuses[5]}"
                        )

                        # But a non-login endpoint should still work
                        # (global limit not reached — only ~n requests total)
                        resp = await ac.get("/api/auth/refresh")
                        assert resp.status_code != 429, (
                            "Non-login endpoint should not be rate-limited yet"
                        )
                finally:
                    rl.login_limiter = orig_login
                    rl.global_limiter = orig_global
                    login_lim.close()
                    global_lim.close()
            finally:
                await redis.flushall()
                await redis.aclose()

        run_async(_run(n_requests))


# ---------------------------------------------------------------------------
# Property 4: Format de la réponse 429
# ---------------------------------------------------------------------------

class TestResponseFormat429:
    """
    Property 4: Format de la réponse 429

    **Validates: Requirements 4.1, 4.2**

    Pour toute requête rejetée par le rate limiter, la réponse HTTP 429 doit
    contenir un corps JSON avec un champ `detail` non vide, et les en-têtes
    X-RateLimit-Limit, X-RateLimit-Remaining et X-RateLimit-Reset doivent
    être présents avec des valeurs numériques.
    """

    @settings(max_examples=100, deadline=2000, suppress_health_check=[HealthCheck.too_slow])
    @given(n_extra=st.integers(min_value=1, max_value=5))
    def test_429_response_format(self, n_extra: int):
        """
        Toute réponse 429 doit avoir le bon format JSON et les bons en-têtes.

        **Validates: Requirements 4.1, 4.2**
        """

        async def _run(extra: int):
            redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                login_rate = Rate(5, Duration.MINUTE)
                login_bucket = await RedisBucket.init(
                    [login_rate], redis, "prop4:login"
                )
                login_lim = Limiter(login_bucket)

                global_rate = Rate(60, Duration.MINUTE)
                global_bucket = await RedisBucket.init(
                    [global_rate], redis, "prop4:global"
                )
                global_lim = Limiter(global_bucket)

                import app.utils.rate_limiter as rl

                orig_login, orig_global = rl.login_limiter, rl.global_limiter
                rl.login_limiter = login_lim
                rl.global_limiter = global_lim

                try:
                    async with AsyncClient(
                        transport=ASGITransport(app=app),
                        base_url="http://test",
                    ) as ac:
                        # Exhaust login limit (5 requests)
                        for _ in range(5):
                            await ac.post(
                                "/api/auth/login",
                                json={
                                    "username": "test@test.fr",
                                    "password": "wrong",
                                },
                            )

                        # Now send extra requests that should all be 429
                        for _ in range(extra):
                            resp = await ac.post(
                                "/api/auth/login",
                                json={
                                    "username": "test@test.fr",
                                    "password": "wrong",
                                },
                            )
                            assert resp.status_code == 429

                            # Check JSON body
                            body = resp.json()
                            assert "detail" in body, "Missing 'detail' in 429 body"
                            assert len(body["detail"]) > 0, "'detail' must be non-empty"

                            # Check required headers
                            assert "Retry-After" in resp.headers, "Missing Retry-After"
                            assert "X-RateLimit-Limit" in resp.headers, (
                                "Missing X-RateLimit-Limit"
                            )
                            assert "X-RateLimit-Remaining" in resp.headers, (
                                "Missing X-RateLimit-Remaining"
                            )
                            assert "X-RateLimit-Reset" in resp.headers, (
                                "Missing X-RateLimit-Reset"
                            )

                            # All header values must be numeric
                            assert resp.headers["Retry-After"].isdigit(), (
                                "Retry-After must be numeric"
                            )
                            assert resp.headers["X-RateLimit-Limit"].isdigit(), (
                                "X-RateLimit-Limit must be numeric"
                            )
                            assert resp.headers["X-RateLimit-Remaining"].isdigit(), (
                                "X-RateLimit-Remaining must be numeric"
                            )
                            assert resp.headers["X-RateLimit-Reset"].isdigit(), (
                                "X-RateLimit-Reset must be numeric"
                            )
                finally:
                    rl.login_limiter = orig_login
                    rl.global_limiter = orig_global
                    login_lim.close()
                    global_lim.close()
            finally:
                await redis.flushall()
                await redis.aclose()

        run_async(_run(n_extra))


# ---------------------------------------------------------------------------
# 6.6 Unit tests: mode dégradé et résilience
# ---------------------------------------------------------------------------

class TestDegradedModeAndResilience:
    """
    Tests unitaires pour le mode dégradé et la résilience.

    **Validates: Requirements 1.3, 5.1, 5.2, 5.3, 6.3**
    """

    def test_init_returns_false_when_valkey_down(self):
        """
        init_rate_limiter retourne False quand Valkey est indisponible.

        **Validates: Requirement 1.3**
        """

        async def _run():
            with patch(
                "app.utils.rate_limiter.aioredis.from_url",
                side_effect=ConnectionError("Connection refused"),
            ):
                import app.utils.rate_limiter as rl

                orig_login, orig_global, orig_redis = (
                    rl.login_limiter,
                    rl.global_limiter,
                    rl._redis_client,
                )
                try:
                    result = await init_rate_limiter()
                    assert result is False, "Should return False when Valkey is down"
                    assert rl.global_limiter is None
                    assert rl.login_limiter is None
                finally:
                    rl.login_limiter = orig_login
                    rl.global_limiter = orig_global
                    rl._redis_client = orig_redis

        run_async(_run())

    def test_degraded_mode_skips_rate_limiting(self):
        """
        En mode dégradé (limiters = None), les requêtes passent sans limitation.

        **Validates: Requirements 1.3, 5.1**
        """

        async def _run():
            import app.utils.rate_limiter as rl

            orig_login, orig_global = rl.login_limiter, rl.global_limiter
            rl.login_limiter = None
            rl.global_limiter = None

            try:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    # Send 10 login requests — none should be 429
                    for i in range(10):
                        resp = await ac.post(
                            "/api/auth/login",
                            json={"username": "test@test.fr", "password": "wrong"},
                        )
                        assert resp.status_code != 429, (
                            f"Request {i+1} should not be rate-limited in degraded mode"
                        )
            finally:
                rl.login_limiter = orig_login
                rl.global_limiter = orig_global

        run_async(_run())

    def test_valkey_failure_during_execution_failopen(self):
        """
        Si Valkey tombe en cours d'exécution, les requêtes passent (fail-open).

        **Validates: Requirements 5.1, 5.2**
        """

        async def _run():
            import app.utils.rate_limiter as rl
            from redis.exceptions import RedisError

            # Create a limiter that raises RedisError on try_acquire_async
            broken_limiter = MagicMock(spec=Limiter)
            broken_limiter.try_acquire_async = AsyncMock(
                side_effect=RedisError("Connection lost")
            )

            orig_login, orig_global = rl.login_limiter, rl.global_limiter
            rl.login_limiter = None
            rl.global_limiter = broken_limiter

            try:
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    resp = await ac.get("/api/auth/refresh")
                    # Should NOT be 429 — fail-open
                    assert resp.status_code != 429, (
                        "Should fail-open when Valkey is down"
                    )
            finally:
                rl.login_limiter = orig_login
                rl.global_limiter = orig_global

        run_async(_run())

    def test_valkey_recovery_resumes_rate_limiting(self):
        """
        Quand Valkey redevient disponible, le rate limiting reprend.

        **Validates: Requirement 5.3**
        """

        async def _run():
            import app.utils.rate_limiter as rl
            from redis.exceptions import RedisError

            redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                # Phase 1: broken limiter (fail-open)
                broken_limiter = MagicMock(spec=Limiter)
                broken_limiter.try_acquire_async = AsyncMock(
                    side_effect=RedisError("Connection lost")
                )

                orig_login, orig_global = rl.login_limiter, rl.global_limiter
                rl.login_limiter = None
                rl.global_limiter = broken_limiter

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    resp = await ac.get("/api/auth/refresh")
                    assert resp.status_code != 429, "Should fail-open"

                # Phase 2: restore working limiter
                login_rate = Rate(5, Duration.MINUTE)
                login_bucket = await RedisBucket.init(
                    [login_rate], redis, "recovery:login"
                )
                login_lim = Limiter(login_bucket)

                global_rate = Rate(60, Duration.MINUTE)
                global_bucket = await RedisBucket.init(
                    [global_rate], redis, "recovery:global"
                )
                global_lim = Limiter(global_bucket)

                rl.login_limiter = login_lim
                rl.global_limiter = global_lim

                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    # Exhaust login limit
                    for _ in range(5):
                        await ac.post(
                            "/api/auth/login",
                            json={"username": "test@test.fr", "password": "wrong"},
                        )

                    # 6th should be blocked
                    resp = await ac.post(
                        "/api/auth/login",
                        json={"username": "test@test.fr", "password": "wrong"},
                    )
                    assert resp.status_code == 429, (
                        "Rate limiting should resume after Valkey recovery"
                    )

                login_lim.close()
                global_lim.close()
                rl.login_limiter = orig_login
                rl.global_limiter = orig_global
            finally:
                await redis.flushall()
                await redis.aclose()

        run_async(_run())

    def test_unknown_ip_fallback(self):
        """
        Quand request.client est None, custom_identifier retourne 'unknown'.

        **Validates: Requirement 6.3**
        """
        request = _make_request(headers={}, client_host=None)
        result = run_async(custom_identifier(request))
        assert result == "unknown"

    def test_unknown_ip_logs_warning(self, caplog):
        """
        Quand l'IP ne peut être déterminée, un avertissement est journalisé.

        **Validates: Requirement 6.3**
        """
        request = _make_request(headers={}, client_host=None)
        with caplog.at_level(logging.WARNING, logger="CMV_GATEWAY"):
            run_async(custom_identifier(request))
        assert any("IP" in record.message for record in caplog.records), (
            "Should log a warning about unknown IP"
        )
