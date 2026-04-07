# Document de Conception — Sécurisation des Secrets et Configuration

## Vue d'ensemble

Le projet CMV Healthcare est composé de quatre microservices FastAPI qui partagent actuellement un problème critique : les secrets (mots de passe de base de données, clés JWT, clés AWS, clé HMAC) sont stockés en clair dans des fichiers `.env` versionnés dans Git. De plus, la configuration est chargée via `os.getenv()` sans aucune validation au démarrage, ce qui permet à un service de démarrer avec une configuration incomplète et de produire des erreurs difficiles à diagnostiquer en production.

Cette conception définit la migration vers `pydantic-settings` (BaseSettings) pour chaque microservice, l'épinglage des dépendances, la création de fichiers `.env.example` documentés, et la mise en place d'une stratégie de configuration par environnement.

### Objectifs

- Supprimer tous les secrets du dépôt Git
- Valider la configuration au démarrage avec des messages d'erreur explicites
- Séparer les configurations par environnement (dev / staging / production)
- Garantir des builds reproductibles via l'épinglage des dépendances
- Fournir un chemin de migration clair depuis `os.getenv()` vers BaseSettings

---

## Architecture

### Avant (état actuel)

```
service/
├── .env                  ← secrets en clair, versionné dans Git
├── requirements.txt      ← dépendances non épinglées
└── app/utils/config.py   ← os.getenv() sans validation
```

### Après (cible)

```
service/
├── .env                  ← secrets réels, exclu de Git
├── .env.example          ← modèle documenté, versionné dans Git
├── requirements.txt      ← dépendances de production épinglées
├── requirements-dev.txt  ← dépendances de test épinglées
└── app/utils/config.py   ← BaseSettings avec validation Pydantic
```

### Flux de chargement de la configuration

```mermaid
flowchart TD
    A[Démarrage du service] --> B[Instanciation de Settings]
    B --> C{Variables d'environnement système ?}
    C -->|Oui| D[Priorité : variables système]
    C -->|Non| E[Lecture du fichier .env]
    D --> F[Validation Pydantic]
    E --> F
    F --> G{Validation réussie ?}
    G -->|Non| H[ValidationError → arrêt du service\nmessage d'erreur explicite]
    G -->|Oui| I{ENVIRONMENT == production ?}
    I -->|Oui| J[Validation renforcée\nSECRET_KEY ≥ 32 chars\nHMAC = 64 hex chars\nPas de valeurs faibles connues]
    J --> K{Validation production OK ?}
    K -->|Non| H
    K -->|Oui| L[Configuration disponible]
    I -->|Non| L
```

---

## Composants et Interfaces

### Composant 1 : `GatewaySettings` (cmv_gateway/cmv_back)

Remplace le fichier `cmv_gateway/cmv_back/app/utils/config.py`.

**Variables gérées :**
- `GATEWAY_DATABASE_URL` — URL PostgreSQL (obligatoire)
- `SECRET_KEY` — clé JWT (obligatoire, validation renforcée en production)
- `ALGORITHM` — algorithme JWT (défaut : `"HS256"`)
- `PATIENTS_SERVICE` — URL du service patients (obligatoire)
- `CHAMBRES_SERVICE` — URL du service chambres (obligatoire)
- `ML_SERVICE` — URL du service ML (obligatoire)
- `ACCESS_MAX_AGE` — durée du token d'accès en minutes (défaut : `30`)
- `REFRESH_MAX_AGE` — durée du token de rafraîchissement en minutes (défaut : `1440`)
- `ENVIRONMENT` — profil d'environnement (défaut : `"dev"`)
- `VALKEY_HOST` — hôte Valkey/Redis (défaut : `"redis"`)
- `VALKEY_PORT` — port Valkey/Redis (défaut : `6379`)

### Composant 2 : `PatientsSettings` (cmv_patients)

Remplace le fichier `cmv_patients/app/utils/config.py`.

**Variables gérées :**
- `PATIENTS_DATABASE_URL` — URL PostgreSQL (obligatoire)
- `SECRET_KEY` — clé JWT (obligatoire)
- `ALGORITHM` — algorithme JWT (défaut : `"HS256"`)
- `ENVIRONMENT` — profil d'environnement (défaut : `"dev"`)
- `AWS_BUCKET_NAME` — nom du bucket S3 (obligatoire)
- `AWS_ACCESS_KEY_ID` — identifiant AWS (obligatoire)
- `AWS_SECRET_ACCESS_KEY` — clé secrète AWS (obligatoire)
- `AWS_REGION` — région AWS (obligatoire)
- `CHAMBRES_SERVICE` — URL du service chambres (obligatoire)

### Composant 3 : `ChambresSettings` (cmv_chambres)

Remplace le fichier `cmv_chambres/app/utils/config.py`.

**Variables gérées :**
- `CHAMBRES_DATABASE_URL` — URL PostgreSQL (obligatoire)
- `SECRET_KEY` — clé JWT (obligatoire)
- `ALGORITHM` — algorithme JWT (défaut : `"HS256"`)
- `ENVIRONMENT` — profil d'environnement (défaut : `"dev"`)

### Composant 4 : `MLSettings` (cmv_ml)

Remplace le fichier `cmv_ml/app/utils/config.py`.

**Variables gérées :**
- `ML_DATABASE_URL` — URL PostgreSQL (obligatoire)
- `SECRET_KEY` — clé JWT (obligatoire)
- `ALGORITHM` — algorithme JWT (défaut : `"HS256"`)
- `ENVIRONMENT` — profil d'environnement (défaut : `"dev"`)
- `MODEL_PATH` — chemin vers le modèle XGBoost (défaut : `"./models/model.ubj"`)
- `SHAP_ENABLED` — activation de l'explicabilité SHAP (défaut : `False`)
- `HMAC` — clé HMAC 256 bits en hexadécimal (obligatoire)

### Interface commune : validateurs partagés

Les validateurs suivants sont communs à tous les services et peuvent être extraits dans un module partagé ou dupliqués dans chaque service :

- `validate_postgres_url(v)` — vérifie que l'URL commence par `postgresql://` ou `postgresql+asyncpg://`
- `validate_service_url(v)` — vérifie que l'URL commence par `http://` ou `https://`
- `validate_secret_key_production(v, values)` — en production : longueur ≥ 32, rejet des valeurs faibles connues
- `validate_hmac(v)` — vérifie que la valeur est une chaîne hexadécimale de 64 caractères

---

## Modèles de données

### Structure de `GatewaySettings`

```python
from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

WEAK_SECRETS = {"cle_tres_secrete", "secret", "changez-moi", "password", "123456"}

class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Base de données
    GATEWAY_DATABASE_URL: str
    TEST_DATABASE_URL: str = "sqlite:///:memory:"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_MAX_AGE: int = 30
    REFRESH_MAX_AGE: int = 1440

    # Services
    PATIENTS_SERVICE: str
    CHAMBRES_SERVICE: str
    ML_SERVICE: str

    # Environnement
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"

    # Valkey
    VALKEY_HOST: str = "redis"
    VALKEY_PORT: int = 6379

    @field_validator("GATEWAY_DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("GATEWAY_DATABASE_URL doit être une URL PostgreSQL valide")
        return v

    @field_validator("PATIENTS_SERVICE", "CHAMBRES_SERVICE", "ML_SERVICE")
    @classmethod
    def validate_service_urls(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"L'URL de service doit commencer par http:// ou https://")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        # La validation renforcée en production est effectuée dans model_post_init
        return v

    def model_post_init(self, __context) -> None:
        if self.ENVIRONMENT == "production":
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY doit avoir au moins 32 caractères en production")
            if self.SECRET_KEY in WEAK_SECRETS:
                raise ValueError("SECRET_KEY utilise une valeur faible connue")


# Singleton — instancié une seule fois au démarrage
settings = GatewaySettings()
```

### Structure de `MLSettings` (avec validation HMAC)

```python
import re
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class MLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ML_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"
    MODEL_PATH: str = "./models/model.ubj"
    SHAP_ENABLED: bool = False
    HMAC: str

    @field_validator("ML_DATABASE_URL")
    @classmethod
    def validate_db_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("ML_DATABASE_URL doit être une URL PostgreSQL valide")
        return v

    @field_validator("HMAC")
    @classmethod
    def validate_hmac(cls, v: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", v):
            raise ValueError("HMAC doit être une chaîne hexadécimale de 64 caractères (256 bits)")
        return v

    def model_post_init(self, __context) -> None:
        if self.ENVIRONMENT == "production":
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY doit avoir au moins 32 caractères en production")
            if self.SECRET_KEY in WEAK_SECRETS:
                raise ValueError("SECRET_KEY utilise une valeur faible connue")


settings = MLSettings()
```

### Structure des fichiers `.env.example`

Chaque service dispose d'un `.env.example` versionné dans Git. Exemple pour `cmv_gateway/cmv_back/.env.example` :

```dotenv
# URL de connexion à la base de données PostgreSQL du gateway
GATEWAY_DATABASE_URL="postgresql://postgres:mot_de_passe_local@localhost:6001/cmv_gateway"

# Clé secrète pour la signature des tokens JWT (min. 32 caractères en production)
SECRET_KEY="changez-moi-avec-une-valeur-aleatoire-de-32-chars"

# Algorithme de signature JWT
ALGORITHM="HS256"

# Durée de validité du token d'accès (en minutes)
ACCESS_MAX_AGE="30"

# Durée de validité du token de rafraîchissement (en minutes)
REFRESH_MAX_AGE="1440"

# URL du service patients
PATIENTS_SERVICE="http://localhost:8002/api"

# URL du service chambres
CHAMBRES_SERVICE="http://localhost:8003/api"

# URL du service ML
ML_SERVICE="http://localhost:8004"

# Environnement d'exécution : dev | staging | production
ENVIRONMENT="dev"

# Hôte du serveur Valkey/Redis
VALKEY_HOST="localhost"

# Port du serveur Valkey/Redis
VALKEY_PORT="6379"
```

### Structure du `.gitignore` mis à jour

```gitignore
# Secrets — ne jamais versionner les fichiers .env réels
.env
**/.env
**/.env.local
**/.env.*.local

# Répertoires générés
tmp/
.DS_Store
cmv_gateway/cmv_back/dist
node_modules/
venv/
# ... (entrées existantes conservées)
```

### Stratégie d'épinglage des dépendances

**`requirements.txt`** (production uniquement) :

```
fastapi==0.115.5
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
uvicorn==0.32.1
pydantic-settings==2.6.1
alembic==1.14.0
cryptography==43.0.3
python-jose==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.3
httpx==0.27.2
fastapi_limiter==0.1.6
aiohttp==3.11.7
python-multipart==0.0.17
email-validator==2.2.0
```

**`requirements-dev.txt`** (tests et développement) :

```
-r requirements.txt
faker==33.1.0
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-mock==3.14.0
pytest-httpx==0.32.0
hypothesis==6.119.3
fakeredis==2.26.1
```

> **Décision de conception** : `python-dotenv` est retiré des dépendances de production car `pydantic-settings` gère nativement le chargement des fichiers `.env` via `python-dotenv` en interne. La dépendance reste transitive.

### Chemin de migration depuis `os.getenv()`

La migration suit un pattern de remplacement direct. Avant :

```python
# config.py (avant)
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("CHAMBRES_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
```

Après :

```python
# config.py (après)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class ChambresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    CHAMBRES_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ENVIRONMENT: Literal["dev", "staging", "production"] = "dev"

settings = ChambresSettings()

# Aliases pour la compatibilité avec le code existant
DATABASE_URL = settings.CHAMBRES_DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ENVIRONMENT = settings.ENVIRONMENT
```

Les aliases permettent une migration progressive : le reste du code (`database.py`, routers, etc.) continue d'importer `DATABASE_URL` depuis `config.py` sans modification immédiate.

---

## Propriétés de Correction

*Une propriété est une caractéristique ou un comportement qui doit être vrai pour toutes les exécutions valides d'un système — c'est-à-dire une déclaration formelle de ce que le système doit faire. Les propriétés servent de pont entre les spécifications lisibles par l'humain et les garanties de correction vérifiables automatiquement.*

### Propriété 1 : Rejet des URLs PostgreSQL invalides

*Pour toute* chaîne de caractères qui ne commence pas par `postgresql://` ou `postgresql+asyncpg://`, l'instanciation de n'importe quel `*Settings` avec cette valeur comme URL de base de données doit lever une `ValidationError`.

**Valide : Exigences 3.3, 3.5**

### Propriété 2 : Rejet des URLs de services invalides

*Pour toute* chaîne de caractères qui ne commence pas par `http://` ou `https://`, l'instanciation de `GatewaySettings` ou `PatientsSettings` avec cette valeur comme URL de service doit lever une `ValidationError`.

**Valide : Exigences 6.2, 6.3**

### Propriété 3 : Validation HMAC — format hexadécimal 64 caractères

*Pour toute* chaîne de caractères qui n'est pas exactement 64 caractères hexadécimaux (`[0-9a-fA-F]{64}`), l'instanciation de `MLSettings` avec cette valeur comme `HMAC` doit lever une `ValidationError`.

**Valide : Exigences 7.3, 7.4**

### Propriété 4 : Rejet des SECRET_KEY faibles en production

*Pour toute* valeur de `SECRET_KEY` appartenant à l'ensemble des valeurs faibles connues (`"cle_tres_secrete"`, `"secret"`, `"changez-moi"`, etc.), l'instanciation d'un `*Settings` avec `ENVIRONMENT="production"` doit lever une `ValidationError`.

**Valide : Exigences 7.2, 7.4**

### Propriété 5 : Rejet des SECRET_KEY trop courtes en production

*Pour toute* chaîne de caractères de longueur strictement inférieure à 32, l'instanciation d'un `*Settings` avec `ENVIRONMENT="production"` et cette valeur comme `SECRET_KEY` doit lever une `ValidationError`.

**Valide : Exigences 7.1, 7.4**

### Propriété 6 : Acceptation des configurations valides

*Pour tout* ensemble de variables d'environnement valides (URLs PostgreSQL correctes, URLs de services correctes, HMAC de 64 hex chars, SECRET_KEY ≥ 32 chars en production), l'instanciation du `*Settings` correspondant doit réussir sans exception.

**Valide : Exigences 3.1, 3.4**

### Propriété 7 : Priorité variable système sur fichier .env

*Pour toute* variable d'environnement définie à la fois dans un fichier `.env` et comme variable système, la valeur retournée par `settings` doit être celle de la variable système.

**Valide : Exigence 5.3**

### Propriété 8 : Valeurs par défaut pour les variables optionnelles

*Pour tout* `*Settings` instancié sans fournir les variables optionnelles (`ALGORITHM`, `ENVIRONMENT`, `VALKEY_PORT`, `SHAP_ENABLED`, etc.), les valeurs par défaut définies dans le modèle doivent être utilisées.

**Valide : Exigence 3.4**

---

## Gestion des Erreurs

### Erreurs au démarrage (fail-fast)

Toutes les erreurs de configuration doivent être détectées au démarrage, avant que le service ne commence à traiter des requêtes. Le pattern singleton (`settings = GatewaySettings()` au niveau module) garantit ce comportement : si la validation échoue, l'import du module lève une exception et le service ne démarre pas.

| Situation | Comportement attendu |
|---|---|
| Variable obligatoire absente | `ValidationError` avec le nom de la variable |
| URL PostgreSQL invalide | `ValidationError` : "doit être une URL PostgreSQL valide" |
| URL de service invalide | `ValidationError` : "doit commencer par http:// ou https://" |
| HMAC non hexadécimal ou ≠ 64 chars | `ValidationError` : "chaîne hexadécimale de 64 caractères" |
| SECRET_KEY < 32 chars en production | `ValidationError` : "au moins 32 caractères en production" |
| SECRET_KEY faible en production | `ValidationError` : "valeur faible connue" |
| ENVIRONMENT invalide | `ValidationError` : valeur non dans `["dev", "staging", "production"]` |

### Gestion de la valeur `None`

Avec `os.getenv()`, une variable absente retourne silencieusement `None`, ce qui peut provoquer des erreurs tardives difficiles à diagnostiquer (ex: `TypeError: argument of type 'NoneType' is not iterable`). Avec BaseSettings, les champs sans valeur par défaut sont obligatoires : leur absence lève immédiatement une `ValidationError` avec le nom du champ manquant.

### Compatibilité avec les tests existants

Les tests qui utilisent `TEST_DATABASE_URL` ou qui patchent `os.environ` restent compatibles. Pour les tests unitaires des Settings eux-mêmes, on utilise le pattern :

```python
def test_invalid_db_url():
    with pytest.raises(ValidationError):
        GatewaySettings(
            GATEWAY_DATABASE_URL="mysql://invalid",
            SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
            PATIENTS_SERVICE="http://localhost:8002/api",
            CHAMBRES_SERVICE="http://localhost:8003/api",
            ML_SERVICE="http://localhost:8004",
        )
```

---

## Stratégie de Tests

### Approche duale : tests unitaires + tests basés sur les propriétés

Les deux types de tests sont complémentaires et tous deux nécessaires :

- **Tests unitaires** : vérifient des exemples concrets, des cas limites et des conditions d'erreur spécifiques
- **Tests basés sur les propriétés** : vérifient les propriétés universelles sur un grand nombre d'entrées générées aléatoirement

### Tests unitaires

Chaque service dispose d'un fichier `tests/test_config.py` couvrant :

- Instanciation réussie avec toutes les variables valides
- Rejet de chaque variable obligatoire manquante (un test par variable)
- Rejet des URLs invalides (exemples concrets : `"mysql://..."`, `"ftp://..."`, `""`)
- Rejet du HMAC invalide (trop court, trop long, caractères non-hex)
- Comportement en production vs dev pour SECRET_KEY
- Vérification des valeurs par défaut

### Tests basés sur les propriétés (Hypothesis)

La bibliothèque **Hypothesis** est utilisée pour les tests basés sur les propriétés (déjà présente dans `cmv_gateway/cmv_back/requirements.txt` et `cmv_ml/requirements.txt`).

Chaque test de propriété doit être configuré avec un minimum de **100 itérations** via `@settings(max_examples=100)`.

Format de tag requis : `# Feature: secure-secrets-config, Property N: <texte de la propriété>`

#### Propriété 1 — Rejet des URLs PostgreSQL invalides

```python
# Feature: secure-secrets-config, Property 1: rejet des URLs PostgreSQL invalides
@given(st.text().filter(lambda s: not s.startswith(("postgresql://", "postgresql+asyncpg://"))))
@settings(max_examples=100)
def test_invalid_postgres_url_rejected(invalid_url):
    with pytest.raises(ValidationError):
        ChambresSettings(
            CHAMBRES_DATABASE_URL=invalid_url,
            SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
        )
```

#### Propriété 2 — Rejet des URLs de services invalides

```python
# Feature: secure-secrets-config, Property 2: rejet des URLs de services invalides
@given(st.text().filter(lambda s: not s.startswith(("http://", "https://"))))
@settings(max_examples=100)
def test_invalid_service_url_rejected(invalid_url):
    with pytest.raises(ValidationError):
        GatewaySettings(
            GATEWAY_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
            SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
            PATIENTS_SERVICE=invalid_url,
            CHAMBRES_SERVICE="http://localhost:8003/api",
            ML_SERVICE="http://localhost:8004",
        )
```

#### Propriété 3 — Validation HMAC

```python
# Feature: secure-secrets-config, Property 3: validation HMAC format hexadécimal 64 caractères
@given(st.text().filter(lambda s: not re.fullmatch(r"[0-9a-fA-F]{64}", s)))
@settings(max_examples=100)
def test_invalid_hmac_rejected(invalid_hmac):
    with pytest.raises(ValidationError):
        MLSettings(
            ML_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
            SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
            HMAC=invalid_hmac,
        )
```

#### Propriété 4 — Rejet des SECRET_KEY faibles en production

```python
# Feature: secure-secrets-config, Property 4: rejet des SECRET_KEY faibles en production
@given(st.sampled_from(list(WEAK_SECRETS)))
@settings(max_examples=100)
def test_weak_secret_key_rejected_in_production(weak_key):
    with pytest.raises(ValidationError):
        ChambresSettings(
            CHAMBRES_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
            SECRET_KEY=weak_key,
            ENVIRONMENT="production",
        )
```

#### Propriété 5 — Rejet des SECRET_KEY trop courtes en production

```python
# Feature: secure-secrets-config, Property 5: rejet des SECRET_KEY trop courtes en production
@given(st.text(max_size=31).filter(lambda s: s not in WEAK_SECRETS))
@settings(max_examples=100)
def test_short_secret_key_rejected_in_production(short_key):
    with pytest.raises(ValidationError):
        ChambresSettings(
            CHAMBRES_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
            SECRET_KEY=short_key,
            ENVIRONMENT="production",
        )
```

#### Propriété 6 — Acceptation des configurations valides

```python
# Feature: secure-secrets-config, Property 6: acceptation des configurations valides
@given(
    db_url=st.just("postgresql://postgres:pwd@localhost/db"),
    secret=st.text(min_size=32).filter(lambda s: s not in WEAK_SECRETS),
)
@settings(max_examples=100)
def test_valid_config_accepted(db_url, secret):
    s = ChambresSettings(
        CHAMBRES_DATABASE_URL=db_url,
        SECRET_KEY=secret,
        ENVIRONMENT="production",
    )
    assert s.CHAMBRES_DATABASE_URL == db_url
    assert s.SECRET_KEY == secret
```

#### Propriété 7 — Priorité variable système sur fichier .env

```python
# Feature: secure-secrets-config, Property 7: priorité variable système sur fichier .env
@given(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))))
@settings(max_examples=100)
def test_env_var_overrides_dotenv(env_value, monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('ALGORITHM="HS256_FROM_FILE"\n')
    monkeypatch.setenv("ALGORITHM", env_value)
    s = ChambresSettings(
        CHAMBRES_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
        SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
        _env_file=str(env_file),
    )
    assert s.ALGORITHM == env_value
```

#### Propriété 8 — Valeurs par défaut pour les variables optionnelles

```python
# Feature: secure-secrets-config, Property 8: valeurs par défaut pour les variables optionnelles
def test_default_values_applied():
    s = ChambresSettings(
        CHAMBRES_DATABASE_URL="postgresql://postgres:pwd@localhost/db",
        SECRET_KEY="une-cle-valide-de-32-caracteres-ok",
    )
    assert s.ALGORITHM == "HS256"
    assert s.ENVIRONMENT == "dev"
```
