#!/bin/bash

# Suppressed Email Checker API Test Script
# Make sure the API is running before executing this script

API_BASE_URL="http://localhost:8000"

echo "🚀 Testing Suppressed Email Checker API"
echo "========================================"

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s -X GET "$API_BASE_URL/health" | jq
echo ""

# Test 2: Root Endpoint
echo "2. Testing Root Endpoint..."
curl -s -X GET "$API_BASE_URL/" | jq
echo ""

# Test 3: Suppressed Emails
echo "3. Testing Suppressed Emails..."
emails=("recipient0@example.com" "recipient1@example.com" "recipient2@example.com")

for email in "${emails[@]}"; do
    echo "   Testing: $email"
    curl -s -X POST "$API_BASE_URL/check-email" \
         -H "Content-Type: application/json" \
         -d "{\"email\": \"$email\"}" | jq
    echo "   ---"
done

# Test 4: Non-suppressed Email
echo "4. Testing Non-suppressed Email..."
curl -s -X POST "$API_BASE_URL/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "valid@example.com"}' | jq
echo ""

# Test 5: Invalid Email Format
echo "5. Testing Invalid Email Format..."
curl -s -X POST "$API_BASE_URL/check-email" \
     -H "Content-Type: application/json" \
     -d '{"email": "invalid-email"}' | jq
echo ""

# Test 6: Missing Email Field
echo "6. Testing Missing Email Field..."
curl -s -X POST "$API_BASE_URL/check-email" \
     -H "Content-Type: application/json" \
     -d '{}' | jq
echo ""

echo "✅ API Testing Complete!"
