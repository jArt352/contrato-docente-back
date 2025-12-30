#!/usr/bin/env bash
# Script de build para Render
# Este script se ejecuta automáticamente en cada deploy

set -o errexit  # Salir si hay error

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Build completed successfully!"
