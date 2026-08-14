---
name: repository-security-audit
description: Perform a comprehensive backend security review of a source code repository, identifying vulnerabilities, insecure patterns, misconfigurations, and AI security risks. Use when asked to audit, review, pentest, or assess application security.
allowed-tools: Read, Bash, WebFetch, WebSearch
license: MIT
compatibility: Works with any source code repository
metadata:
  author: security-team
  version: "1.0"
  category: security
---

# Repository Security Audit

## Goal

Perform a systematic security review of the repository.

Only report findings that are supported by evidence.

Prefer high-confidence findings over speculative issues.

---

## Workflow

Follow these phases in order.

### 1. Understand the project

Identify:

- Language
- Framework
- Runtime
- Database
- ORM
- Authentication
- Infrastructure
- Deployment model
- External integrations

Build a mental model before looking for vulnerabilities.

---

### 2. Identify attack surface

Locate:

- HTTP routes
- Controllers
- Middleware
- Background jobs
- Scheduled tasks
- Webhooks
- Queue consumers
- CLI commands

Identify every external entry point.

---

### 3. Trace data flow

For every public entry point:

Input

↓

Validation

↓

Business Logic

↓

Database

↓

External Services

↓

Response

Track user-controlled data to sensitive operations.

---

### 4. Review security controls

Verify implementation of:

- Authentication
- Authorization
- Session management
- JWT validation
- CSRF protection
- Rate limiting
- Input validation
- Output encoding
- Secret management
- Logging
- Error handling

---

### 5. Review vulnerability classes

Always review for:

- SQL Injection
- NoSQL Injection
- Command Injection
- Prompt Injection
- SSRF
- Path Traversal
- File Upload
- XSS
- CSRF
- XXE
- IDOR
- Broken Access Control
- Authentication flaws
- Authorization flaws
- Race conditions
- Sensitive Data Exposure
- Weak Cryptography
- Security Misconfiguration
- Dependency vulnerabilities

---

### 6. Infrastructure review

Review:

- Docker
- Kubernetes
- CI/CD
- Reverse proxy
- Environment variables
- Secrets
- TLS
- CORS

---

### 7. AI Security

If the repository uses LLMs, review:

- Prompt Injection
- Indirect Prompt Injection
- Tool Injection
- RAG poisoning
- System prompt exposure
- Secret leakage
- Unsafe tool execution
- Missing output validation

---

### 8. Validate findings

Do not report vulnerabilities based only on keyword matching.

Whenever possible:

- Follow the execution path.
- Confirm exploitability.
- Consider framework protections.
- Reduce false positives.

If evidence is insufficient:

Mark the issue as:

> Needs Manual Verification

Never report assumptions as confirmed vulnerabilities.

---

## Reporting

Each finding should include:

- Title
- Severity
- Confidence
- Category
- CWE (when applicable)
- OWASP mapping
- Affected files
- Evidence
- Explanation
- Attack scenario
- Recommended remediation

---

## Severity

Use:

- Critical
- High
- Medium
- Low
- Informational

---

## Confidence

Use:

- High
- Medium
- Low

---

## Principles

- Evidence over assumptions.
- Prefer data-flow analysis over regex matching.
- Correlate findings across multiple files.
- Respect framework-specific protections.
- Explain why the issue exists.
- Provide repository-specific remediation.
- Minimize false positives.
