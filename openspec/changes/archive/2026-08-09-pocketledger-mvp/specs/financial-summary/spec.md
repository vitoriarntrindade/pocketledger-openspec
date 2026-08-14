## Purpose

Gives a user an always-consistent view of their financial position for a chosen period, computed directly from their transactions on every request rather than from any independently stored balance.

## ADDED Requirements

### Requirement: Summary Retrieval For a Period
The system SHALL allow an authenticated user to request a financial summary for a start and end date, scoped to their own transactions only.

#### Scenario: Summary for a period with activity
- **WHEN** an authenticated user requests a summary for a period containing both income and expense transactions
- **THEN** the system returns a summary computed from exactly those transactions

### Requirement: Summary Fields
A financial summary SHALL include: total income, total expenses, balance, number of income transactions, number of expense transactions, and the distribution of expense totals by category.

#### Scenario: All fields present
- **WHEN** an authenticated user requests a summary for a period
- **THEN** the response includes total income, total expenses, balance, income count, expense count, and an expense-by-category breakdown

### Requirement: Derived Balance
The balance SHALL always equal total income minus total expenses, computed from the current set of transactions at request time. The system SHALL NOT persist the balance as an independent, separately-updated value.

#### Scenario: Balance reflects a new transaction immediately
- **WHEN** an authenticated user creates or deletes a transaction and then requests a summary covering that transaction's date
- **THEN** the returned balance reflects that change without any separate update step

### Requirement: Empty Period Handling
A period containing no matching transactions SHALL return zero totals and counts and an empty category distribution, not an error.

#### Scenario: No transactions in range
- **WHEN** an authenticated user requests a summary for a period with no transactions
- **THEN** the system returns a summary with all totals and counts at zero and an empty distribution

### Requirement: Summary Ownership Isolation
The summary SHALL only ever be computed from the authenticated user's own transactions.

#### Scenario: Other users' transactions excluded
- **WHEN** another user has transactions within the same requested period
- **THEN** those transactions have no effect on the requesting user's summary
