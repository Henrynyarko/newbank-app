# Use official Postgres image
FROM postgres:15

# Copy initialization scripts into Docker image
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Expose default Postgres port
EXPOSE 5432
