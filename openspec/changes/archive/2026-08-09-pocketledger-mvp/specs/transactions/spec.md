## Purpose

Records each user's income and expense events with the fields and rules needed to keep the ledger accurate, owned per-user, and queryable by period, type, and category.

## ADDED Requirements

### Requirement: Transaction Creation
The system SHALL allow an authenticated user to create a transaction with a type (income or expense), a description, an amount, a transaction date, and a category, owned exclusively by that user.

#### Scenario: Successful creation
- **WHEN** an authenticated user creates a transaction whose category belongs to them and whose type matches that category's type
- **THEN** the system creates the transaction owned by that user

#### Scenario: Category type mismatch rejected
- **WHEN** an authenticated user creates a transaction whose type does not match the type of the specified category
- **THEN** the system rejects the creation with a validation error

#### Scenario: Category from another user rejected
- **WHEN** an authenticated user creates a transaction referencing a category owned by a different user
- **THEN** the system rejects the creation as if the category does not exist

### Requirement: Amount Validation
A transaction's amount SHALL be strictly greater than zero and SHALL be represented with fixed decimal precision suitable for monetary values, without floating-point rounding error.

#### Scenario: Zero or negative amount rejected
- **WHEN** an authenticated user submits a transaction with an amount less than or equal to zero
- **THEN** the system rejects the creation with a validation error

### Requirement: Exactly One Transaction Type
A transaction SHALL have exactly one type: income or expense.

#### Scenario: Missing or invalid type rejected
- **WHEN** an authenticated user submits a transaction without a type, or with a type other than income or expense
- **THEN** the system rejects the creation with a validation error

### Requirement: Independent Transaction Date
A transaction SHALL record a user-supplied transaction date that is independent of the system-generated creation timestamp, so a transaction can be registered after the fact.

#### Scenario: Backdated transaction accepted
- **WHEN** an authenticated user creates a transaction with a transaction date earlier than the current time
- **THEN** the system creates the transaction, recording both the supplied transaction date and the actual creation timestamp

### Requirement: Transaction Editing
The system SHALL allow the owning user to edit a transaction's description, amount, date, category, and type, re-validating the amount and the category/type match against the edited values.

#### Scenario: Successful edit
- **WHEN** an authenticated user edits their own transaction with a new category whose type matches the transaction's (possibly also edited) type
- **THEN** the system updates the transaction

#### Scenario: Edit producing a type mismatch rejected
- **WHEN** an authenticated user edits their own transaction such that the resulting type and category type no longer match
- **THEN** the system rejects the edit with a validation error and leaves the transaction unchanged

### Requirement: Transaction Deletion
The system SHALL allow the owning user to delete their own transaction.

#### Scenario: Successful deletion
- **WHEN** an authenticated user deletes their own transaction
- **THEN** the system removes the transaction

### Requirement: Transaction Ownership Isolation
The system SHALL restrict every transaction to the user who owns it. A user SHALL NOT view, edit, or delete a transaction owned by another user.

#### Scenario: Cross-user access rejected
- **WHEN** an authenticated user attempts to view, edit, or delete a transaction owned by a different user
- **THEN** the system rejects the request as if the transaction does not exist

### Requirement: Transaction Filtering
The system SHALL allow listing transactions filtered by start date, end date, type, and category, with filters combinable together.

#### Scenario: Combined filters
- **WHEN** an authenticated user lists transactions with a start date, an end date, a type, and a category all specified together
- **THEN** the system returns only that user's transactions matching every specified filter

### Requirement: Transaction Sorting
The system SHALL allow listing transactions sorted by date or by amount, in ascending or descending order, so a user can identify their largest expenses or most recent activity.

#### Scenario: Sort by amount descending
- **WHEN** an authenticated user lists expense transactions sorted by amount in descending order
- **THEN** the system returns those transactions ordered from largest to smallest amount

### Requirement: Transaction Pagination
The system SHALL paginate transaction listings and SHALL report the total number of matching transactions alongside each page.

#### Scenario: Second page returns remaining results
- **WHEN** an authenticated user requests the second page of a transaction listing with a given page size
- **THEN** the system returns the next set of matching transactions after the first page, along with the total matching count

#### Scenario: Default pagination applied
- **WHEN** an authenticated user lists transactions without specifying page or page size
- **THEN** the system applies a default page size rather than returning every matching transaction at once
