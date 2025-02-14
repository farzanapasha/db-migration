import mysql.connector
import os

# MySQL Connection Configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

# SQL Migration Files Directory
MIGRATIONS_DIR = "./migrations"

def apply_migrations():
    """Applies all new SQL migration files in order."""
    try:
        # Establish database connection
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Retrieve applied migrations
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (id INT AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(255) UNIQUE)")
        conn.commit()
        cursor.execute("SELECT filename FROM schema_migrations")
        applied_migrations = {row[0] for row in cursor.fetchall()}

        # Process migration files
        for file in sorted(os.listdir(MIGRATIONS_DIR)):
            if file.endswith(".sql") and file not in applied_migrations:
                print(f"Applying migration: {file}")
                with open(os.path.join(MIGRATIONS_DIR, file), "r") as f:
                    sql_commands = f.read()

                try:
                    for statement in sql_commands.split(";"):
                        if statement.strip():
                            cursor.execute(statement)

                    # Record migration in database
                    cursor.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (file,))
                    conn.commit()
                    print(f"Migration {file} applied successfully.")

                except mysql.connector.Error as err:
                    conn.rollback()
                    print(f"Error applying {file}: {err}")
                    break  # Stop execution if an error occurs

        cursor.close()
        conn.close()
        print("Database migrations completed.")
    
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")

if __name__ == "__main__":
    apply_migrations()

