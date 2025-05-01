export enum ResponseMessages {
    // success messages
    USER_CREATED = 'User created successfully',
    USER_UPDATED = 'User updated successfully',
    USER_DELETED = 'User deleted successfully',
    USER_LOGGED_IN = 'User logged in successfully',
    USER_LOGGED_OUT = 'User logged out successfully',
    USER_RETRIEVED = "User profile retrieved successfully",

    // error messages
    USER_NOT_FOUND = 'User not found',
    USER_ALREADY_EXISTS = 'User already exists',
    INVALID_CREDENTIALS = 'Invalid credentials',
    SERVICE_ERROR = 'Upstream Service Error',
    SERVICE_UNAVAILABLE = 'Service Unreachable',
    INTERNAL_SERVER_ERROR = 'Unknown error'
}
