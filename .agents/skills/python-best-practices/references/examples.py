"""Examples of Python code following best practices.

This module demonstrates PEP 8, type hints, Google-style docstrings,
and line length (78 chars max) best practices.

Key standards:
- All functions have type hints
- All classes have docstrings
- Google-style docstring format
- Maximum 78 characters per line
- PEP 8 naming conventions
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any


class UserRole(Enum):
    """User role enumeration."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class ValidationError(Exception):
    """Exception raised for validation errors."""


class User:
    """Represent a user in the system.

    Attributes:
        id: Unique user identifier.
        username: User's login username.
        email: User's email address.
        role: User's role/permissions level.
        created_at: Account creation timestamp.
        is_active: Whether the account is active.
    """

    def __init__(
        self,
        username: str,
        email: str,
        role: UserRole = UserRole.USER,
    ) -> None:
        """Initialize a new User instance.

        Args:
            username: User's login username (2-20 chars).
            email: User's email address.
            role: User's role. Defaults to USER.

        Raises:
            ValidationError: If username or email invalid.
        """
        self.id: int | None = None
        self.username: str = self._validate_username(
            username,
        )
        self.email: str = self._validate_email(email)
        self.role: UserRole = role
        self.created_at: datetime = datetime.now(UTC)
        self.is_active: bool = True

    @staticmethod
    def _validate_username(username: str) -> str:
        """Validate username format.

        Args:
            username: Username to validate.

        Returns:
            Validated username (lowercase).

        Raises:
            ValidationError: If username is invalid.
        """
        if not username or len(username) < 2:
            raise ValidationError(
                "Username must be at least 2 characters",
            )
        if len(username) > 20:
            raise ValidationError(
                "Username must be at most 20 characters",
            )
        if not username.replace("_", "").isalnum():
            raise ValidationError(
                "Username contains invalid characters",
            )
        return username.lower()

    @staticmethod
    def _validate_email(email: str) -> str:
        """Validate email format.

        Args:
            email: Email address to validate.

        Returns:
            Validated email (lowercase).

        Raises:
            ValidationError: If email is invalid.
        """
        if "@" not in email or "." not in email:
            raise ValidationError("Invalid email format")
        return email.lower()

    def __repr__(self) -> str:
        """Return string representation of user."""
        return f"User({self.username!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on username."""
        if not isinstance(other, User):
            return False
        return self.username == other.username


class UserRepository(ABC):
    """Abstract base class for user data access.

    Defines interface for user repository implementations.
    """

    @abstractmethod
    def create(self, user: User) -> int:
        """Create a new user.

        Args:
            user: User object to create.

        Returns:
            Newly created user ID.
        """

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User object if found, None otherwise.
        """

    @abstractmethod
    def find_by_username(
        self,
        username: str,
    ) -> User | None:
        """Find user by username.

        Args:
            username: User's login username.

        Returns:
            User object if found, None otherwise.
        """


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository.

    Used for testing and development. Data is stored in
    a dictionary and lost when the application exits.
    """

    def __init__(self) -> None:
        """Initialize empty repository."""
        self._users: dict[int, User] = {}
        self._counter: int = 0

    def create(self, user: User) -> int:
        """Create a new user."""
        self._counter += 1
        user.id = self._counter
        self._users[self._counter] = user
        return self._counter

    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        return self._users.get(user_id)

    def find_by_username(
        self,
        username: str,
    ) -> User | None:
        """Find user by username."""
        for user in self._users.values():
            if user.username == username.lower():
                return user
        return None


class UserService:
    """Service for user business logic.

    Handles user operations including registration,
    authentication, and profile management.
    """

    def __init__(
        self,
        repository: UserRepository,
    ) -> None:
        """Initialize UserService.

        Args:
            repository: UserRepository implementation.
        """
        self.repository: UserRepository = repository

    def register_user(
        self,
        username: str,
        email: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Register a new user.

        Args:
            username: Desired username.
            email: User's email address.
            role: User's role. Defaults to USER.

        Returns:
            Created User object with assigned ID.

        Raises:
            ValidationError: If username already exists.
        """
        # Check if username is available
        existing = self.repository.find_by_username(
            username,
        )
        if existing:
            raise ValidationError(
                f"Username '{username}' already taken",
            )

        # Create and store new user
        user = User(username, email, role)
        self.repository.create(user)

        return user

    def get_user(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: User identifier.

        Returns:
            User object if found, None otherwise.
        """
        return self.repository.find_by_id(user_id)

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account.

        Args:
            user_id: User identifier.

        Returns:
            True if deactivation successful, False if
            user not found.
        """
        user = self.repository.find_by_id(user_id)
        if not user:
            return False
        user.is_active = False
        return True


def calculate_session_duration(
    start_time: datetime,
    end_time: datetime,
) -> timedelta:
    """Calculate duration of a user session.

    Args:
        start_time: Session start timestamp.
        end_time: Session end timestamp.

    Returns:
        Duration as timedelta object.

    Raises:
        ValueError: If end_time is before start_time.
    """
    if end_time < start_time:
        raise ValueError(
            "End time cannot be before start time",
        )
    return end_time - start_time


def batch_process_users(
    users: list[User],
    batch_size: int = 10,
) -> list[list[User]]:
    """Process users in batches.

    Args:
        users: List of users to process.
        batch_size: Size of each batch. Defaults to 10.

    Returns:
        List of user batches.

    Example:
        >>> users = [User("user1", "u1@test.com"), ...]
        >>> batches = batch_process_users(users, 5)
        >>> len(batches[0])
        5
    """
    batches: list[list[User]] = []
    for i in range(0, len(users), batch_size):
        batch = users[i : i + batch_size]
        batches.append(batch)
    return batches


def format_user_profile(user: User) -> str:
    """Format user information for display.

    Args:
        user: User object to format.

    Returns:
        Formatted user profile string.
    """
    status = "Active" if user.is_active else "Inactive"
    return (
        f"Username: {user.username}\n"
        f"Email: {user.email}\n"
        f"Role: {user.role.value}\n"
        f"Status: {status}\n"
        f"Created: {user.created_at.isoformat()}"
    )


def filter_users_by_role(
    users: list[User],
    role: UserRole,
) -> list[User]:
    """Filter users by role.

    Args:
        users: List of users to filter.
        role: Role to filter by.

    Returns:
        Users matching the specified role.
    """
    return [user for user in users if user.role == role]


if __name__ == "__main__":
    # Example usage
    repo = InMemoryUserRepository()
    service = UserService(repo)

    # Register users
    user1 = service.register_user(
        "alice",
        "alice@example.com",
        UserRole.ADMIN,
    )
    user2 = service.register_user(
        "bob",
        "bob@example.com",
        UserRole.USER,
    )

    # Display user info
    print(format_user_profile(user1))
    print()

    # Batch process
    users = [user1, user2]
    batches = batch_process_users(users, 1)
    print(f"Created {len(batches)} batches")
