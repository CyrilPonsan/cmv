import shutil
import os
import logging

# Configuration du logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

ACTIVE_DB_FILE = "app.db"
BACKUP_DB_FILE = "backup.db"

SUCCESS_BACKUP_MSG = "Database backed up successfully."
SUCCESS_RESTORE_MSG = "Database restored successfully."
ERROR_NOT_FOUND_MSG = "Error: {} not found."
ERROR_PERMISSION_MSG = "Error: Permission denied while accessing {} or {}."
ERROR_UNEXPECTED_MSG = "An unexpected error occurred: {}"
MENU_OPTIONS = """
1. Backup Database
2. Restore Database
3. Exit
"""


def backup_db() -> None:
    try:
        if not os.path.exists(ACTIVE_DB_FILE):
            raise FileNotFoundError(ACTIVE_DB_FILE)
        shutil.copy(ACTIVE_DB_FILE, BACKUP_DB_FILE)
        print(SUCCESS_BACKUP_MSG)
        logging.info(SUCCESS_BACKUP_MSG)
    except FileNotFoundError:
        error_msg = ERROR_NOT_FOUND_MSG.format(ACTIVE_DB_FILE)
        print(error_msg)
        logging.error(error_msg)
    except PermissionError:
        error_msg = ERROR_PERMISSION_MSG.format(ACTIVE_DB_FILE, BACKUP_DB_FILE)
        print(error_msg)
        logging.error(error_msg)
    except Exception as e:
        error_msg = ERROR_UNEXPECTED_MSG.format(e)
        print(error_msg)
        logging.error(error_msg)


def restore_db() -> None:
    try:
        if not os.path.exists(BACKUP_DB_FILE):
            raise FileNotFoundError(BACKUP_DB_FILE)
        shutil.copy(BACKUP_DB_FILE, ACTIVE_DB_FILE)
        print(SUCCESS_RESTORE_MSG)
        logging.info(SUCCESS_RESTORE_MSG)
    except FileNotFoundError:
        error_msg = ERROR_NOT_FOUND_MSG.format(BACKUP_DB_FILE)
        print(error_msg)
        logging.error(error_msg)
    except PermissionError:
        error_msg = ERROR_PERMISSION_MSG.format(BACKUP_DB_FILE, ACTIVE_DB_FILE)
        print(error_msg)
        logging.error(error_msg)
    except Exception as e:
        error_msg = ERROR_UNEXPECTED_MSG.format(e)
        print(error_msg)
        logging.error(error_msg)


def display_menu() -> None:
    print(MENU_OPTIONS)


def main() -> None:
    choice = ""
    while choice != "3":
        display_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            backup_db()
        elif choice == "2":
            restore_db()
        elif choice == "3":
            print("Exiting...")
            logging.info("Exiting the application.")
        else:
            print("Invalid choice. Please try again.")
            logging.warning("Invalid choice entered.")


if __name__ == "__main__":
    main()
