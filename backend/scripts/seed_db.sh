#!/bin/bash

# Database seeding script using SQL
# This script creates an admin user and default knowledge base

set -e

# Default values
ADMIN_USERNAME=${ADMIN_USERNAME:-"superadmin"}
ADMIN_EMAIL=${ADMIN_EMAIL:-"superadmin@example.com"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"superadmin123"}
DB_HOST=${POSTGRESQL_SERVER:-"db"}
DB_PORT=${POSTGRESQL_PORT:-"5432"}
DB_NAME=${POSTGRESQL_DATABASE:-"llmops"}
DB_USER=${POSTGRESQL_USER:-"llmops"}
DB_PASSWORD=${POSTGRESQL_PASSWORD:-"llmops"}

echo "🌱 Starting database seeding..."

# Function to generate bcrypt hash using Python (one-time use)
generate_bcrypt_hash() {
    local password="$1"
    python3 -c "
import sys
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('$password'))
"
}

# Generate password hash
echo "Generating password hash..."
HASHED_PASSWORD=$(generate_bcrypt_hash "$ADMIN_PASSWORD")

# Create SQL script
SQL_FILE="/tmp/seed_data.sql"
cat > "$SQL_FILE" << EOF
-- Database seeding script
-- This script creates an admin user and default knowledge base

-- Insert admin user (only if not exists)
INSERT INTO users (username, email, hashed_password, is_active, is_superuser, created_at, updated_at)
SELECT '$ADMIN_USERNAME', '$ADMIN_EMAIL', '$HASHED_PASSWORD', true, true, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = '$ADMIN_USERNAME' OR email = '$ADMIN_EMAIL'
);
EOF

echo "Executing SQL seeding script..."

# Execute SQL script
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database seeding completed successfully!"
    echo "�� Admin credentials:"
    echo "   Username: $ADMIN_USERNAME"
    echo "   Email: $ADMIN_EMAIL"
    echo "   Password: $ADMIN_PASSWORD"
    echo "   Role: Superuser"
else
    echo "❌ Database seeding failed!"
    exit 1
fi

# Clean up
rm -f "$SQL_FILE"
