# Correction des Avertissements de Dépréciation — Design

## Vue d'ensemble

Ce document formalise la correction de deux avertissements de dépréciation présents dans les 4 services du projet (cmv_patients, cmv_chambres, cmv_gateway/cmv_back, cmv_ml) :

1. **SQLAlchemy `declarative_base()`** — Migration de l'import déprécié `sqlalchemy.ext.declarative.declarative_base` vers l'approche moderne SQLAlchemy 2.0 utilisant une classe `DeclarativeBase`.
2. **passlib / module `crypt`** — Remplacement de `passlib.context.CryptContext` par l'utilisation directe de la bibliothèque `bcrypt` pour le hachage et la vérification des mots de passe.

La stratégie est de faire des changements minimaux et ciblés dans chaque `database.py` et chaque module d'authentification, tout en préservant la compatibilité avec les modèles ORM existants, les migrations Alembic, et les hachages bcrypt déjà stockés en base de données.

## Glossaire

- **Bug_Condition (C)** : La condition qui déclenche le bug — l'import de `declarative_base` depuis le chemin déprécié, ou l'utilisation de `passlib` qui charge le module `crypt` déprécié
- **Property (P)** : Le comportement attendu — aucun warning de dépréciation lors de l'exécution des tests ou en production
- **Preservation** : Les comportements existants qui doivent rester inchangés — définition de modèles ORM via `Base`, sessions de BDD, migrations Alembic, hachage/vérification de mots de passe bcrypt
- **`Base`** : La classe de base déclarative dans `app/utils/database.py` dont héritent tous les modèles SQLAlchemy
- **`metadata`** : L'objet `MetaData` exposé par `database.py`, utilisé par Alembic (`env.py`) via `models.Base.metadata`
- **`pwd_context`** : L'instance `CryptContext` de passlib utilisée pour `hash()` et `verify()` des mots de passe
- **`DeclarativeBase`** : La nouvelle classe de base SQLAlchemy 2.0 (`from sqlalchemy.orm import DeclarativeBase`) qui remplace `declarative_base()`

## Détails du Bug

### Condition de Bug

Le bug se manifeste sous deux formes indépendantes :

**Bug 1 — SQLAlchemy** : Chaque fichier `database.py` des 4 services importe `declarative_base` depuis `sqlalchemy.ext.declarative`, un chemin déprécié depuis SQLAlchemy 2.0. Cela produit un `MovedIn20Warning` à chaque import.

**Bug 2 — passlib/crypt** : Les modules d'authentification de 3 services (cmv_gateway, cmv_patients, cmv_chambres) et les scripts de fixtures utilisent `passlib.context.CryptContext`, qui charge en interne le module `crypt` de Python, déprécié depuis Python 3.11.

**Spécification formelle :**

```
FUNCTION isBugCondition(X)
  INPUT: X de type ModuleImport (un fichier Python du projet)
  OUTPUT: boolean

  // Bug SQLAlchemy : import depuis le chemin déprécié
  condition_sqlalchemy := X.contient_import("sqlalchemy.ext.declarative", "declarative_base")

  // Bug passlib : utilisation de CryptContext qui charge le module crypt
  condition_passlib := X.contient_import("passlib.context", "CryptContext")

  RETURN condition_sqlalchemy OR condition_passlib
END FUNCTION
```

### Exemples

- **cmv_gateway/cmv_back/app/utils/database.py** : `from sqlalchemy.ext.declarative import declarative_base` → produit `MovedIn20Warning`
- **cmv_patients/app/utils/database.py** : même import déprécié → même warning
- **cmv_chambres/app/utils/database.py** : même import déprécié → même warning
- **cmv_ml/app/utils/database.py** : même import déprécié → même warning
- **cmv_gateway/cmv_back/app/dependancies/auth.py** : `from passlib.context import CryptContext` → produit `DeprecationWarning: 'crypt' is deprecated`
- **cmv_gateway/cmv_back/app/routers/auth.py** : même usage passlib → même warning
- **cmv_gateway/cmv_back/app/repositories/user_crud.py** : même usage passlib → même warning
- **cmv_patients/app/dependancies/auth.py** : même usage passlib → même warning
- **cmv_chambres/app/dependancies/auth.py** : même usage passlib → même warning
- **Cas limite** : cmv_ml n'utilise pas passlib dans son code applicatif (seulement installé comme dépendance) — seul le bug SQLAlchemy s'applique

## Comportement Attendu

### Exigences de Préservation

**Comportements inchangés :**
- Les modèles SQLAlchemy définis avec `class MonModele(Base):` doivent continuer à fonctionner normalement (CRUD, relations, mapped_column)
- `SessionLocal` doit continuer à fournir des sessions avec `autocommit=False` et `autoflush=False`
- `metadata` (alias `Base.metadata`) doit rester accessible pour les migrations Alembic — les fichiers `env.py` accèdent `models.Base.metadata`
- Les hachages bcrypt existants en base de données doivent rester vérifiables avec la nouvelle implémentation
- Les fonctions `verify_password()` et `hash()` doivent produire des résultats identiques (format bcrypt `$2b$...`)
- Les migrations Alembic existantes et futures doivent fonctionner sans modification des fichiers `env.py`
- Les scripts de fixtures (`fixtures.py`, `create_fixtures.py`) doivent continuer à hacher les mots de passe correctement

**Portée :**
Tous les fichiers qui n'importent pas `declarative_base` depuis le chemin déprécié et qui n'utilisent pas `passlib` ne sont pas affectés par cette correction. Cela inclut :
- Les routeurs, schémas Pydantic, et middlewares
- Les fichiers de configuration
- Le frontend (cmv_front)
- Les tests qui n'instancient pas directement `CryptContext`

## Cause Racine Hypothétisée

Basé sur l'analyse du code, les causes sont clairement identifiées :

1. **Import SQLAlchemy déprécié** : Les 4 fichiers `database.py` utilisent `from sqlalchemy.ext.declarative import declarative_base`. Ce chemin d'import a été déprécié dans SQLAlchemy 1.4 et déplacé vers `sqlalchemy.orm`. Le projet utilise déjà SQLAlchemy 2.0.x, donc l'approche moderne avec `DeclarativeBase` est disponible.

2. **passlib non maintenu** : `passlib==1.7.4` n'est plus activement maintenu et utilise en interne le module `crypt` de la bibliothèque standard Python, déprécié depuis Python 3.11 (PEP 594). La bibliothèque `bcrypt` est déjà présente dans les `requirements.txt` de chaque service (version 4.1.3), donc le remplacement est direct.

3. **Duplication de `pwd_context`** : Dans cmv_gateway, `CryptContext` est instancié dans 7 fichiers différents (auth.py, user_crud.py, routers/auth.py, fixtures.py, create_fixtures.py, conftest.py, utils/fixtures.py). Chaque instance doit être remplacée.

## Propriétés de Correction

Property 1: Bug Condition - Suppression des warnings de dépréciation

_Pour tout_ fichier `database.py` qui importait `declarative_base` depuis `sqlalchemy.ext.declarative`, le fichier corrigé SHALL utiliser une classe héritant de `DeclarativeBase` (import depuis `sqlalchemy.orm`) et ne produire aucun `MovedIn20Warning`.

**Valide : Exigences 2.1, 2.3**

Property 2: Bug Condition - Suppression des warnings passlib/crypt

_Pour tout_ module qui utilisait `passlib.context.CryptContext` pour le hachage de mots de passe, le module corrigé SHALL utiliser directement la bibliothèque `bcrypt` et ne produire aucun `DeprecationWarning` lié au module `crypt`.

**Valide : Exigences 2.2, 2.3**

Property 3: Preservation - Compatibilité des modèles ORM et migrations

_Pour tout_ modèle SQLAlchemy héritant de `Base` et toute migration Alembic utilisant `Base.metadata`, le code corrigé SHALL produire exactement le même comportement que le code original : les modèles se définissent, les sessions fonctionnent, et les migrations s'exécutent correctement.

**Valide : Exigences 3.1, 3.2, 3.3, 3.5**

Property 4: Preservation - Compatibilité des hachages bcrypt

_Pour tout_ mot de passe haché avec l'ancienne implémentation passlib (format `$2b$...`), la nouvelle implémentation bcrypt directe SHALL vérifier correctement ces hachages existants ET produire de nouveaux hachages dans le même format bcrypt compatible.

**Valide : Exigence 3.4**

## Implémentation de la Correction

### Changements Requis

En supposant que notre analyse de cause racine est correcte :

**Changement 1 : Migration `database.py` — 4 fichiers**

Fichiers : `cmv_patients/app/utils/database.py`, `cmv_chambres/app/utils/database.py`, `cmv_gateway/cmv_back/app/utils/database.py`, `cmv_ml/app/utils/database.py`

Remplacer :
```python
from sqlalchemy.ext.declarative import declarative_base
# ...
Base = declarative_base()
metadata = Base.metadata
```

Par :
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

metadata = Base.metadata
```

- `Base` reste une classe utilisable comme parent pour les modèles (`class MonModele(Base):`)
- `Base.metadata` reste accessible, donc les fichiers `env.py` d'Alembic (`target_metadata = models.Base.metadata`) fonctionnent sans modification
- Les modèles existants utilisant `Mapped`, `mapped_column`, et `relationship` sont déjà compatibles avec `DeclarativeBase`
- Aucune modification nécessaire dans les fichiers `alembic/env.py` car ils accèdent `Base.metadata` via `models.Base.metadata`

**Changement 2 : Remplacement passlib → bcrypt — cmv_gateway/cmv_back/app/dependancies/auth.py**

Remplacer :
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# ...
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

Par :
```python
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
```

**Changement 3 : Remplacement passlib → bcrypt — cmv_gateway/cmv_back/app/repositories/user_crud.py**

Supprimer l'import et l'instanciation de `CryptContext` (non utilisé directement dans ce fichier pour hash/verify, seulement importé).

**Changement 4 : Remplacement passlib → bcrypt — cmv_gateway/cmv_back/app/routers/auth.py**

Supprimer l'import et l'instanciation de `CryptContext` (non utilisé directement dans les routes, le hachage est délégué au service d'authentification).

**Changement 5 : Remplacement passlib → bcrypt — Scripts de fixtures**

Fichiers : `cmv_gateway/cmv_back/fixtures.py`, `cmv_gateway/cmv_back/create_fixtures.py`, `cmv_gateway/cmv_back/app/utils/fixtures.py`

Remplacer :
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("Abcdef@123456")
```

Par :
```python
import bcrypt
hashed_password = bcrypt.hashpw("Abcdef@123456".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

**Changement 6 : Remplacement passlib → bcrypt — cmv_patients/app/dependancies/auth.py**

Supprimer l'import de `CryptContext` et l'instanciation de `pwd_context` (ce fichier ne fait que de la vérification JWT, `pwd_context` n'est pas utilisé dans les fonctions).

**Changement 7 : Remplacement passlib → bcrypt — cmv_chambres/app/dependancies/auth.py**

Supprimer l'import de `CryptContext` et l'instanciation de `pwd_context` (ce fichier ne fait que de la vérification JWT, `pwd_context` n'est pas utilisé dans les fonctions).

**Changement 8 : Remplacement passlib → bcrypt — cmv_gateway/cmv_back/app/tests/conftest.py**

Remplacer l'usage de `CryptContext` par `bcrypt` direct pour le hachage du mot de passe de test.

**Changement 9 : Mise à jour des requirements.txt — 4 fichiers**

Supprimer `passlib[bcrypt]==1.7.4` des `requirements.txt` des 4 services. La dépendance `bcrypt==4.1.3` est déjà présente.

**Note sur la compatibilité bcrypt :**
- passlib avec le schéma `bcrypt` produit des hachages au format `$2b$12$...`
- La bibliothèque `bcrypt` directe produit le même format `$2b$12$...`
- `bcrypt.checkpw()` vérifie correctement les hachages produits par passlib
- Le coût par défaut de passlib bcrypt est 12 rounds, identique au défaut de `bcrypt.gensalt()`

## Stratégie de Test

### Approche de Validation

La stratégie de test suit une approche en deux phases : d'abord, mettre en évidence des contre-exemples démontrant le bug sur le code non corrigé, puis vérifier que la correction fonctionne et préserve le comportement existant.

### Vérification Exploratoire de la Condition de Bug

**Objectif** : Mettre en évidence des contre-exemples démontrant le bug AVANT d'implémenter la correction. Confirmer ou réfuter l'analyse de cause racine.

**Plan de test** : Écrire des tests qui importent les modules affectés et capturent les warnings émis. Exécuter ces tests sur le code NON CORRIGÉ pour observer les warnings.

**Cas de test** :
1. **Test Warning SQLAlchemy** : Importer `database.py` et vérifier qu'un `MovedIn20Warning` est émis (échouera sur le code non corrigé)
2. **Test Warning passlib** : Importer un module auth utilisant `CryptContext` et vérifier qu'un `DeprecationWarning` lié à `crypt` est émis (échouera sur le code non corrigé)
3. **Test Hash passlib** : Hacher un mot de passe via `pwd_context.hash()` et vérifier le format de sortie
4. **Test Verify passlib** : Vérifier un mot de passe haché via `pwd_context.verify()` et confirmer le résultat

**Contre-exemples attendus** :
- `MovedIn20Warning` émis lors de l'import de `declarative_base` depuis `sqlalchemy.ext.declarative`
- `DeprecationWarning` émis lors du chargement de passlib qui importe le module `crypt`

### Vérification de la Correction (Fix Checking)

**Objectif** : Vérifier que pour toutes les entrées où la condition de bug est vraie, la fonction corrigée produit le comportement attendu.

**Pseudocode :**
```
POUR TOUT fichier_database DANS [cmv_patients, cmv_chambres, cmv_gateway, cmv_ml] FAIRE
  result ← importer(fichier_database_corrigé)
  ASSERT aucun_MovedIn20Warning(result)
  ASSERT Base_est_classe_valide(result)
  ASSERT metadata_est_accessible(result)
FIN POUR

POUR TOUT module_auth DANS [cmv_gateway.auth, cmv_patients.auth, cmv_chambres.auth] FAIRE
  result ← importer(module_auth_corrigé)
  ASSERT aucun_DeprecationWarning_crypt(result)
FIN POUR

POUR TOUT mot_de_passe DANS mots_de_passe_aléatoires FAIRE
  hash ← bcrypt.hashpw(mot_de_passe)
  ASSERT bcrypt.checkpw(mot_de_passe, hash) = True
  ASSERT hash commence_par "$2b$"
FIN POUR
```

### Vérification de Préservation (Preservation Checking)

**Objectif** : Vérifier que pour toutes les entrées où la condition de bug n'est PAS vraie, la fonction corrigée produit le même résultat que la fonction originale.

**Pseudocode :**
```
POUR TOUT modèle DANS modèles_existants FAIRE
  ASSERT modèle_corrigé.metadata = modèle_original.metadata
  ASSERT modèle_corrigé.__tablename__ = modèle_original.__tablename__
  ASSERT modèle_corrigé.columns = modèle_original.columns
FIN POUR

POUR TOUT hash_existant DANS hachages_bcrypt_en_base FAIRE
  ASSERT bcrypt.checkpw(mot_de_passe_original, hash_existant) = pwd_context.verify(mot_de_passe_original, hash_existant)
FIN POUR
```

**Approche de test** : Les tests basés sur les propriétés (PBT) sont recommandés pour la vérification de préservation car :
- Ils génèrent automatiquement de nombreux cas de test sur le domaine d'entrée
- Ils détectent des cas limites que les tests unitaires manuels pourraient manquer
- Ils fournissent des garanties solides que le comportement est inchangé pour toutes les entrées non affectées

**Plan de test** : Observer le comportement sur le code NON CORRIGÉ d'abord pour les opérations ORM et le hachage de mots de passe, puis écrire des tests PBT capturant ce comportement.

**Cas de test** :
1. **Préservation ORM** : Observer que les modèles se définissent correctement sur le code non corrigé, puis vérifier que cela continue après la correction
2. **Préservation Metadata** : Observer que `Base.metadata.tables` contient les mêmes tables avant et après la correction
3. **Préservation Hachage** : Observer que `pwd_context.verify(password, hash)` retourne True sur le code non corrigé, puis vérifier que `bcrypt.checkpw()` retourne le même résultat
4. **Préservation Sessions** : Observer que `SessionLocal()` crée des sessions fonctionnelles avant et après la correction

### Tests Unitaires

- Vérifier que l'import de `database.py` corrigé ne produit aucun warning
- Vérifier que `Base` est une classe valide pour l'héritage de modèles
- Vérifier que `bcrypt.hashpw()` produit un hash au format `$2b$`
- Vérifier que `bcrypt.checkpw()` valide correctement un mot de passe
- Vérifier que `bcrypt.checkpw()` rejette un mauvais mot de passe
- Vérifier la compatibilité avec un hash produit par passlib

### Tests Basés sur les Propriétés (PBT)

- Générer des mots de passe aléatoires et vérifier que `hashpw` suivi de `checkpw` retourne toujours True
- Générer des paires (mot_de_passe, mauvais_mot_de_passe) et vérifier que `checkpw` retourne toujours False quand les mots de passe diffèrent
- Vérifier que les hachages produits commencent toujours par `$2b$` et ont la bonne longueur (60 caractères)

### Tests d'Intégration

- Exécuter les migrations Alembic avec la nouvelle `Base` et vérifier qu'elles passent
- Créer un modèle, l'insérer en base, et le relire pour vérifier le cycle complet ORM
- Hacher un mot de passe, le stocker, et le vérifier dans un flux d'authentification complet
