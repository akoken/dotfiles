# Advanced DI Patterns

Testing with DI extensions, advanced registration patterns.

## Contents

- [Testing Benefits](#testing-benefits)
- [Common Patterns](#common-patterns)

## Testing Benefits

The main advantage of `Add*` extension methods: **reuse production configuration in tests**.

### WebApplicationFactory

```csharp
public class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public ApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Production services already registered via Add* methods
                // Only override what's different for testing

                // Replace email sender with test double
                services.RemoveAll<IEmailSender>();
                services.AddSingleton<IEmailSender, TestEmailSender>();

                // Replace external payment processor
                services.RemoveAll<IPaymentProcessor>();
                services.AddSingleton<IPaymentProcessor, FakePaymentProcessor>();
            });
        });
    }

    [Fact]
    public async Task CreateOrder_SendsConfirmationEmail()
    {
        var client = _factory.CreateClient();
        var emailSender = _factory.Services.GetRequiredService<IEmailSender>() as TestEmailSender;

        await client.PostAsJsonAsync("/api/orders", new CreateOrderRequest(...));

        Assert.Single(emailSender!.SentEmails);
    }
}
```

### Standalone Unit Tests

```csharp
public class UserServiceTests
{
    private readonly ServiceProvider _provider;

    public UserServiceTests()
    {
        var services = new ServiceCollection();

        // Reuse production registrations
        services.AddUserServices();

        // Add test infrastructure
        services.AddSingleton<IUserRepository, InMemoryUserRepository>();

        _provider = services.BuildServiceProvider();
    }

    [Fact]
    public async Task CreateUser_ValidData_Succeeds()
    {
        var service = _provider.GetRequiredService<IUserService>();
        var result = await service.CreateUserAsync(new CreateUserRequest(...));

        Assert.True(result.IsSuccess);
    }
}
```

## Common Patterns

### Conditional Registration

```csharp
public static IServiceCollection AddEmailServices(
    this IServiceCollection services,
    IHostEnvironment environment)
{
    services.AddSingleton<IEmailComposer, MjmlEmailComposer>();

    if (environment.IsDevelopment())
    {
        services.AddSingleton<IEmailSender, MailpitEmailSender>();
    }
    else
    {
        services.AddSingleton<IEmailSender, SmtpEmailSender>();
    }

    return services;
}
```

### Factory-Based Registration

```csharp
public static IServiceCollection AddPaymentServices(
    this IServiceCollection services,
    string configSection = "Stripe")
{
    services.AddOptions<StripeOptions>()
        .BindConfiguration(configSection)
        .ValidateOnStart();

    services.AddSingleton<IPaymentProcessor>(sp =>
    {
        var options = sp.GetRequiredService<IOptions<StripeOptions>>().Value;
        var logger = sp.GetRequiredService<ILogger<StripePaymentProcessor>>();

        return new StripePaymentProcessor(options.ApiKey, options.WebhookSecret, logger);
    });

    return services;
}
```

### Keyed Services (.NET 8+)

```csharp
public static IServiceCollection AddNotificationServices(this IServiceCollection services)
{
    services.AddKeyedSingleton<INotificationSender, EmailNotificationSender>("email");
    services.AddKeyedSingleton<INotificationSender, SmsNotificationSender>("sms");
    services.AddKeyedSingleton<INotificationSender, PushNotificationSender>("push");

    services.AddScoped<INotificationDispatcher, NotificationDispatcher>();

    return services;
}
```
