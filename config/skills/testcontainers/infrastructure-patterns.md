# Infrastructure Testcontainers Patterns

## Contents

- Generic containers
- Service modules
- Wait strategies
- Networks and ports
- Resource mapping
- CI behavior
- Diagnostics and performance

## Generic Containers

Use `ContainerBuilder` for an unsupported service or a custom image:

```csharp
using DotNet.Testcontainers.Builders;

const ushort ServicePort = 8080;

var container = new ContainerBuilder("example/service:1.2.3")
    .WithPortBinding(ServicePort, true)
    .WithWaitStrategy(
        Wait.ForUnixContainer()
            .UntilHttpRequestIsSucceeded(request => request.ForPort(ServicePort)))
    .Build();
```

Pin the image, configure an explicit readiness condition, and use `Hostname` plus `GetMappedPublicPort` from the started container.

## Service Modules

Prefer typed modules such as `RedisBuilder`, `RabbitMqBuilder`, or another official module when available. Modules provide service-specific defaults and connection information; generic builders are the fallback, not the default.

For xUnit, choose the package matching the repository:

- xUnit v3: `Testcontainers.XunitV3`
- xUnit v2: `Testcontainers.Xunit`

Use isolated `ContainerTest<...>` fixtures for destructive tests and shared `ContainerFixture<...>` fixtures when state can be reset deterministically.

## Wait Strategies

Container startup is not service readiness. Match the wait strategy to the protocol:

- HTTP health/readiness endpoint for web services;
- listening port plus a real client probe for databases or brokers;
- log-message wait only when the log contract is stable;
- command-based health check when the image provides one.

Set a bounded startup timeout appropriate for the service and CI environment. Preserve logs when the timeout expires.

## Networks and Ports

- Use random host ports for host-to-container access.
- For container-to-container communication, create a Testcontainers network and use stable network aliases.
- Use `host.testcontainers.internal` only when a container must call a service on the test host.
- Do not assume `localhost` inside a container refers to the test host or another container.

Start independent containers concurrently only after their dependency relationships and readiness checks are explicit.

## Resource Mapping

Prefer `WithResourceMapping` for small configuration files, scripts, or certificates. Avoid bind mounts for portable tests because host paths and permissions differ across developer machines and CI runners.

Never bake real credentials into mapped resources. Generate test-only values or use the container module's defaults.

## CI Behavior

The CI runner must expose a Docker-API-compatible runtime. Use the repository's current checkout and .NET setup actions rather than copying pinned action versions from this reference.

The CI test command should match the local command. Cache package restores and container layers only when the CI platform supports safe, deterministic caching.

Do not run `docker container prune`, disable the Resource Reaper, or enable container reuse on a shared runner unless the CI environment has an explicit isolated cleanup policy.

## Diagnostics and Performance

Speed improvements, in order:

1. Use module defaults and a smaller pinned image where production compatibility permits.
2. Share a class/collection fixture.
3. Reset service state instead of recreating the container.
4. Start independent dependencies concurrently.
5. Cache pulled images in CI.

Do not trade away isolation or pinned inputs for faster green tests.

On failure, collect bounded stdout/stderr, container state, readiness diagnostics, and the resolved endpoint. Redact secrets before attaching logs to test output.
