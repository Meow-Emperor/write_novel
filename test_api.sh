#!/bin/bash

API_URL=${1:-http://localhost:8000}

echo "=== Testing AI Novel Platform API ==="
echo "API URL: $API_URL"
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | jq .
echo ""

# Test root endpoint
echo "2. Testing root endpoint..."
curl -s "$API_URL/" | jq .
echo ""

# Test novel creation
echo "3. Creating a test novel..."
NOVEL_ID=$(curl -s -X POST "$API_URL/api/novels/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试小说",
    "author": "测试作者",
    "genre": "奇幻",
    "description": "这是一个测试小说"
  }' | jq -r '.id')

if [ "$NOVEL_ID" != "null" ]; then
  echo "✓ Novel created with ID: $NOVEL_ID"
else
  echo "✗ Failed to create novel"
  exit 1
fi
echo ""

# Test character creation
echo "4. Creating a test character..."
CHARACTER_ID=$(curl -s -X POST "$API_URL/api/characters/" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "'$NOVEL_ID'",
    "name": "测试角色",
    "role": "protagonist",
    "description": "主角描述"
  }' | jq -r '.id')

if [ "$CHARACTER_ID" != "null" ]; then
  echo "✓ Character created with ID: $CHARACTER_ID"
else
  echo "✗ Failed to create character"
fi
echo ""

# Test plot creation
echo "5. Creating a test plot..."
PLOT_ID=$(curl -s -X POST "$API_URL/api/plots/" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "'$NOVEL_ID'",
    "title": "主线情节",
    "plot_type": "main",
    "order": 1
  }' | jq -r '.id')

if [ "$PLOT_ID" != "null" ]; then
  echo "✓ Plot created with ID: $PLOT_ID"
else
  echo "✗ Failed to create plot"
fi
echo ""

# Test chapter creation
echo "6. Creating a test chapter..."
CHAPTER_ID=$(curl -s -X POST "$API_URL/api/chapters/" \
  -H "Content-Type: application/json" \
  -d '{
    "novel_id": "'$NOVEL_ID'",
    "title": "第一章",
    "chapter_number": 1,
    "summary": "第一章摘要"
  }' | jq -r '.id')

if [ "$CHAPTER_ID" != "null" ]; then
  echo "✓ Chapter created with ID: $CHAPTER_ID"
else
  echo "✗ Failed to create chapter"
fi
echo ""

# Test list endpoints
echo "7. Testing list endpoints..."
echo "Novels:"
curl -s "$API_URL/api/novels/" | jq 'length'
echo "Characters:"
curl -s "$API_URL/api/characters/?novel_id=$NOVEL_ID" | jq 'length'
echo "Plots:"
curl -s "$API_URL/api/plots/?novel_id=$NOVEL_ID" | jq 'length'
echo "Chapters:"
curl -s "$API_URL/api/chapters/?novel_id=$NOVEL_ID" | jq 'length'
echo ""

# Test admin registration
echo "8. Testing admin registration..."
ADMIN_TOKEN=$(curl -s -X POST "$API_URL/api/admin/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testadmin",
    "email": "test@admin.com",
    "password": "admin123",
    "full_name": "Test Admin"
  }' | jq -r '.id')

if [ "$ADMIN_TOKEN" != "null" ]; then
  echo "✓ Admin registered"
  
  # Try login
  echo "9. Testing admin login..."
  TOKEN=$(curl -s -X POST "$API_URL/api/admin/login" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "testadmin",
      "password": "admin123"
    }' | jq -r '.access_token')
  
  if [ "$TOKEN" != "null" ]; then
    echo "✓ Admin logged in successfully"
    
    # Test admin stats
    echo "10. Testing admin stats..."
    curl -s "$API_URL/api/admin/stats" \
      -H "Authorization: Bearer $TOKEN" | jq .
  else
    echo "✗ Failed to login"
  fi
else
  echo "Note: Admin might already exist, skipping..."
fi
echo ""

echo "=== API Tests Complete ==="
echo ""
echo "Created resources:"
echo "  Novel ID: $NOVEL_ID"
echo "  Character ID: $CHARACTER_ID"
echo "  Plot ID: $PLOT_ID"
echo "  Chapter ID: $CHAPTER_ID"
echo ""
echo "To clean up, delete the novel (will cascade delete all related data):"
echo "  curl -X DELETE $API_URL/api/novels/$NOVEL_ID"
