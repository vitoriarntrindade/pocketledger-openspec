# Auth Specification

## Purpose

Handles new-user registration and JWT-based login so that every subsequent request can be tied to exactly one authenticated user and no one else's data.

## Requirements

### Requirement: User Registration
The system SHALL allow a new user to register by providing a name, an email address, and a password, creating a unique account identified by that email.

#### Scenario: Successful registration
- **WHEN** a client submits a name, a previously unused email, and a password meeting the minimum length requirement
- **THEN** the system creates a new user account and does not include the password in the response

#### Scenario: Duplicate email rejected
- **WHEN** a client submits a registration with an email that already belongs to an existing account
- **THEN** the system rejects the registration with a 4xx error and does not create a second account

#### Scenario: Password below minimum length rejected
- **WHEN** a client submits a registration with a password shorter than the minimum required length
- **THEN** the system rejects the registration with a validation error

### Requirement: Password Storage
The system SHALL store passwords only as an irreversible hash and SHALL NOT store or return plaintext passwords at any point.

#### Scenario: Password never exposed
- **WHEN** any endpoint returns user data, including the registration and login responses
- **THEN** the response never contains the plaintext or hashed password

### Requirement: Login and Token Issuance
The system SHALL allow a registered user to authenticate with their email and password and, on success, SHALL issue a JWT access token identifying that user.

#### Scenario: Successful login
- **WHEN** a client submits the correct email and password for an existing account
- **THEN** the system returns a JWT access token that identifies that user

#### Scenario: Invalid credentials rejected
- **WHEN** a client submits an email that does not exist, or a password that does not match the account
- **THEN** the system rejects the request with a 401 error that does not reveal whether the email or the password was the specific problem

### Requirement: Access Token Validation
The system SHALL reject any request to a protected endpoint unless it carries a JWT access token that is well-formed, unexpired, and identifies an existing user.

#### Scenario: Missing token rejected
- **WHEN** a request to a protected endpoint carries no access token
- **THEN** the system rejects the request with a 401 error

#### Scenario: Expired token rejected
- **WHEN** a request carries an access token whose expiration time has passed
- **THEN** the system rejects the request with a 401 error

#### Scenario: Malformed or tampered token rejected
- **WHEN** a request carries a token that fails signature verification or cannot be parsed as a valid JWT
- **THEN** the system rejects the request with a 401 error

### Requirement: Fixed Token Expiration
Issued access tokens SHALL expire after a fixed, short lifetime. The system SHALL NOT provide a token refresh or revocation mechanism in this MVP; a user regains access by logging in again.

#### Scenario: Expired token requires re-login
- **WHEN** a previously valid access token has passed its expiration time
- **THEN** the only way to obtain a new valid token is to log in again with email and password
