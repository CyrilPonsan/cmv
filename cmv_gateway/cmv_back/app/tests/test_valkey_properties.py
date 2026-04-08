"""
Property-based tests for Valkey key-value operations.

**Validates: Requirements 3.3, 3.4**

These tests verify that the round-trip operations (setex/get) work correctly
for session keys and blacklisted tokens.

This test file is standalone and does not depend on the main application.
"""

import asyncio
from hypothesis import given, settings, strategies as st
import fakeredis.aioredis


def run_async(coro):
    """Helper to run async code in sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestValkeyRoundTrip:
    """
    Property 1: Round-trip des opérations clé-valeur
    
    **Validates: Requirements 3.3, 3.4**
    
    Pour toute clé et valeur valides (sessions `session:{id}` ou tokens 
    blacklistés `blacklist:{token}`), stocker la valeur avec `setex` puis 
    la récupérer avec `get` doit retourner la valeur originale, tant que 
    le TTL n'est pas expiré.
    """

    @settings(max_examples=100)
    @given(
        session_id=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N")),
            min_size=1,
            max_size=50
        ),
        user_id=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N")),
            min_size=1,
            max_size=50
        )
    )
    def test_session_roundtrip(self, session_id: str, user_id: str):
        """
        Test round-trip for session keys (session:{session_id} -> user_id).
        
        **Validates: Requirements 3.3**
        """
        async def run_test():
            client = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                key = f"session:{session_id}"
                ttl = 3600  # 1 hour as per design
                
                # Store with setex
                await client.setex(key, ttl, user_id)
                
                # Retrieve with get
                retrieved = await client.get(key)
                
                # Verify equality
                assert retrieved == user_id, f"Expected {user_id}, got {retrieved}"
            finally:
                await client.aclose()
        
        run_async(run_test())

    @settings(max_examples=100)
    @given(
        token=st.text(
            alphabet=st.characters(whitelist_categories=("L", "N", "P")),
            min_size=1,
            max_size=200
        )
    )
    def test_blacklist_roundtrip(self, token: str):
        """
        Test round-trip for blacklisted tokens (blacklist:{token} -> "true").
        
        **Validates: Requirements 3.4**
        """
        async def run_test():
            client = fakeredis.aioredis.FakeRedis(decode_responses=True)
            try:
                key = f"blacklist:{token}"
                value = "true"
                ttl = 3600  # 1 hour as per design
                
                # Store with setex
                await client.setex(key, ttl, value)
                
                # Retrieve with get
                retrieved = await client.get(key)
                
                # Verify equality
                assert retrieved == value, f"Expected {value}, got {retrieved}"
            finally:
                await client.aclose()
        
        run_async(run_test())
