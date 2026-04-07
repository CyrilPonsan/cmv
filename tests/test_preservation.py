"""
Tests de préservation basés sur les propriétés — Compatibilité hachage bcrypt.

Ces tests encodent le comportement OBSERVÉ sur le code NON CORRIGÉ.
Ils DOIVENT PASSER avant ET après la correction — l'échec signalerait une régression.

Méthodologie observation-first :
- Observation : pwd_context.verify("Abcdef@123456", pwd_context.hash("Abcdef@123456")) → True
- Observation : pwd_context.hash("test") → hash $2b$ de 60 caractères
- Observation : Les modèles SQLAlchemy héritant de Base se définissent, Base.metadata accessible

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
"""

import bcrypt
from hypothesis import given, settings, assume
from hypothesis.strategies import text
from passlib.context import CryptContext

# Instance passlib identique à celle du code non corrigé (cmv_gateway auth.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Stratégie de mots de passe valides pour bcrypt : pas de NULL bytes
# bcrypt rejette les NULL bytes — c'est une contrainte connue du format, pas un bug
valid_password = text(
    min_size=1,
    max_size=72,
    alphabet=text(min_size=1, max_size=1).filter(lambda c: c != "\x00"),
)


class TestPreservationHachage:
    """PBT 1 — Préservation hachage : Pour tout mot de passe aléatoire,
    vérifier que bcrypt.checkpw(password, bcrypt.hashpw(password)) retourne True
    ET que le hash commence par $2b$ ET fait 60 caractères.

    **Validates: Requirements 3.4**
    """

    @given(password=valid_password)
    @settings(max_examples=50, deadline=None)
    def test_hash_then_check_roundtrip(self, password: str):
        """Pour tout mot de passe, hashpw suivi de checkpw retourne True,
        le hash commence par $2b$ et fait 60 caractères."""
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        # Le hash doit commencer par $2b$
        assert hashed.startswith(b"$2b$"), (
            f"Le hash ne commence pas par $2b$ : {hashed[:10]}"
        )

        # Le hash doit faire 60 caractères
        assert len(hashed) == 60, (
            f"Le hash fait {len(hashed)} caractères au lieu de 60"
        )

        # checkpw doit valider le mot de passe original
        assert bcrypt.checkpw(password_bytes, hashed), (
            f"bcrypt.checkpw a rejeté le mot de passe original après hashpw"
        )


class TestRejetMotDePasseIncorrect:
    """PBT 2 — Rejet mot de passe incorrect : Pour toute paire (password, wrong_password)
    où ils diffèrent, vérifier que bcrypt.checkpw(wrong_password, hash) retourne False.

    **Validates: Requirements 3.4**
    """

    @given(
        password=valid_password,
        wrong_password=valid_password,
    )
    @settings(max_examples=50, deadline=None)
    def test_wrong_password_rejected(self, password: str, wrong_password: str):
        """Pour toute paire de mots de passe différents, checkpw rejette le mauvais."""
        assume(password != wrong_password)

        password_bytes = password.encode("utf-8")
        wrong_bytes = wrong_password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        assert not bcrypt.checkpw(wrong_bytes, hashed), (
            f"bcrypt.checkpw a accepté un mauvais mot de passe"
        )


class TestCompatibilitePasslibBcrypt:
    """PBT 3 — Compatibilité passlib→bcrypt : Hacher avec pwd_context.hash()
    (code non corrigé) et vérifier que bcrypt.checkpw() valide le même mot de passe.
    Confirme la rétrocompatibilité des hachages existants.

    **Validates: Requirements 3.4, 3.5**
    """

    @given(password=valid_password)
    @settings(max_examples=50, deadline=None)
    def test_passlib_hash_verified_by_bcrypt(self, password: str):
        """Un hash produit par passlib pwd_context.hash() doit être vérifiable
        par bcrypt.checkpw() — garantit la compatibilité descendante."""
        # Hash avec passlib (code non corrigé)
        passlib_hash = pwd_context.hash(password)

        # Le hash passlib doit être au format bcrypt
        assert passlib_hash.startswith("$2b$"), (
            f"Le hash passlib ne commence pas par $2b$ : {passlib_hash[:10]}"
        )
        assert len(passlib_hash) == 60, (
            f"Le hash passlib fait {len(passlib_hash)} caractères au lieu de 60"
        )

        # bcrypt direct doit pouvoir vérifier le hash passlib
        assert bcrypt.checkpw(
            password.encode("utf-8"),
            passlib_hash.encode("utf-8"),
        ), (
            f"bcrypt.checkpw a rejeté un hash produit par passlib pour le même mot de passe"
        )
