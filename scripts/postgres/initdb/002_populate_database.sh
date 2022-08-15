in_database_run() {
    psql --username "${OCTONN_USER}" --dbname "${OCTONN_DB}" -f "$1"
}

for file in ${MIGRATION_PATH}/*.up.sql
do
    in_database_run ${file}
done
