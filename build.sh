#!/usr/bin/env bash
# Script de build para Render
# Este script se ejecuta automáticamente en cada deploy

set -o errexit  # Salir si hay error

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
