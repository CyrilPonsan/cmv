"""
Test exploratoire de la condition de bug — Avertissements de dépréciation.

Ce test encode le COMPORTEMENT ATTENDU (aucun warning de dépréciation).
Sur le code NON CORRIGÉ, ces tests DOIVENT ÉCHOUER — l'échec confirme le bug.

**Validates: Requirements 1.1, 1.2, 2.1, 2.2, 2.3**
"""

import importlib
import sys
import warnings


class TestSQLAlchemyDeprecationWarnings:
    """Test 1 — Vérifier qu'aucun MovedIn20Warning n'est émis lors de l'import
    des modules database.py des 4 services.

    Bug condition: `from sqlalchemy.ext.declarative import declarative_base`
    produit un MovedIn20Warning sur SQLAlchemy 2.0+.
    """

    # Paths to the 4 database.py modules (as dotted import paths)
    DATABASE_MODULES = [
        ("cmv_patients", "cmv_patients.app.utils.database"),
        ("cmv_chambres", "cmv_chambres.app.utils.database"),
        ("cmv_gateway", "cmv_gateway.cmv_back.app.utils.database"),
        ("cmv_ml", "cmv_ml.app.utils.database"),
    ]

    def _check_source_for_deprecated_import(self, service_name: str, module_path: str):
        """Read the source file and check if it uses the deprecated import path.

        This avoids needing to actually import the module (which requires
        env vars, DB connections, etc.) while still detecting the bug condition.
        """
        # Convert dotted module path to file path
        file_path = module_path.replace(".", "/") + ".py"

        with open(file_path, "r") as f:
            source = f.read()

        # The bug condition: importing from the deprecated path
        has_deprecated_import = "sqlalchemy.ext.declarative" in source

        assert not has_deprecated_import, (
            f"[{service_name}] database.py contient l'import déprécié "
            f"'from sqlalchemy.ext.declarative import declarative_base'. "
            f"Devrait utiliser 'from sqlalchemy.orm import DeclarativeBase' à la place."
        )

    def _check_import_emits_no_warning(self):
        """Verify that importing declarative_base from the path used in the
        codebase does not emit MovedIn20Warning."""
        # Force re-import to capture warnings
        modules_to_remove = [
            k for k in sys.modules
            if "sqlalchemy.ext.declarative" in k
        ]
        for mod in modules_to_remove:
            del sys.modules[mod]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            # This is the exact import used in the codebase
            from sqlalchemy.ext.declarative import declarative_base  # noqa: F401

        moved_warnings = [
            w for w in caught
            if "MovedIn20Warning" in type(w.category).__name__
            or "declarative_base" in str(w.message)
        ]

        assert len(moved_warnings) == 0, (
            f"L'import 'from sqlalchemy.ext.declarative import declarative_base' "
            f"a émis {len(moved_warnings)} MovedIn20Warning(s): "
            f"{[str(w.message) for w in moved_warnings]}"
        )

    def test_no_deprecated_sqlalchemy_import_cmv_patients(self):
        """cmv_patients/app/utils/database.py ne doit pas utiliser l'import déprécié."""
        self._check_source_for_deprecated_import(
            "cmv_patients", "cmv_patients.app.utils.database"
        )

    def test_no_deprecated_sqlalchemy_import_cmv_chambres(self):
        """cmv_chambres/app/utils/database.py ne doit pas utiliser l'import déprécié."""
        self._check_source_for_deprecated_import(
            "cmv_chambres", "cmv_chambres.app.utils.database"
        )

    def test_no_deprecated_sqlalchemy_import_cmv_gateway(self):
        """cmv_gateway/cmv_back/app/utils/database.py ne doit pas utiliser l'import déprécié."""
        self._check_source_for_deprecated_import(
            "cmv_gateway", "cmv_gateway.cmv_back.app.utils.database"
        )

    def test_no_deprecated_sqlalchemy_import_cmv_ml(self):
        """cmv_ml/app/utils/database.py ne doit pas utiliser l'import déprécié."""
        self._check_source_for_deprecated_import(
            "cmv_ml", "cmv_ml.app.utils.database"
        )

    def test_declarative_base_import_emits_no_warning(self):
        """L'import de declarative_base ne doit émettre aucun MovedIn20Warning."""
        self._check_import_emits_no_warning()


class TestPasslibCryptDeprecationWarnings:
    """Test 2 — Vérifier qu'aucun DeprecationWarning lié à 'crypt' n'est émis
    lors de l'import des modules auth de cmv_gateway.

    Bug condition: `from passlib.context import CryptContext` charge en interne
    le module `crypt` de Python, déprécié depuis Python 3.11.
    """

    GATEWAY_AUTH_MODULES = [
        ("dependancies.auth", "cmv_gateway/cmv_back/app/dependancies/auth.py"),
        ("routers.auth", "cmv_gateway/cmv_back/app/routers/auth.py"),
        ("repositories.user_crud", "cmv_gateway/cmv_back/app/repositories/user_crud.py"),
    ]

    def _check_source_for_passlib_import(self, module_name: str, file_path: str):
        """Read the source file and check if it uses passlib CryptContext."""
        with open(file_path, "r") as f:
            source = f.read()

        has_passlib_import = "from passlib.context import CryptContext" in source

        assert not has_passlib_import, (
            f"[{module_name}] contient l'import déprécié "
            f"'from passlib.context import CryptContext'. "
            f"Devrait utiliser 'import bcrypt' directement à la place."
        )

    def _check_passlib_import_emits_no_crypt_warning(self):
        """Verify that passlib is no longer available (removed from requirements)
        OR if still installed, that importing it does not emit a
        DeprecationWarning related to the crypt module.

        The fix removes passlib from the project entirely — if passlib is not
        installed, the test passes because no crypt warning can be emitted.
        """
        try:
            # Force re-import to capture warnings
            modules_to_remove = [
                k for k in sys.modules
                if "passlib" in k or k == "crypt"
            ]
            for mod in modules_to_remove:
                del sys.modules[mod]

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                from passlib.context import CryptContext  # noqa: F401
        except ModuleNotFoundError:
            # passlib is not installed — this IS the fix.
            # No passlib means no crypt deprecation warning.
            return

        crypt_warnings = [
            w for w in caught
            if issubclass(w.category, DeprecationWarning)
            and "crypt" in str(w.message).lower()
        ]

        assert len(crypt_warnings) == 0, (
            f"L'import de passlib.context.CryptContext a émis "
            f"{len(crypt_warnings)} DeprecationWarning(s) liés à 'crypt': "
            f"{[str(w.message) for w in crypt_warnings]}"
        )

    def test_no_passlib_import_in_gateway_auth(self):
        """cmv_gateway dependancies/auth.py ne doit pas importer passlib."""
        self._check_source_for_passlib_import(
            "dependancies.auth",
            "cmv_gateway/cmv_back/app/dependancies/auth.py",
        )

    def test_no_passlib_import_in_gateway_routers_auth(self):
        """cmv_gateway routers/auth.py ne doit pas importer passlib."""
        self._check_source_for_passlib_import(
            "routers.auth",
            "cmv_gateway/cmv_back/app/routers/auth.py",
        )

    def test_no_passlib_import_in_gateway_user_crud(self):
        """cmv_gateway repositories/user_crud.py ne doit pas importer passlib."""
        self._check_source_for_passlib_import(
            "repositories.user_crud",
            "cmv_gateway/cmv_back/app/repositories/user_crud.py",
        )

    def test_passlib_import_emits_no_crypt_warning(self):
        """L'import de passlib ne doit émettre aucun DeprecationWarning lié à crypt."""
        self._check_passlib_import_emits_no_crypt_warning()
