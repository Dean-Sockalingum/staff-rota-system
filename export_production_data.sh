#!/bin/bash
# Export production data using Django dumpdata
# This can be run on the production server

echo "Exporting production database..."

# Export in chunks to avoid memory issues
python manage.py dumpdata scheduling.CareHome --indent 2 > care_homes.json
python manage.py dumpdata scheduling.Unit --indent 2 > units.json
python manage.py dumpdata scheduling.Role --indent 2 > roles.json
python manage.py dumpdata scheduling.User --indent 2 > users.json
python manage.py dumpdata scheduling.Shift --indent 2 > shifts.json

echo "Done! Files created:"
ls -lh *.json
