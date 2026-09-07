# Advanced Concurrency Patterns

Reactive Extensions and async local function patterns for advanced concurrency scenarios.

## Contents

- [Reactive Extensions (UI and Event Composition)](#reactive-extensions-ui-and-event-composition)
- [Prefer Async Local Functions](#prefer-async-local-functions)

## Reactive Extensions (UI and Event Composition)

**Use for:** UI event handling, composing event streams, time-based operations in client applications.

Rx shines in UI scenarios where you need to react to user events with debouncing, throttling, or combining multiple event sources.

```csharp
using System.Reactive.Linq;

// Search-as-you-type with debouncing
public class SearchViewModel
{
    public SearchViewModel(ISearchService searchService)
    {
        SearchResults = SearchText
            .Throttle(TimeSpan.FromMilliseconds(300))  // Wait for typing to pause
            .DistinctUntilChanged()                     // Ignore if same text
            .Where(text => text.Length >= 3)           // Minimum length
            .SelectMany(text => searchService.SearchAsync(text).ToObservable())
            .ObserveOn(RxApp.MainThreadScheduler);     // Back to UI thread
    }

    public IObservable<string> SearchText { get; }
    public IObservable<IList<SearchResult>> SearchResults { get; }
}

// Combining multiple UI events
public IObservable<bool> CanSubmit =>
    Observable.CombineLatest(
        UsernameValid,
        PasswordValid,
        EmailValid,
        (user, pass, email) => user && pass && email);

// Double-click detection
public IObservable<Point> DoubleClicks =>
    MouseClicks
        .Buffer(TimeSpan.FromMilliseconds(300))
        .Where(clicks => clicks.Count >= 2)
        .Select(clicks => clicks.Last());

// Auto-save with debouncing
public IDisposable AutoSave =>
    DocumentChanges
        .Throttle(TimeSpan.FromSeconds(2))
        .Subscribe(async doc => await SaveAsync(doc));
```

**Rx is ideal for:**
- UI event composition (WPF, WinForms, MAUI, Blazor)
- Search-as-you-type with debouncing
- Combining multiple event sources
- Time-windowed operations in UI
- Drag-and-drop gesture detection
- Real-time data visualization

## Prefer Async Local Functions

Use async local functions instead of `Task.Run(async () => ...)` or `ContinueWith()`:

### Don't: Anonymous Async Lambda

```csharp
private async Task<WorkCompleted> HandleCommandAsync()
{
    return await Task.Run(async () =>
    {
        var result = await DoWorkAsync();
        return new WorkCompleted(result);
    });
}
```

### Do: Async Local Function

```csharp
private async Task<WorkCompleted> HandleCommandAsync()
{
    async Task<WorkCompleted> ExecuteAsync()
    {
        var result = await DoWorkAsync();
        return new WorkCompleted(result);
    }

    return await ExecuteAsync();
}
```

### Avoid ContinueWith for Sequencing

**Don't:**
```csharp
someTask
    .ContinueWith(t => ProcessResult(t.Result))
    .ContinueWith(t => SendNotification(t.Result));
```

**Do:**
```csharp
async Task ProcessAndNotifyAsync()
{
    var result = await someTask;
    var processed = await ProcessResult(result);
    await SendNotification(processed);
}

await ProcessAndNotifyAsync();
```

| Benefit | Description |
|---------|-------------|
| **Readability** | Named functions are self-documenting |
| **Debugging** | Stack traces show meaningful function names |
| **Exception handling** | Cleaner try/catch without `AggregateException` |
| **Scope clarity** | Local functions make captured variables explicit |
| **Testability** | Easier to extract and unit test the async logic |
