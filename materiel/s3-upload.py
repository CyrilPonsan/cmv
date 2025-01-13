import time
import os
import boto3
from botocore.exceptions import ClientError
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import configparser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="/var/log/s3-upload.log",  # Log to system file on EC2
)
logger = logging.getLogger(__name__)

# Also log to console for systemd service visibility
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class S3UploadHandler(FileSystemEventHandler):
    def __init__(self, bucket_name, folder_to_watch):
        self.bucket_name = bucket_name
        self.folder_to_watch = folder_to_watch

        try:
            # Use EC2 instance role credentials automatically
            self.s3_client = boto3.client("s3")

            # Verify bucket access
            self.s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Successfully connected to S3 bucket: {bucket_name}")

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "403":
                logger.error(
                    "Access denied to S3 bucket. Please check EC2 instance role permissions."
                )
            elif error_code == "404":
                logger.error("Bucket not found. Please check the bucket name.")
            else:
                logger.error(f"Error connecting to S3: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {str(e)}")
            raise

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Wait for file to be completely written
        time.sleep(1)

        try:
            # Get the relative path from the watched folder
            relative_path = os.path.relpath(file_path, self.folder_to_watch)

            # Set up private ACL and server-side encryption
            extra_args = {"ServerSideEncryption": "AES256"}

            # Upload file to S3
            logger.info(f"Uploading {file_path} to S3...")
            self.s3_client.upload_file(
                file_path, self.bucket_name, relative_path, ExtraArgs=extra_args
            )
            logger.info(
                f"Successfully uploaded {relative_path} to S3 bucket {self.bucket_name}"
            )

        except ClientError as e:
            logger.error(f"S3 upload error for {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading {file_path}: {str(e)}")


def load_config():
    config = configparser.ConfigParser()
    config_file = "/etc/s3-upload/config.ini"

    if not os.path.exists(config_file):
        # Create default config file
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        config["S3"] = {"bucket_name": "your-private-bucket-name"}
        config["LOCAL"] = {"folder_to_watch": "/path/to/your/folder"}

        with open(config_file, "w") as f:
            config.write(f)

        logger.info(f"Created default config file: {config_file}")
        logger.info(
            "Please update the config file with your settings before running again."
        )
        exit(1)

    config.read(config_file)
    return config


def start_monitoring():
    # Load configuration
    config = load_config()

    # Get settings
    bucket_name = config["S3"]["bucket_name"]
    folder_to_watch = config["LOCAL"]["folder_to_watch"]

    # Create an observer and handler
    event_handler = S3UploadHandler(bucket_name, folder_to_watch)
    observer = Observer()

    # Schedule the observer to watch the folder
    observer.schedule(event_handler, folder_to_watch, recursive=True)

    # Start the observer
    observer.start()
    logger.info(f"Started monitoring folder: {folder_to_watch}")
    logger.info(f"Files will be uploaded to private S3 bucket: {bucket_name}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("\nStopped monitoring folder")

    observer.join()


if __name__ == "__main__":
    start_monitoring()
