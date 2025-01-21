import os

# Define the environment variables for each service
env_configs = {
    # Destiné au développement et aux tests
    "cmv_gateway/cmv_back/.env": {
        "GATEWAY_DATABASE_URL": "postgresql://postgres:cmv_gateway@localhost:6001/cmv_gateway",
        "GATEWAY_POSTGRES_USER": "postgres",
        "GATEWAY_POSTGRES_PASSWORD": "cmv_gateway",
        "GATEWAY_POSTGRES_DB": "cmv_gateway",
        "SECRET_KEY": "cle_tres_tres_tres_secrete",
        "ALGORITHM": "HS256",
        "PATIENTS_SERVICE": "http://localhost:8002/api",
        "CHAMBRES_SERVICE": "http://localhost:8003/api",
        "ACCESS_MAX_AGE": "30",
        "REFRESH_MAX_AGE": "1440",
        "ENVIRONMENT": "development",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
    },  # Destiné au développement et aux tests
    "cmv_gateway/cmv_front/.env": {
        "VITE_ENVIRONMENT": "dev",
    },  # Destiné au développement et aux tests
    "cmv_patients/.env": {
        "PATIENTS_DATABASE_URL": "postgresql://postgres:cmv_patients@localhost:6002/cmv_patients",
        "PATIENTS_POSTGRES_USER": "postgres",
        "PATIENTS_POSTGRES_PASSWORD": "cmv_patients",
        "PATIENTS_POSTGRES_DB": "cmv_patients",
        "SECRET_KEY": "cle_tres_tres_tres_secrete",
        "ALGORITHM": "HS256",
        "ENVIRONMENT": "development",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
        "AWS_BUCKET_NAME": "nom_du_bucker",
        "AWS_ACCESS_KEY_ID": "aws_access_key_id",
        "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
        "AWS_REGION": "aws_region",
    },
    "cmv_chambres/.env": {
        "CHAMBRES_DATABASE_URL": "postgresql://postgres:cmv_chambres@localhost:6003/cmv_chambres",
        "CHAMBRES_POSTGRES_USER": "postgres",
        "CHAMBRES_POSTGRES_PASSWORD": "cmv_chambres",
        "CHAMBRES_POSTGRES_DB": "cmv_chambres",
        "SECRET_KEY": "cle_tres_tres_tres_secrete",
        "ALGORITHM": "HS256",
        "ENVIRONMENT": "development",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
    },
    # Destiné à la production ou préparation à la production
    "./env": {
        "GATEWAY_POSTGRES_URL": "postgresql://postgres:cmv_gateway@db_gateway:5432/cmv_gateway",
        "PATIENTS_DATABASE_URL": "postgresql://postgres:cmv_patients@db_patients:5432/cmv_patients",
        "CHAMBRES_DATABASE_URL": "postgresql://postgres:cmv_chambres@db_chambres:5432/cmv_chambres",
        "GATEWAY_POSTGRES_USER": "postgres",
        "GATEWAY_POSTGRES_PASSWORD": "cmv_gateway",
        "GATEWAY_POSTGRES_DB": "cmv_gateway",
        "PATIENTS_POSTGRES_USER": "postgres",
        "PATIENTS_POSTGRES_PASSWORD": "cmv_patients",
        "PATIENTS_POSTGRES_DB": "cmv_patients",
        "CHAMBRES_POSTGRES_USER": "postgres",
        "CHAMBRES_POSTGRES_PASSWORD": "cmv_chambres",
        "CHAMBRES_POSTGRES_DB": "cmv_chambres",
        "MY_NETWORK": "cmv",
        "SECRET_KEY": "cle_tres_tres_tres_secrete",
        "ALGORITHM": "HS256",
        "ACCESS_MAX_AGE": "20",
        "REFRESH_MAX_AGE": "60",
        "PATIENTS_SERVICE": "http://api_patients:8000/api",
        "CHAMBRES_SERVICE": "http://api_chambres:8000/api",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
        "TEST_GATEWAY_POSTGRES_DB": "test-gateway",
        "AWS_BUCKET_NAME": "nom_du_bucker",
        "AWS_ACCESS_KEY_ID": "aws_access_key_id",
        "AWS_SECRET_ACCESS_KEY": "aws_secret_access_key",
        "AWS_REGION": "aws_region",
        "ENVIRONMENT": "production",
        "VITE_ENVIRONMENT": "production",
    },
}


def create_env_files():
    """Create .env files for each service with example values."""
    for file_path, config in env_configs.items():
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the .env file
        with open(file_path, "w") as f:
            for key, value in config.items():
                f.write(f'{key}="{value}"\n')
        print(f"Created {file_path}")


if __name__ == "__main__":
    create_env_files()
