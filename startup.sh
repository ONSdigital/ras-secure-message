#!/bin/sh



# Run all migrations on the database.
alembic upgrade head
# Start the backend...