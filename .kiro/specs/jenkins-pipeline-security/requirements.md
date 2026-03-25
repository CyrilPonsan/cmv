# Document d'Exigences — Sécurité des Pipelines Jenkins

## Introduction

Ce document définit les exigences pour le renforcement de la sécurité des pipelines Jenkins du projet CMV. Le projet comporte 8 Jenkinsfiles (Jenkins-gateway, Jenkins-ml, Jenkins-chambres, Jenkins-patients et leurs variantes CDK) qui partagent des patterns similaires présentant des vulnérabilités de sécurité. Les problèmes principaux identifiés sont : l'interpolation Groovy de secrets dans les étapes `sh`, des logs verbeux exposant des informations sensibles, et un manque de bonnes pratiques de sécurité générales.

## Glossaire

- **Pipeline** : Un pipeline Jenkins déclaratif défini dans un Jenkinsfile
- **Interpolation_Groovy** : Le mécanisme Groovy utilisant des guillemets doubles (`"..."`) ou triple-guillemets (`"""..."""`) pour insérer des variables dans des chaînes, dangereux quand utilisé avec des secrets
- **Single_Quotes** : Chaînes Groovy entre guillemets simples (`'...'`) qui ne font pas d'interpolation, sûres pour les secrets
- **Heredoc_Quoted** : Un heredoc shell dont le délimiteur est entre guillemets simples (`<< 'EOF'`), empêchant l'interpolation des variables par le shell parent
- **Credentials_Binding** : Le mécanisme Jenkins `credentials()` qui fournit des variables `_USR` et `_PSW` pour les identifiants
- **Step_sh** : L'étape Jenkins `sh` qui exécute une commande shell
- **Jenkinsfile** : Fichier de définition de pipeline (Jenkins-gateway, Jenkins-ml, Jenkins-chambres, Jenkins-patients et variantes CDK)
- **Secret** : Toute valeur sensible (mot de passe, nom d'utilisateur, clé SSH, adresse d'hôte) gérée par Jenkins Credentials

## Exigences

### Exigence 1 : Éliminer l'interpolation Groovy des secrets dans les étapes sh

**User Story :** En tant que DevOps, je veux que les secrets ne soient jamais passés aux étapes `sh` via l'interpolation Groovy, afin d'éliminer les avertissements Jenkins et empêcher toute fuite de secrets dans les logs de build.

#### Critères d'acceptation

1. THE Pipeline SHALL passer tous les secrets aux étapes Step_sh en utilisant exclusivement des Single_Quotes ou des variables d'environnement shell (notation `$VAR`), sans Interpolation_Groovy (notation `${VAR}`)
2. WHEN une étape Step_sh référence DOCKERHUB_CREDENTIALS_USR ou DOCKERHUB_CREDENTIALS_PSW, THE Pipeline SHALL utiliser la syntaxe Single_Quotes pour éviter l'Interpolation_Groovy
3. WHEN une étape Step_sh utilise `docker push` avec un nom d'image, THE Pipeline SHALL référencer la variable d'image via la syntaxe shell `$VAR` à l'intérieur de Single_Quotes, et non via l'Interpolation_Groovy
4. WHEN une commande SSH distante référence des secrets (DOCKERHUB_CREDENTIALS_USR, DOCKERHUB_CREDENTIALS_PSW), THE Pipeline SHALL utiliser un Heredoc_Quoted (`<< 'EOF'`) pour empêcher l'interpolation côté Jenkins
5. WHEN le Pipeline est exécuté, THE Pipeline SHALL produire zéro avertissement Jenkins de type "A secret was passed to 'sh' using Groovy String interpolation"

### Exigence 2 : Supprimer les logs verbeux et inutiles

**User Story :** En tant que DevOps, je veux réduire le bruit dans les logs de build en supprimant les echo redondants et les commandes de debug, afin d'avoir des logs lisibles et de minimiser l'exposition d'informations.

#### Critères d'acceptation

1. THE Pipeline SHALL supprimer les étapes `sh "echo 'Starting Docker build...'"` et `sh "echo 'Docker build completed.'"` redondantes dans les stages Build Image
2. THE Pipeline SHALL supprimer les étapes de debug `sh "docker --version"`, `sh "pwd"`, et `sh "ls -la"` des stages Build Image
3. WHEN une étape `docker login` est exécutée, THE Pipeline SHALL utiliser l'option `--quiet` ou rediriger la sortie pour éviter l'affichage de `+ docker login -u **** --password-stdin` dans les logs
4. THE Pipeline SHALL conserver uniquement les messages de log pertinents pour le suivi du déroulement du pipeline (succès/échec dans le bloc `post`)

### Exigence 3 : Sécuriser les connexions SSH dans les stages de déploiement

**User Story :** En tant que DevOps, je veux que les connexions SSH vers les serveurs EC2 soient sécurisées et que les variables sensibles (hôtes, utilisateurs) ne soient pas interpolées par Groovy, afin de réduire la surface d'attaque.

#### Critères d'acceptation

1. WHEN le Pipeline exécute une commande SSH vers un serveur distant, THE Pipeline SHALL passer les variables d'hôte et d'utilisateur (EC2_HOST, EC2_USER, GATEWAY_HOST, GATEWAY_USER, etc.) via la syntaxe shell `$VAR` à l'intérieur de Single_Quotes, et non via l'Interpolation_Groovy
2. WHEN le Pipeline utilise un heredoc pour les commandes distantes, THE Pipeline SHALL utiliser un Heredoc_Quoted (`<< 'EOF'`) pour empêcher l'expansion des variables côté Jenkins
3. WHEN le Pipeline utilise un heredoc avec des variables d'image Docker qui doivent être transmises au serveur distant, THE Pipeline SHALL exporter ces variables via des commandes `export` ou les passer comme variables d'environnement au début du heredoc
4. THE Pipeline SHALL utiliser `set +x` au début des blocs shell contenant des secrets pour désactiver le mode trace du shell

### Exigence 4 : Utiliser withCredentials pour isoler l'accès aux secrets

**User Story :** En tant que DevOps, je veux que les secrets soient accédés via le bloc `withCredentials` de Jenkins plutôt que via des variables d'environnement globales, afin de limiter la portée d'exposition des secrets aux seules étapes qui en ont besoin.

#### Critères d'acceptation

1. WHEN le Pipeline a besoin d'identifiants DockerHub, THE Pipeline SHALL utiliser un bloc `withCredentials([usernamePassword(...)])` autour des étapes `docker login` et `docker push` au lieu de déclarer les credentials dans le bloc `environment` global
2. WHEN le Pipeline utilise `withCredentials`, THE Pipeline SHALL déclarer les variables de binding avec le type `usernamePassword` et les paramètres `credentialsId`, `usernameVariable`, et `passwordVariable`
3. THE Pipeline SHALL limiter la portée des variables de secrets au bloc `withCredentials` le plus restreint possible

### Exigence 5 : Nettoyage sécurisé post-build

**User Story :** En tant que DevOps, je veux que le nettoyage post-build (docker logout, suppression d'images) soit fiable et ne génère pas d'erreurs, afin de garantir qu'aucune session Docker authentifiée ne persiste après le build.

#### Critères d'acceptation

1. THE Pipeline SHALL exécuter `docker logout` dans le bloc `post.always` sans encapsuler dans un bloc `node` redondant (le pipeline utilise déjà `agent any`)
2. IF l'étape `docker logout` échoue, THEN THE Pipeline SHALL ignorer l'erreur et continuer le nettoyage sans faire échouer le build
3. THE Pipeline SHALL supprimer les images Docker locales construites pendant le build dans le bloc `post.always` pour éviter l'accumulation d'images sur l'agent Jenkins

### Exigence 6 : Cohérence entre tous les Jenkinsfiles

**User Story :** En tant que DevOps, je veux que les corrections de sécurité soient appliquées de manière cohérente à tous les Jenkinsfiles du projet, afin d'éviter des régressions ou des oublis sur certains pipelines.

#### Critères d'acceptation

1. THE Pipeline SHALL appliquer les mêmes patterns de sécurité (Single_Quotes pour les secrets, Heredoc_Quoted, `withCredentials`, suppression des logs verbeux) à tous les Jenkinsfiles : Jenkins-gateway, Jenkins-gateway-cdk, Jenkins-ml, Jenkins-ml-cdk, Jenkins-chambres, Jenkins-chambres-cdk, Jenkins-patients
2. WHEN un Jenkinsfile utilise un stage Deploy to EC2 avec rebond SSH (jump host via `-J`), THE Pipeline SHALL appliquer les mêmes protections de secrets que pour les déploiements directs
3. THE Pipeline SHALL conserver la même structure fonctionnelle (stages Checkout, Build, Push, Deploy, post) dans chaque Jenkinsfile après les modifications de sécurité
