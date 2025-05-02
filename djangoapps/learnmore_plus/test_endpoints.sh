#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000"

# Function to reset the system
reset_system() {
    echo -e "\n${YELLOW}Resetting system to clean state...${NC}"
    ./reset_system.sh
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ System reset successful${NC}"
    else
        echo -e "${RED}✗ System reset failed${NC}"
        exit 1
    fi
}

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local expected_status=$3
    local description=$4
    local follow_redirects=${5:-false}
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $endpoint"
    
    # Add -L to follow redirects if requested
    local curl_opts="-s"
    if [ "$follow_redirects" = true ]; then
        curl_opts="$curl_opts -L"
    fi
    
    # Make the request
    response=$(curl $curl_opts -b cookies.txt "$BASE_URL$endpoint")
    status_code=$(curl $curl_opts -w "%{http_code}" -b cookies.txt "$BASE_URL$endpoint" -o /dev/null)
    
    # Check status code
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ Status code $status_code (expected $expected_status)${NC}"
    else
        echo -e "${RED}✗ Status code $status_code (expected $expected_status)${NC}"
        echo "Response:"
        echo "$response" | head -n 5
    fi
    
    # Check for error messages
    if echo "$response" | grep -q "error\|exception\|traceback"; then
        echo -e "${RED}✗ Error message found in response${NC}"
        echo "Error content:"
        echo "$response" | grep -A 2 -B 2 "error\|exception\|traceback"
    else
        echo -e "${GREEN}✓ No error messages found in response${NC}"
    fi
    
    echo "----------------------------------------"
}

# Function to login as a specific user
login_as() {
    local username=$1
    local password=$2
    local role=$3
    
    echo -e "\n${YELLOW}Logging in as $role ($username)${NC}"
    
    # Get CSRF token
    csrf_token=$(curl -s -c cookies.txt "$BASE_URL/accounts/login/" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | cut -d'"' -f4)
    
    # Login
    login_response=$(curl -s -c cookies.txt -b cookies.txt \
        -d "login=$username&password=$password&csrfmiddlewaretoken=$csrf_token" \
        -H "Referer: $BASE_URL/accounts/login/" \
        "$BASE_URL/accounts/login/")
    
    # Check for error messages
    if echo "$login_response" | grep -q "errorlist"; then
        echo -e "${RED}✗ Login failed${NC}"
        echo "Login response:"
        echo "$login_response" | grep -A 2 "errorlist"
        return 1
    fi
    
    # Verify login success by checking if we're redirected to dashboard
    if curl -s -b cookies.txt "$BASE_URL/courses/student/dashboard/" | grep -q "dashboard"; then
        echo -e "${GREEN}✓ Login successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Login failed - Not redirected to dashboard${NC}"
        return 1
    fi
}

# Function to register a new user
register_user() {
    local username=$1
    local email=$2
    local password=$3
    local first_name=$4
    local last_name=$5
    
    echo -e "\n${YELLOW}Registering new user: $username${NC}"
    
    # Get CSRF token
    csrf_token=$(curl -s -c cookies.txt "$BASE_URL/accounts/register/" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | cut -d'"' -f4)
    
    # Register with a strong password
    register_data="username=$username&email=$email&password1=$password&password2=$password&first_name=$first_name&last_name=$last_name&csrfmiddlewaretoken=$csrf_token"
    register_response=$(curl -s -c cookies.txt -b cookies.txt \
        -d "$register_data" \
        -H "Referer: $BASE_URL/accounts/register/" \
        "$BASE_URL/accounts/register/")
    
    # Check for error messages
    if echo "$register_response" | grep -q "errorlist"; then
        echo -e "${RED}✗ Registration failed${NC}"
        echo "Registration response:"
        echo "$register_response" | grep -A 2 "errorlist"
        return 1
    fi
    
    # Verify registration success by checking if we're redirected to dashboard
    if curl -s -b cookies.txt "$BASE_URL/courses/student/dashboard/" | grep -q "dashboard"; then
        echo -e "${GREEN}✓ Registration successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Registration failed - Not redirected to dashboard${NC}"
        return 1
    fi
}

# Function to enroll in a course
enroll_in_course() {
    local course_slug=$1
    
    echo -e "\n${YELLOW}Enrolling in course: $course_slug${NC}"
    
    # Get CSRF token
    csrf_token=$(curl -s -b cookies.txt "$BASE_URL/courses/course/$course_slug/enroll/" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | cut -d'"' -f4)
    
    # Enroll
    enroll_data="csrfmiddlewaretoken=$csrf_token"
    enroll_response=$(curl -s -c cookies.txt -b cookies.txt \
        -d "$enroll_data" \
        -H "Referer: $BASE_URL/courses/course/$course_slug/enroll/" \
        "$BASE_URL/courses/course/$course_slug/enroll/")
    
    # Verify enrollment success
    if echo "$enroll_response" | grep -q "Successfully enrolled"; then
        echo -e "${GREEN}✓ Enrollment successful${NC}"
        return 0
    else
        echo -e "${RED}✗ Enrollment failed${NC}"
        return 1
    fi
}

# Reset system to clean state
reset_system

# Test public endpoints
echo -e "\n${YELLOW}Testing Public Endpoints${NC}"
test_endpoint "/courses/catalog/" "GET" 200 "Course Catalog"
test_endpoint "/courses/course/non-existent-course/" "GET" 404 "Non-existent Course Detail"
test_endpoint "/accounts/login/" "GET" 200 "Login Page"
test_endpoint "/accounts/register/" "GET" 200 "Registration Page"

# Get a course slug for testing
course_slug=$(curl -s "$BASE_URL/courses/catalog/" | grep -o 'course/[^/]*/' | head -n1 | cut -d'/' -f2)
if [ -z "$course_slug" ]; then
    echo -e "${RED}Could not find a course slug to test with${NC}"
    exit 1
fi

# Test user registration and course enrollment
echo -e "\n${YELLOW}Testing User Registration and Course Enrollment${NC}"
register_user "test.student" "test@example.com" "TestStudent123!" "Test" "Student"
if [ $? -eq 0 ]; then
    # Test student endpoints
    test_endpoint "/courses/student/dashboard/" "GET" 200 "Student Dashboard"
    test_endpoint "/courses/student/progress/" "GET" 200 "Learning Progress"
    
    # Enroll in course
    enroll_in_course "$course_slug"
    if [ $? -eq 0 ]; then
        # Test course access after enrollment
        test_endpoint "/courses/course/$course_slug/learn/" "GET" 200 "Course Learning Interface"
        test_endpoint "/courses/course/$course_slug/progress/" "GET" 200 "Course Progress"
    fi
fi

# Reset system
reset_system

# Test as Admin
login_as "admin" "admin123" "Administrator"
if [ $? -eq 0 ]; then
    echo -e "\n${YELLOW}Testing Admin Endpoints${NC}"
    test_endpoint "/admin/" "GET" 200 "Admin Dashboard"
    test_endpoint "/courses/student/dashboard/" "GET" 200 "Student Dashboard"
    test_endpoint "/courses/instructor/dashboard/" "GET" 200 "Instructor Dashboard"
    test_endpoint "/courses/coordinator/courses/" "GET" 200 "Course Management"
    test_endpoint "/courses/course/$course_slug/manage/content/" "GET" 200 "Course Content Management"
    test_endpoint "/courses/course/$course_slug/manage/instructors/" "GET" 200 "Course Instructor Management"
    test_endpoint "/courses/course/$course_slug/analytics/" "GET" 200 "Course Analytics"
fi

# Reset system
reset_system

# Test as Course Coordinator
login_as "coordinator" "coord123" "Course Coordinator"
if [ $? -eq 0 ]; then
    echo -e "\n${YELLOW}Testing Course Coordinator Endpoints${NC}"
    test_endpoint "/courses/coordinator/courses/" "GET" 200 "Course Management"
    test_endpoint "/courses/course/$course_slug/manage/content/" "GET" 200 "Course Content Management"
    test_endpoint "/courses/course/$course_slug/manage/instructors/" "GET" 200 "Course Instructor Management"
    test_endpoint "/courses/course/$course_slug/analytics/" "GET" 200 "Course Analytics"
    test_endpoint "/admin/" "GET" 302 "Admin Dashboard (Not Authorized)"
fi

# Reset system
reset_system

# Test as Instructor
login_as "dr.smith" "dr.smith123" "Instructor"
if [ $? -eq 0 ]; then
    echo -e "\n${YELLOW}Testing Instructor Endpoints${NC}"
    test_endpoint "/courses/instructor/dashboard/" "GET" 200 "Instructor Dashboard"
    test_endpoint "/courses/course/$course_slug/manage/content/" "GET" 200 "Course Content Management"
    test_endpoint "/courses/course/$course_slug/manage/instructors/" "GET" 302 "Course Instructor Management (Not Authorized)"
    test_endpoint "/courses/course/$course_slug/analytics/" "GET" 200 "Course Analytics"
    test_endpoint "/courses/coordinator/courses/" "GET" 302 "Course Management (Not Authorized)"
    test_endpoint "/admin/" "GET" 302 "Admin Dashboard (Not Authorized)"
fi

# Reset system
reset_system

# Test as Student
login_as "john.doe" "john.doe123" "Student"
if [ $? -eq 0 ]; then
    echo -e "\n${YELLOW}Testing Student Endpoints${NC}"
    test_endpoint "/courses/student/dashboard/" "GET" 200 "Student Dashboard"
    test_endpoint "/courses/student/progress/" "GET" 200 "Learning Progress"
    test_endpoint "/courses/course/$course_slug/" "GET" 200 "Course Detail"
    test_endpoint "/courses/course/$course_slug/enroll/" "GET" 200 "Course Enrollment Page"
    test_endpoint "/courses/course/$course_slug/learn/" "GET" 302 "Course Learning Interface (Not Enrolled)"
    test_endpoint "/courses/course/$course_slug/manage/content/" "GET" 302 "Course Content Management (Not Authorized)"
    test_endpoint "/courses/course/$course_slug/manage/instructors/" "GET" 302 "Course Instructor Management (Not Authorized)"
    test_endpoint "/courses/course/$course_slug/analytics/" "GET" 302 "Course Analytics (Not Authorized)"
    test_endpoint "/courses/instructor/dashboard/" "GET" 302 "Instructor Dashboard (Not Authorized)"
    test_endpoint "/courses/coordinator/courses/" "GET" 302 "Course Management (Not Authorized)"
    test_endpoint "/admin/" "GET" 302 "Admin Dashboard (Not Authorized)"
    
    # Test course enrollment
    enroll_in_course "$course_slug"
    if [ $? -eq 0 ]; then
        # Test course access after enrollment
        test_endpoint "/courses/course/$course_slug/learn/" "GET" 200 "Course Learning Interface"
        test_endpoint "/courses/course/$course_slug/progress/" "GET" 200 "Course Progress"
    fi
fi

# Test unauthenticated access to protected endpoints
echo -e "\n${YELLOW}Testing Unauthenticated Access to Protected Endpoints${NC}"
rm -f cookies.txt  # Remove cookies to test as unauthenticated user
test_endpoint "/courses/student/dashboard/" "GET" 302 "Student Dashboard (Unauthenticated)"
test_endpoint "/courses/instructor/dashboard/" "GET" 302 "Instructor Dashboard (Unauthenticated)"
test_endpoint "/courses/coordinator/courses/" "GET" 302 "Course Management (Unauthenticated)"
test_endpoint "/courses/course/$course_slug/manage/content/" "GET" 302 "Course Content Management (Unauthenticated)"
test_endpoint "/admin/" "GET" 302 "Admin Dashboard (Unauthenticated)"

# Final system reset
reset_system

# Clean up
rm -f cookies.txt

echo -e "\n${GREEN}Testing complete!${NC}" 