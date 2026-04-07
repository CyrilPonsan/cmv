# Plan d'implémentation : Sécurité des Pipelines Jenkins

## Vue d'ensemble

Sécurisation incrémentale des 8 Jenkinsfiles du projet CMV. Chaque tâche applique les patterns de sécurité définis dans le design (single-quotes, withCredentials, heredoc quoté, set +x, nettoyage post-build). Les tests property-based (Hypothesis/Python) valident les propriétés de correction sur les fichiers modifiés.

## Tâches

- [x] 1. Sécuriser les pipelines gateway (déploiement direct EC2)
  - [x] 1.1 Sécuriser Jenkins-gateway
    - Supprimer `DOCKERHUB_CREDENTIALS = credentials('cmv-dockerhub')` du bloc `environment`
    - Remplacer le stage `Push to DockerHub` par un bloc `withCredentials([usernamePassword(...)])` avec `sh '''` et `docker login --quiet`
    - Remplacer le stage `Deploy to EC2` : supprimer la variable `remoteCommands`, utiliser `sh '''` avec heredoc quoté `<< 'EOF'`, ajouter `set +x`
    - Nettoyer le stage `Build Image` : supprimer les `sh "echo ..."`, `sh "docker --version"`, `sh "pwd"`, `sh "ls -la"` et le bloc `script {}` inutile
    - Remplacer le bloc `post` : supprimer `node {}`, ajouter `docker logout || true` et `docker image rm "$IMAGE_GATEWAY:latest" || true`
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3_

  - [x] 1.2 Sécuriser Jenkins-gateway-cdk
    - Appliquer les mêmes corrections que Jenkins-gateway (même structure de déploiement direct avec `EC2_SERVER`/`EC2_USER`)
    - Adapter le stage `Install Dependencies` : remplacer `sh """` par `sh '''` pour `NPM_CACHE_DIR`
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1_

  - [x] 1.3 Sécuriser Jenkinsfile-gateway-exemple
    - Appliquer les mêmes corrections de sécurité au fichier exemple (structure similaire à Jenkins-gateway avec stages conditionnels)
    - Supprimer `docker.build()` Groovy et utiliser `sh 'docker build ...'` à la place
    - Corriger le heredoc non quoté dans le stage Deploy
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 4.1, 5.1, 5.2, 6.1_

- [x] 2. Checkpoint — Vérifier les pipelines gateway
  - Vérifier visuellement que les 3 fichiers gateway ne contiennent plus d'interpolation Groovy de secrets
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Sécuriser les pipelines avec déploiement via bastion (jump host)
  - [x] 3.1 Sécuriser Jenkins-chambres
    - Supprimer `DOCKERHUB_CREDENTIALS = credentials('cmv-dockerhub')` du bloc `environment`
    - Remplacer le stage `Push to DockerHub` par un bloc `withCredentials` avec `sh '''` et `docker login --quiet`
    - Remplacer le stage `Deploy to EC2` : encapsuler dans `withCredentials`, utiliser `sh '''` avec heredoc quoté, ajouter `set +x`, passer les variables SSH via `$VAR` shell
    - Nettoyer le stage `Build Image` : supprimer les commandes de debug et le bloc `script {}` inutile
    - Remplacer le bloc `post` : supprimer `node {}`, ajouter `docker logout || true` et `docker image rm`
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3_

  - [x] 3.2 Sécuriser Jenkins-chambres-cdk
    - Appliquer les mêmes corrections que Jenkins-chambres (même structure bastion avec `GATEWAY_HOST`/`GATEWAY_USER` et `CHAMBRES_HOST`/`CHAMBRES_USER`)
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2_

  - [x] 3.3 Sécuriser Jenkins-patients
    - Appliquer les mêmes corrections que Jenkins-chambres (même structure bastion avec `PATIENTS_HOST`/`PATIENTS_USER`)
    - Conserver le stage `Run Backend Tests` existant (docker-compose)
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2_

  - [x] 3.4 Sécuriser Jenkins-ml-cdk
    - Appliquer les mêmes corrections que Jenkins-chambres (structure bastion avec `ML_HOST`/`ML_USER`)
    - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2_

- [x] 4. Sécuriser Jenkins-ml (déploiement direct sans bastion)
  - Supprimer `DOCKERHUB_CREDENTIALS` du bloc `environment`
  - Remplacer le stage `Push to DockerHub` par un bloc `withCredentials` avec `sh '''`
  - Remplacer le stage `Deploy to EC2` : utiliser `sh '''` (pas `sh """`), ajouter `withCredentials` pour le docker login distant, heredoc quoté, `set +x`
  - Nettoyer le stage `Build Image` et le bloc `post`
  - _Exigences : 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 6.1_

- [x] 5. Checkpoint — Vérifier tous les Jenkinsfiles bastion et ML
  - Vérifier que les 5 fichiers restants ne contiennent plus d'interpolation Groovy de secrets
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Créer les tests property-based (Hypothesis/Python)
  - [x] 6.1 Mettre en place la structure de test et les helpers de parsing
    - Créer `tests/test_jenkinsfile_security.py` avec les imports Hypothesis et les fonctions utilitaires de parsing des Jenkinsfiles
    - Écrire les stratégies Hypothesis pour générer des noms de variables, d'images et d'hôtes
    - _Exigences : 6.1_

  - [ ]* 6.2 Écrire le property test pour la Property 1 (aucune interpolation Groovy de secrets)
    - **Property 1 : Aucune interpolation Groovy de secrets dans les étapes sh**
    - **Validates: Exigences 1.1, 1.2, 1.3, 3.1**
    - Générer des noms de secrets variés, vérifier qu'aucun `sh """...\${VAR}..."""` n'apparaît dans les étapes sh des 8 fichiers

  - [ ]* 6.3 Écrire le property test pour la Property 2 (heredocs SSH avec délimiteur quoté)
    - **Property 2 : Tous les heredocs SSH utilisent un délimiteur quoté**
    - **Validates: Exigences 1.4, 3.2**
    - Générer des blocs SSH avec heredocs, vérifier que tous les heredocs utilisent `<< 'EOF'` et non `<< EOF`

  - [ ]* 6.4 Écrire le property test pour la Property 3 (docker login --quiet)
    - **Property 3 : Docker login utilise le mode silencieux**
    - **Validates: Exigence 2.3**
    - Générer des commandes docker login, vérifier la présence de `--quiet` dans toutes les invocations

  - [ ]* 6.5 Écrire le property test pour la Property 4 (withCredentials pour DockerHub)
    - **Property 4 : withCredentials pour les identifiants DockerHub**
    - **Validates: Exigences 4.1, 4.2**
    - Vérifier que `DOCKERHUB_CREDENTIALS` n'apparaît pas dans le bloc `environment` et que chaque fichier contient un bloc `withCredentials([usernamePassword(credentialsId: 'cmv-dockerhub'`

  - [ ]* 6.6 Écrire le property test pour la Property 5 (set +x dans les blocs sh avec secrets)
    - **Property 5 : set +x dans les blocs shell contenant des secrets**
    - **Validates: Exigence 3.4**
    - Générer des blocs sh référençant des variables de secrets, vérifier que `set +x` est présent en début de bloc

  - [ ]* 6.7 Écrire le property test pour la Property 6 (variables d'image exportées dans les heredocs quotés)
    - **Property 6 : Variables d'image transmises explicitement dans les heredocs quotés**
    - **Validates: Exigence 3.3**
    - Vérifier que les heredocs quotés contenant des références à des images Docker incluent un `export` ou une affectation de variable en début de bloc distant

  - [ ]* 6.8 Écrire le property test pour la Property 7 (nettoyage post-build)
    - **Property 7 : Nettoyage post-build sécurisé et tolérant aux erreurs**
    - **Validates: Exigences 5.1, 5.2, 5.3**
    - Vérifier que le bloc `post.always` contient `docker logout || true`, pas de `node {`, et une suppression d'image avec `|| true`

  - [ ]* 6.9 Écrire le property test pour la Property 8 (structure fonctionnelle préservée)
    - **Property 8 : Structure fonctionnelle des stages préservée**
    - **Validates: Exigence 6.3**
    - Vérifier que les stages Checkout, Build Image, Push to DockerHub, Deploy to EC2 et le bloc post sont présents dans chaque Jenkinsfile dans le bon ordre

- [x] 7. Checkpoint final — Tous les tests passent
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches marquées `*` sont optionnelles et peuvent être ignorées pour un MVP rapide
- Les tests property-based utilisent **Hypothesis** (Python), déjà présent dans le workspace
- Chaque test doit être annoté avec `# Feature: jenkins-pipeline-security, Property {N}: {titre}` et `@settings(max_examples=100)`
- Les Jenkinsfiles sont testés par analyse statique du contenu (pas d'exécution des pipelines)
- Les pipelines gateway (tâche 1) et bastion (tâche 3) partagent les mêmes patterns — corriger l'un sert de référence pour les autres
