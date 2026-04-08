# Document de Correction de Bug

## Introduction

Deux avertissements de dépréciation polluent la sortie des tests et les logs dans l'ensemble des services du projet (cmv_patients, cmv_chambres, cmv_gateway/cmv_back, cmv_ml). Ces warnings génèrent du bruit dans la sortie des tests, masquent potentiellement de vrais problèmes, et signalent l'utilisation d'APIs qui seront supprimées dans de futures versions de Python et SQLAlchemy.

1. **`declarative_base()` déprécié** — Tous les fichiers `app/utils/database.py` importent `declarative_base` depuis `sqlalchemy.ext.declarative`, un chemin déprécié depuis SQLAlchemy 2.0. Le projet utilise déjà SQLAlchemy 2.0.46/2.0.48.

2. **Module `crypt` déprécié via passlib** — La dépendance `passlib[bcrypt]==1.7.4` utilise en interne le module `crypt` de Python, qui est déprécié depuis Python 3.11 et sera supprimé en Python 3.13. passlib n'est plus activement maintenu.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN les tests sont exécutés dans n'importe quel service (cmv_patients, cmv_chambres, cmv_gateway, cmv_ml) THEN le système affiche un avertissement `MovedIn20Warning: The declarative_base() function is now available as sqlalchemy.orm.declarative_base()` car `database.py` importe depuis `sqlalchemy.ext.declarative`

1.2 WHEN les tests sont exécutés dans un service utilisant passlib (cmv_patients, cmv_chambres, cmv_gateway) THEN le système affiche un avertissement `DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13` provenant du module interne de passlib

1.3 WHEN les logs de production ou de CI sont consultés THEN les avertissements de dépréciation polluent la sortie et masquent potentiellement de vrais problèmes

### Expected Behavior (Correct)

2.1 WHEN les tests sont exécutés dans n'importe quel service THEN le système SHALL ne produire aucun avertissement `MovedIn20Warning` lié à `declarative_base`, en utilisant l'import moderne `from sqlalchemy.orm import DeclarativeBase` (approche classe de base SQLAlchemy 2.0)

2.2 WHEN les tests sont exécutés dans un service utilisant le hachage de mots de passe THEN le système SHALL ne produire aucun avertissement `DeprecationWarning` lié au module `crypt`, en remplaçant `passlib` par l'utilisation directe de la bibliothèque `bcrypt` (déjà présente dans les dépendances)

2.3 WHEN les logs de production ou de CI sont consultés THEN le système SHALL afficher une sortie propre sans avertissements de dépréciation liés à SQLAlchemy ou passlib

### Unchanged Behavior (Regression Prevention)

3.1 WHEN les modèles SQLAlchemy sont définis en héritant de `Base` THEN le système SHALL CONTINUE À permettre la définition de modèles ORM et les opérations CRUD normalement

3.2 WHEN les sessions de base de données sont créées via `SessionLocal` THEN le système SHALL CONTINUE À fournir des sessions fonctionnelles avec autocommit=False et autoflush=False

3.3 WHEN `metadata` est accédé depuis le module database THEN le système SHALL CONTINUE À exposer les métadonnées de la base pour les migrations Alembic et autres usages

3.4 WHEN un mot de passe est haché ou vérifié via les fonctions d'authentification THEN le système SHALL CONTINUE À produire et vérifier des hachages bcrypt compatibles avec les mots de passe existants en base de données

3.5 WHEN les migrations Alembic sont exécutées THEN le système SHALL CONTINUE À fonctionner correctement avec la nouvelle classe de base déclarative

---

## Dérivation de la Condition de Bug

### Condition de Bug — Warning SQLAlchemy

```pascal
FUNCTION isBugCondition_SQLAlchemy(X)
  INPUT: X de type ModuleImport (un fichier database.py d'un service)
  OUTPUT: boolean

  // Retourne vrai quand le fichier importe declarative_base depuis le chemin déprécié
  RETURN X.import_path = "sqlalchemy.ext.declarative.declarative_base"
END FUNCTION
```

### Propriété — Correction SQLAlchemy

```pascal
// Propriété : Vérification de la correction — Import SQLAlchemy moderne
FOR ALL X WHERE isBugCondition_SQLAlchemy(X) DO
  result ← importer_et_executer(X')
  ASSERT aucun_warning_MovedIn20(result) AND Base_est_fonctionnel(result)
END FOR
```

### Condition de Bug — Warning passlib/crypt

```pascal
FUNCTION isBugCondition_Passlib(X)
  INPUT: X de type ServiceDependency (un service utilisant passlib)
  OUTPUT: boolean

  // Retourne vrai quand le service dépend de passlib qui utilise le module crypt déprécié
  RETURN X.dependencies CONTIENT "passlib" ET passlib_utilise_crypt(X)
END FUNCTION
```

### Propriété — Correction passlib

```pascal
// Propriété : Vérification de la correction — Pas de warning crypt
FOR ALL X WHERE isBugCondition_Passlib(X) DO
  result ← hacher_et_verifier_mot_de_passe(X')
  ASSERT aucun_warning_crypt(result) AND hachage_bcrypt_valide(result)
END FOR
```

### Objectif de Préservation

```pascal
// Propriété : Vérification de préservation — Comportement identique
FOR ALL X WHERE NOT isBugCondition_SQLAlchemy(X) AND NOT isBugCondition_Passlib(X) DO
  ASSERT F(X) = F'(X)
END FOR
```

Ceci garantit que pour toutes les entrées non affectées par le bug, le code corrigé se comporte de manière identique à l'original.
