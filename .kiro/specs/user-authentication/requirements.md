# Requirements Document

## Introduction

This feature implements a comprehensive user authentication and configuration management system for the IPTV Series Browser application. The system will handle user credentials, server configurations, user information retrieval via API, and support for multiple user accounts with separate search caching per user.

## Requirements

### Requirement 1

**User Story:** As a new user, I want to be prompted to enter my server details and credentials when I first launch the app, so that I can connect to my IPTV service if the config.py was not found or  populated

#### Acceptance Criteria

1. WHEN the application starts AND no configuration exists THEN the system SHALL redirect the user to a configuration setup page
2. WHEN the user is on the setup page THEN the system SHALL display form fields for server URL, username, and password
3. WHEN the user submits valid configuration details THEN the system SHALL validate the connection using the player API
4. WHEN the API validation succeeds THEN the system SHALL save the configuration and redirect to the main application
5. WHEN the API validation fails THEN the system SHALL display an error message and allow the user to retry

### Requirement 2

**User Story:** As a user, I want the system to retrieve and display my account information from the IPTV service, so that I can verify my connection and see my account details.

#### Acceptance Criteria

1. WHEN the user successfully connects THEN the system SHALL call the player API endpoint: `{{server}}/player_api.php?username={{username}}&password={{password}}`
2. WHEN the API call succeeds THEN the system SHALL parse and store both user_info and server_info from the response into config.py
3. WHEN user information is available THEN the system SHALL display account status, expiry date, connection limits, and allowed formats
4. IF the API call fails OR auth field is not 1 THEN the system SHALL display an appropriate error message
5. WHEN user information is displayed THEN it SHALL include status, expiry date, max connections, active connections, and trial status

### Requirement 3

**User Story:** As a user, I want to be able to logout and clear my stored configuration, so that I can protect my credentials or switch to a different account.

#### Acceptance Criteria

1. WHEN the user clicks logout THEN the system SHALL clear all stored configuration data of that user
2. WHEN the user clicks logout THEN the system SHALL clear all cached search data for the current user
3. WHEN logout is complete THEN the system SHALL redirect the user to the configuration setup page
4. WHEN the user confirms logout THEN the system SHALL display a confirmation dialog before proceeding
5. WHEN configuration is cleared THEN the system SHALL ensure no sensitive data remains in local storage

### Requirement 4

**User Story:** As a user, I want to be able to add multiple user accounts and switch between them, so that I can manage different IPTV services or family accounts.

#### Acceptance Criteria

1. WHEN the user has an existing configuration THEN the system SHALL provide an option to add additional users
2. WHEN adding a new user THEN the system SHALL display the same configuration form as initial setup
3. WHEN multiple users exist THEN the system SHALL display a user selection interface
4. WHEN switching users THEN the system SHALL maintain separate search caches for each user account
5. WHEN displaying multiple users THEN the system SHALL show identifying information (server/username) for each account




### Requirement 6

**User Story:** As a user, I want to view and manage my current configuration settings, so that I can update my credentials or server information when needed.

#### Acceptance Criteria

1. WHEN the user accesses user info THEN the system SHALL display current server URL, username, and connection status
2. WHEN the user wants to edit configuration THEN the system SHALL provide an edit interface with current values pre-filled
3. WHEN configuration is updated THEN the system SHALL validate the new settings before saving
4. WHEN validation fails THEN the system SHALL display specific error messages and retain the edit interface
5. WHEN configuration is successfully updated THEN the system SHALL refresh the user information from the API

### Requirement 7

**User Story:** As a user, I want the system to handle connection errors gracefully, so that I can understand and resolve connectivity issues.

#### Acceptance Criteria

1. WHEN the API is unreachable THEN the system SHALL display a clear network error message
2. WHEN credentials are invalid THEN the system SHALL display an authentication error message
3. WHEN the server URL is malformed THEN the system SHALL display a URL format error message
4. WHEN connection times out THEN the system SHALL display a timeout error and suggest retry
5. WHEN any error occurs THEN the system SHALL log the error details for debugging purposes