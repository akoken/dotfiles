---
name: testcontainers
description: Build .NET integration tests against disposable Docker dependencies with Testcontainers and xUnit. Use for databases, caches, brokers, migration tests, container lifecycle, isolation, wait strategies, CI execution, or replacing infrastructure mocks with real services.
---

# Testcontainers for .NET

Use real disposable infrastructure when correctness depends on a database engine, broker, cache, filesystem, or network protocol. Keep unit tests for pure logic; use Testcontainers at the infrastructure boundary.

## Workflow

1. Inspect the target framework, test framework version, package management, Docker availability, and existing fixture conventions.
2. Prefer the official module package and module-specific builder (`Testcontainers.MsSql` with `MsSqlBuilder`, for example). Use `ContainerBuilder` only when no suitable module exists.
3. Pin every container image to an explicit tag or digest. Never use `latest`.
4. Choose isolation deliberately:
   - per-test container for destructive or strongly isolated tests;
   - shared class/collection fixture plus deterministic state reset for faster suites;
   - separate database/schema/tenant only when the service supports it reliably.
5. Start containers through xUnit fixtures or explicit async lifecycle management. Always dispose them.
6. Run the production migration/schema path before assertions when the test covers persistence.
7. Use random host-port bindings and obtain endpoints from the container object.
8. Wait for service readiness, not merely container process startup.
9. Run the focused integration tests locally, then verify the same command in Docker-capable CI.

Completion requires a pinned image, deterministic isolation, disposal, a real readiness condition, and a passing test against the actual service.

## Current API Shape

Install packages through the repository's normal package-management workflow. Do not paste wildcard versions into project XML.

```bash
dotnet add package Testcontainers.MsSql

# Optional lifecycle integration. Match the repository's xUnit major version.
dotnet add package Testcontainers.XunitV3
# or: dotnet add package Testcontainers.Xunit
```

Minimal explicit lifecycle example:

```csharp
using Testcontainers.MsSql;

await using var database = new MsSqlBuilder(
        "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")
    .Build();

await database.StartAsync(cancellationToken);

var connectionString = database.GetConnectionString();
// Run the production migration path, exercise the repository, then assert behavior.
```

For a generic image:

```csharp
using DotNet.Testcontainers.Builders;

const ushort ContainerPort = 8080;

await using var container = new ContainerBuilder("testcontainers/helloworld:1.3.0")
    .WithPortBinding(ContainerPort, true)
    .WithWaitStrategy(
        Wait.ForUnixContainer()
            .UntilHttpRequestIsSucceeded(request => request.ForPort(ContainerPort)))
    .Build();

await container.StartAsync(cancellationToken);

var endpoint = new UriBuilder(
    Uri.UriSchemeHttp,
    container.Hostname,
    container.GetMappedPublicPort(ContainerPort)).Uri;
```

## Reference Routing

- Read [database-patterns.md](database-patterns.md) for SQL Server/PostgreSQL modules, migrations, state reset, and database-test isolation.
- Read [infrastructure-patterns.md](infrastructure-patterns.md) for generic containers, Redis/brokers, networks, wait strategies, diagnostics, and CI.
- Verify API details against the current [Testcontainers for .NET documentation](https://dotnet.testcontainers.org/) when the installed package version may differ from these examples.

## Guardrails

- Do not mock the dependency in a test whose purpose is to validate its protocol, query semantics, constraints, transactions, serialization, or migrations.
- Do not bind fixed host ports.
- Do not use floating image tags.
- Do not depend on test execution order.
- Do not share mutable fixture state without a deterministic reset boundary.
- Do not disable the Resource Reaper or enable reusable containers merely for speed without an explicit local-only policy.
- Do not run broad Docker cleanup commands on shared CI hosts.
- Preserve container logs on failure when startup or readiness is flaky.

## Verification

Run the narrowest integration-test project first, then the repository's normal broader checks:

```bash
dotnet test path/to/IntegrationTests.csproj
```

If Docker is unavailable, report the integration test as not run; do not replace it with a mock and claim equivalent coverage.
