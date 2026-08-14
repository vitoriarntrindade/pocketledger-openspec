## Purpose

Lets an authenticated user view their own account details, kept as a distinct concern from the login/token mechanics handled by authentication.

## ADDED Requirements

### Requirement: View Own Profile
The system SHALL allow an authenticated user to retrieve their own account's id, name, and email.

#### Scenario: Successful profile retrieval
- **WHEN** an authenticated user requests their own profile
- **THEN** the system returns that user's id, name, and email

#### Scenario: Unauthenticated request rejected
- **WHEN** a request for the profile carries no valid access token
- **THEN** the system rejects the request with a 401 error

### Requirement: No Cross-User Profile Access
The system SHALL only ever expose the authenticated user's own profile. No endpoint SHALL allow a user to look up another user's profile by id, email, or any other identifier.

#### Scenario: No lookup-by-id path exists
- **WHEN** an authenticated user attempts to retrieve profile data for any account other than their own
- **THEN** the system has no endpoint that returns another user's profile, and any such attempt fails to resolve to another user's data
