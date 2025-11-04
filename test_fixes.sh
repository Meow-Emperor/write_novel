#!/bin/bash

echo "=== Testing Bug Fixes ==="
echo ""

echo "1. Checking docker-compose.yml..."
grep -A 2 "DATABASE_URL" docker-compose.yml
echo ""

echo "2. Checking Novel model relationships..."
grep -A 5 "# Relationships" backend/app/models/novel.py
echo ""

echo "3. Checking all API routes are registered..."
grep "include_router" backend/app/main.py
echo ""

echo "4. Checking frontend views exist..."
ls -la frontend/src/views/ | grep -E "(Character|Plot|World|Chapter|Content)" 
echo ""

echo "5. Checking routes are configured..."
grep -E "(characters|plot|world|chapters|editor)" frontend/src/router/index.ts
echo ""

echo "=== All checks completed ==="
