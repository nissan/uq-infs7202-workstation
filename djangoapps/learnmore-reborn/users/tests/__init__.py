# users tests package
# Import the API tests to ensure they are discovered
from users.api_tests import UserAPITests
from users.serializer_tests import (
    UserSerializerValidationTest,
    UserProfileSerializerValidationTest,
    LoginSerializerValidationTest,
    GoogleAuthSerializerValidationTest
)