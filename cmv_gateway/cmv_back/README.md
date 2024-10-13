Créer une image docker pour l'api :
$ docker build -t svelte-poste-api .

Créer une image pour postgresql :
$ docker run --name pg-svelte-poste -e POSTGRES_PASSWORD=<POSTGRES_PASSWORD> -dp 5500:5432 postgres

Créer un réseau :
$ docker network create <MY_NETWORK>

A l'aide d'un outil graphique comme dbeaver ou en ligne de commande créer la base de données svelte-poste.
Exécuter les containers à l'aide docker-compose :
$ docker-compose up -d

Pour stopper l'API et le serveur de base de données :
$ docker-compose down

note : les valeurs entourées de chevrons se trouvent dans le fichier .env
