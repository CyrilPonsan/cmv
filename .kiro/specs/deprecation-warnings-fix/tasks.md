# Plan d'Implémentation — Correction des Avertissements de Dépréciation

- [x] 1. Écrire le test exploratoire de la condition de bug
  - **Property 1: Bug Condition** — Warnings de dépréciation SQLAlchemy et passlib
  - **IMPORTANT** : Écrire ce test basé sur les propriétés AVANT d'implémenter la correction
  - **CRITIQUE** : Ce test DOIT ÉCHOUER sur le code non corrigé — l'échec confirme que le bug existe
  - **NE PAS tenter de corriger le test ou le code quand il échoue**
  - **NOTE** : Ce test encode le comportement attendu — il validera la correction quand il passera après implémentation
  - **OBJECTIF** : Mettre en évidence des contre-exemples démontrant l'existence du bug
  - **Approche PBT ciblée** : Pour ce bug déterministe, cibler les cas concrets d'échec
  - Créer un fichier de test `tests/test_deprecation_warnings.py` à la racine du projet
  - Test 1 — SQLAlchemy : Importer chaque `database.py` des 4 services (cmv_patients, cmv_chambres, cmv_gateway/cmv_back, cmv_ml) avec `warnings.catch_warnings(record=True)` et vérifier qu'AUCUN `MovedIn20Warning` n'est émis (condition de bug : `from sqlalchemy.ext.declarative import declarative_base`)
  - Test 2 — passlib/crypt : Importer les modules auth de cmv_gateway (`app.dependancies.auth`, `app.routers.auth`, `app.repositories.user_crud`) et vérifier qu'AUCUN `DeprecationWarning` lié à `crypt` n'est émis (condition de bug : `from passlib.context import CryptContext`)
  - Exécuter les tests sur le code NON CORRIGÉ
  - **RÉSULTAT ATTENDU** : Les tests ÉCHOUENT (c'est correct — cela prouve que le bug existe)
  - Documenter les contre-exemples trouvés (ex: `MovedIn20Warning` émis lors de l'import de `cmv_patients/app/utils/database.py`)
  - Marquer la tâche comme terminée quand le test est écrit, exécuté, et l'échec documenté
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3_

- [x] 2. Écrire les tests de préservation basés sur les propriétés (AVANT d'implémenter la correction)
  - **Property 2: Preservation** — Compatibilité ORM et hachage bcrypt
  - **IMPORTANT** : Suivre la méthodologie observation-first
  - **Approche observation-first** :
    1. Exécuter le code NON CORRIGÉ avec des entrées non affectées par le bug (cas où `isBugCondition` retourne false)
    2. Observer et enregistrer les sorties réelles
    3. Écrire des tests PBT qui assertent ces comportements observés sur le domaine d'entrée
    4. Vérifier que les tests PASSENT sur le code NON CORRIGÉ avant d'implémenter la correction
  - Créer un fichier de test `tests/test_preservation.py` à la racine du projet
  - Observer : `pwd_context.verify("Abcdef@123456", pwd_context.hash("Abcdef@123456"))` retourne `True` sur le code non corrigé
  - Observer : `pwd_context.hash("test")` produit un hash commençant par `$2b$` de 60 caractères sur le code non corrigé
  - Observer : Les modèles SQLAlchemy héritant de `Base` se définissent correctement, `Base.metadata` est accessible
  - Test PBT 1 — Préservation hachage : Pour tout mot de passe aléatoire (stratégie Hypothesis : `text(min_size=1, max_size=72)`), vérifier que `bcrypt.checkpw(password, bcrypt.hashpw(password))` retourne True ET que le hash commence par `$2b$` ET fait 60 caractères (depuis Preservation Requirements — Exigence 3.4)
  - Test PBT 2 — Rejet mot de passe incorrect : Pour toute paire (mot_de_passe, mauvais_mot_de_passe) où ils diffèrent, vérifier que `bcrypt.checkpw(mauvais_mot_de_passe, hash)` retourne False
  - Test PBT 3 — Compatibilité passlib→bcrypt : Hacher avec `pwd_context.hash()` (code non corrigé) et vérifier que `bcrypt.checkpw()` valide le même mot de passe — confirme la rétrocompatibilité des hachages existants
  - Exécuter les tests sur le code NON CORRIGÉ
  - **RÉSULTAT ATTENDU** : Les tests PASSENT (cela confirme le comportement de base à préserver)
  - Marquer la tâche comme terminée quand les tests sont écrits, exécutés, et passent sur le code non corrigé
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Correction des avertissements de dépréciation

  - [x] 3.1 Migrer les 4 fichiers `database.py` de `declarative_base()` vers `DeclarativeBase`
    - Remplacer dans `cmv_patients/app/utils/database.py` : supprimer `from sqlalchemy.ext.declarative import declarative_base` et `Base = declarative_base()`, ajouter `from sqlalchemy.orm import DeclarativeBase` et `class Base(DeclarativeBase): pass`
    - Remplacer dans `cmv_chambres/app/utils/database.py` : même transformation
    - Remplacer dans `cmv_gateway/cmv_back/app/utils/database.py` : même transformation
    - Remplacer dans `cmv_ml/app/utils/database.py` : même transformation
    - Conserver `metadata = Base.metadata` dans chaque fichier (compatibilité Alembic `env.py`)
    - Conserver `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)` inchangé
    - _Bug_Condition: isBugCondition_SQLAlchemy(X) où X.contient_import("sqlalchemy.ext.declarative", "declarative_base")_
    - _Expected_Behavior: Aucun MovedIn20Warning émis, Base reste fonctionnel pour l'héritage de modèles_
    - _Preservation: Les modèles ORM, SessionLocal, metadata, et migrations Alembic continuent de fonctionner identiquement_
    - _Requirements: 1.1, 2.1, 2.3, 3.1, 3.2, 3.3, 3.5_

  - [x] 3.2 Remplacer passlib par bcrypt direct dans `cmv_gateway/cmv_back/app/dependancies/auth.py`
    - Supprimer `from passlib.context import CryptContext` et `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
    - Ajouter `import bcrypt`
    - Modifier `verify_password()` : utiliser `bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))`
    - _Bug_Condition: isBugCondition_Passlib(X) où X.contient_import("passlib.context", "CryptContext")_
    - _Expected_Behavior: Aucun DeprecationWarning lié à crypt, verify_password() fonctionne identiquement_
    - _Preservation: Les hachages bcrypt existants ($2b$...) restent vérifiables_
    - _Requirements: 1.2, 2.2, 2.3, 3.4_

  - [x] 3.3 Supprimer passlib inutilisé dans `cmv_gateway/cmv_back/app/repositories/user_crud.py`
    - Supprimer `from passlib.context import CryptContext` et `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
    - Supprimer `pwd_context = CryptContext` dans la classe `PgUserRepository`
    - Ce fichier n'utilise pas `pwd_context` pour hash/verify — import inutile
    - _Bug_Condition: isBugCondition_Passlib(X) — import passlib non utilisé_
    - _Requirements: 1.2, 2.2_

  - [x] 3.4 Supprimer passlib inutilisé dans `cmv_gateway/cmv_back/app/routers/auth.py`
    - Supprimer `from passlib.context import CryptContext` et `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
    - Ce fichier n'utilise pas `pwd_context` — le hachage est délégué au service d'authentification
    - _Bug_Condition: isBugCondition_Passlib(X) — import passlib non utilisé_
    - _Requirements: 1.2, 2.2_

  - [x] 3.5 Remplacer passlib par bcrypt direct dans les scripts de fixtures
    - `cmv_gateway/cmv_back/fixtures.py` : remplacer `pwd_context = CryptContext(...)` et `pwd_context.hash(...)` par `import bcrypt` et `bcrypt.hashpw("...".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")`
    - `cmv_gateway/cmv_back/create_fixtures.py` : même transformation
    - `cmv_gateway/cmv_back/app/utils/fixtures.py` : même transformation
    - _Bug_Condition: isBugCondition_Passlib(X) — utilisation de CryptContext pour le hachage_
    - _Preservation: Les mots de passe hachés restent au format bcrypt $2b$ compatible_
    - _Requirements: 1.2, 2.2, 3.4_

  - [x] 3.6 Remplacer passlib par bcrypt direct dans `cmv_gateway/cmv_back/app/tests/conftest.py`
    - Supprimer `from passlib.context import CryptContext`
    - Dans la fixture `user` : remplacer `pwd_context = CryptContext(...)` et `pwd_context.hash(...)` par `import bcrypt` et `bcrypt.hashpw(...)` 
    - _Bug_Condition: isBugCondition_Passlib(X) — utilisation de CryptContext dans les tests_
    - _Requirements: 1.2, 2.2_

  - [x] 3.7 Supprimer l'import passlib inutilisé dans `cmv_patients/app/dependancies/auth.py`
    - Supprimer `from passlib.context import CryptContext` et `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
    - Ce fichier ne fait que de la vérification JWT — `pwd_context` n'est jamais utilisé dans les fonctions
    - _Bug_Condition: isBugCondition_Passlib(X) — import passlib non utilisé_
    - _Requirements: 1.2, 2.2_

  - [x] 3.8 Supprimer l'import passlib inutilisé dans `cmv_chambres/app/dependancies/auth.py`
    - Supprimer `from passlib.context import CryptContext` et `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
    - Ce fichier ne fait que de la vérification JWT — `pwd_context` n'est jamais utilisé dans les fonctions
    - _Bug_Condition: isBugCondition_Passlib(X) — import passlib non utilisé_
    - _Requirements: 1.2, 2.2_

  - [x] 3.9 Supprimer `passlib[bcrypt]==1.7.4` des 4 fichiers `requirements.txt`
    - `cmv_patients/requirements.txt` : supprimer la ligne `passlib[bcrypt]==1.7.4`
    - `cmv_chambres/requirements.txt` : supprimer la ligne `passlib[bcrypt]==1.7.4`
    - `cmv_gateway/cmv_back/requirements.txt` : supprimer la ligne `passlib[bcrypt]==1.7.4`
    - `cmv_ml/requirements.txt` : supprimer la ligne `passlib[bcrypt]==1.7.4`
    - La dépendance `bcrypt==4.1.3` est déjà présente dans chaque fichier
    - _Requirements: 2.2, 2.3_

  - [x] 3.10 Vérifier que le test exploratoire de la condition de bug passe maintenant
    - **Property 1: Expected Behavior** — Suppression des warnings de dépréciation
    - **IMPORTANT** : Ré-exécuter le MÊME test de la tâche 1 — NE PAS écrire un nouveau test
    - Le test de la tâche 1 encode le comportement attendu
    - Quand ce test passe, il confirme que le comportement attendu est satisfait
    - Exécuter le test exploratoire de la condition de bug de l'étape 1
    - **RÉSULTAT ATTENDU** : Le test PASSE (confirme que le bug est corrigé)
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.11 Vérifier que les tests de préservation passent toujours
    - **Property 2: Preservation** — Compatibilité ORM et hachage bcrypt
    - **IMPORTANT** : Ré-exécuter les MÊMES tests de la tâche 2 — NE PAS écrire de nouveaux tests
    - Exécuter les tests de préservation basés sur les propriétés de l'étape 2
    - **RÉSULTAT ATTENDU** : Les tests PASSENT (confirme l'absence de régressions)
    - Confirmer que tous les tests passent toujours après la correction (pas de régressions)

- [x] 4. Checkpoint — Vérifier que tous les tests passent
  - S'assurer que tous les tests passent, demander à l'utilisateur si des questions se posent.
