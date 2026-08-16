# Classification, with worked examples

Load this when a request does not obviously belong to one tier. Most do; the
ones that do not are where mistakes get made, so the borderline cases below
matter more than the clear ones.

## TRIVIAL

No behaviour changes. Nothing a test could detect.

- fixing a spelling mistake in a docstring or comment
- correcting a typo in `README.md`
- renaming a local variable inside one function
- reformatting a file the formatter would fix anyway

**Process:** fix it, `make fast`, done. No OpenSpec change, no branch ceremony.

**Careful:** a rename that crosses a module boundary is not trivial — it is a
SMALL refactor, because something outside the file can break.

## SMALL

Behaviour changes, but narrowly and within one layer, and the requirement fits
in a sentence.

- adding a `max_length` to an existing Pydantic field
- adding a sort option to an endpoint that already sorts
- extracting a helper inside one service
- adding a missing index to a query that already exists

**Process:** branch, implement with a test, `make quality`, brief report. No
full spec, but the branch and commit still record why.

**Careful:** "add a field to the response" sounds SMALL and often is not. If
the field requires a schema change, it is STANDARD.

## STANDARD

New user-visible behaviour, contained, and specifiable in a handful of
requirements.

- a new endpoint over existing models
- a new filter combination with its own validation rules
- an export of existing data in a new format

**Process:** the full workflow — `spec-architect`, branch, implement, gate,
review, `spec-verifier`, report.

**Careful:** if it touches how users are isolated from each other, it is
COMPLEX regardless of how small the diff looks.

## COMPLEX

Cross-cutting, or touching something whose failure is expensive.

- transfers between accounts (two writes that must agree, new invariants,
  cross-entity validation)
- adding a new entity with its own migration
- changing pagination or filtering across every endpoint
- integrating an external service
- changing anything about authentication or authorisation

**Process:** the full workflow, plus `security-reviewer`, plus explicit
architectural decisions recorded in `design.md`.

**Careful:** a change is COMPLEX if *any* part of it is, even when most of it
is routine.

## CRITICAL

Failure is irreversible, or the blast radius includes data or secrets.

- a migration that drops or rewrites a column
- rotating or changing how JWT secrets are handled
- anything touching payments
- changing how passwords are hashed or verified
- infrastructure or deployment configuration

**Process:** the full workflow, and **no irreversible step runs without
explicit human authorisation** — not the migration, not the deletion, not the
rotation. Write the plan, present it, and wait.

## The borderline cases that are usually misjudged

**"Just add a field."** Trivial-sounding, but if it reaches the database it is
a migration, and migrations are at least COMPLEX.

**"Just fix the bug."** If the fix changes what the system does in a case
someone might depend on, it is a behaviour change and needs a spec.

**"Just refactor."** A refactor that cannot change behaviour is SMALL. A
refactor that moves a boundary between layers is COMPLEX, because boundaries
are architecture.

**"Just update a dependency."** Usually a chore. But a dependency that handles
authentication, cryptography or the database is CRITICAL — its behaviour is
your behaviour.

**"Make it faster."** Performance work that changes query shape can change
result ordering, and ordering is observable behaviour. Specify what must stay
the same.
