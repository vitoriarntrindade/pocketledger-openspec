# Categories Specification

## Purpose

Lets each user organize their transactions into personal categories with a fixed income/expense type, keeping category usage consistent with the transactions that reference it.

## Requirements

### Requirement: Category Creation
The system SHALL allow an authenticated user to create a category with a name and a type of either income or expense, owned exclusively by that user.

#### Scenario: Successful creation
- **WHEN** an authenticated user creates a category with a name and a valid type
- **THEN** the system creates the category scoped to that user

#### Scenario: Duplicate name and type rejected
- **WHEN** an authenticated user creates a category whose name and type combination already exists among their own categories
- **THEN** the system rejects the creation with a validation error

#### Scenario: Same name allowed across different types
- **WHEN** an authenticated user creates a category with a name that already exists among their categories but with the other type
- **THEN** the system creates the category, since name uniqueness is scoped per user and type

### Requirement: Category Type Is Immutable
A category's type SHALL be fixed at creation time and SHALL NOT be changeable afterward, since existing transactions may already depend on it matching their type.

#### Scenario: Type change rejected
- **WHEN** an authenticated user attempts to update a category's type
- **THEN** the system rejects the change; only the category's name may be edited

### Requirement: Category Rename
The system SHALL allow the owning user to rename their own category.

#### Scenario: Successful rename
- **WHEN** an authenticated user renames one of their own categories to a name not already used for that type
- **THEN** the system updates the category's name

#### Scenario: Rename to duplicate rejected
- **WHEN** an authenticated user renames a category to a name already used by another of their categories with the same type
- **THEN** the system rejects the rename with a validation error

### Requirement: Category Deletion Restricted When In Use
The system SHALL prevent deletion of a category that is referenced by at least one transaction.

#### Scenario: Delete unused category
- **WHEN** an authenticated user deletes a category with no associated transactions
- **THEN** the system deletes the category

#### Scenario: Delete used category rejected
- **WHEN** an authenticated user attempts to delete a category referenced by at least one transaction
- **THEN** the system rejects the deletion with a clear error and the category remains

### Requirement: Category Ownership Isolation
The system SHALL restrict every category to the user who created it. A user SHALL NOT view, edit, delete, or reference in a transaction any category owned by another user.

#### Scenario: Cross-user access rejected
- **WHEN** an authenticated user attempts to view, rename, or delete a category owned by a different user
- **THEN** the system rejects the request as if the category does not exist

### Requirement: Category Listing
The system SHALL allow an authenticated user to list their own categories.

#### Scenario: Listing returns only own categories
- **WHEN** an authenticated user lists categories
- **THEN** the system returns only categories owned by that user
