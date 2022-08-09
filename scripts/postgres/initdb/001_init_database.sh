set -e

psql_command() {
    psql --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" -c "$1"
}

psql_command "CREATE DATABASE ${OCTONN_DB};"
psql_command "CREATE USER ${OCTONN_USER} PASSWORD 'sdh45walth27xndsk6';"
psql_command "GRANT ALL ON DATABASE ${OCTONN_DB} TO ${OCTONN_USER};"
