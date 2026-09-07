# Type Design and Collections

Focused performance guidance for C# type shape, pure functions, enumeration, async return types, and collections.

## Prefer Static Pure Functions

Prefer static pure functions for computations that do not need instance state; explicit inputs make them easy to test.

```csharp
public static class OrderCalculator
{
    public static Money CalculateTotal(
        IReadOnlyList<OrderItem> items,
        decimal taxRate,
        decimal discountPercent)
    {
        var subtotal = items.Sum(i => i.Price * i.Quantity);
        return new Money(subtotal * (1 + taxRate) * (1 - discountPercent), "USD");
    }
}
```

Benefits:

- No virtual dispatch.
- No hidden state.
- Pure input to output behavior is simple to test.
- Safe for concurrent calls when inputs are immutable or independently owned.
- Dependencies are explicit parameters.

Use instance methods when the type genuinely owns state or must participate in polymorphism.

## Defer Enumeration

Do not materialize enumerables until needed. Avoid repeated LINQ materialization.

```csharp
public IReadOnlyList<Order> GetActiveOrders()
{
    return _orders
        .Where(o => o.IsActive)
        .OrderBy(o => o.CreatedAt)
        .ToList();
}
```

Return `IEnumerable<T>` only when lazy evaluation is part of the contract and the caller can safely enumerate later. Return a materialized read-only collection when the data must be stable.

### Async Enumeration

Avoid hiding async work inside LINQ projections when streaming is the clearer shape.

```csharp
public async IAsyncEnumerable<OrderResult> ProcessOrdersAsync(
    IEnumerable<Order> orders,
    [EnumeratorCancellation] CancellationToken cancellationToken = default)
{
    foreach (var order in orders)
    {
        cancellationToken.ThrowIfCancellationRequested();
        yield return await ProcessOrderAsync(order, cancellationToken);
    }
}
```

Use `Task.WhenAll` for bounded batches when all work should start together.

## ValueTask Rules

Use `ValueTask` only for hot paths that often complete synchronously. For real I/O, use `Task`.

```csharp
public ValueTask<User?> GetUserAsync(UserId id)
{
    if (_cache.TryGetValue(id, out var user))
    {
        return ValueTask.FromResult<User?>(user);
    }

    return new ValueTask<User?>(FetchUserAsync(id));
}
```

Rules:

- Never await a `ValueTask` more than once.
- Never use `.Result` or `.GetAwaiter().GetResult()` before completion.
- If in doubt, use `Task`.

## Collection Return Types

Return read-only contracts from API boundaries and keep mutation internal. A read-only interface does not guarantee an immutable collection or immutable elements; return a snapshot or an immutable collection when callers require stability.

```csharp
// .NET 8+; using System.Collections.Frozen;
private static readonly FrozenDictionary<string, Handler> Handlers =
    new Dictionary<string, Handler>
    {
        ["create"] = new CreateHandler(),
        ["update"] = new UpdateHandler(),
    }.ToFrozenDictionary();
```

| Scenario | Return Type |
|----------|-------------|
| API boundary | `IReadOnlyList<T>`, `IReadOnlyCollection<T>` |
| Static lookup data | `FrozenDictionary<K,V>`, `FrozenSet<T>` |
| Internal building | `List<T>`, then return as readonly |
| Single item or none | `T?` |
| Zero or more, lazy | `IEnumerable<T>` |

## Quick Reference

| Pattern | Benefit |
|---------|---------|
| `sealed class` | Devirtualization, clear API |
| `readonly record struct` | No defensive copies, value semantics |
| Static pure functions | No virtual dispatch, testable, thread-safe |
| Defer `.ToList()` | Single materialization |
| `ValueTask` for hot paths | Avoid `Task` allocation |
| `Span<T>` for bytes | Views over contiguous memory without copying |
| `IReadOnlyList<T>` return | Read-only API contract |
| `FrozenDictionary` | Fast lookup for static data |

## Anti-Patterns

| Avoid | Prefer |
|-------|--------|
| Unsealed class without an inheritance design | `sealed class` |
| Mutable struct | `readonly struct` or `readonly record struct` |
| Instance method that could be static | Static pure function |
| Multiple `.ToList()` calls in one pipeline | One materialization at the boundary |
| Returning `List<T>` from public APIs | `IReadOnlyList<T>` or `IReadOnlyCollection<T>` |
| `ValueTask` for always-async operations | `Task` |
