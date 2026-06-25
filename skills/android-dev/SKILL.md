---
name: android-dev
description: >
  Android development skill for Kutti. Use this for any Android development task
  including Kotlin, Java, Gradle, AndroidManifest, Jetpack Compose, and ADB.
triggers:
  - android
  - kotlin
  - java
  - gradle
  - compose
  - adb
  - xml
  - manifest
priority: high
---

# Android Development

You are working inside a Kutti Android project. Always prefer modern Android development practices.

## Language Preferences

- **Kotlin over Java**: Always prefer Kotlin for new code
- **Jetpack Compose for UI**: Use Compose for all new UI development
- **Coroutines + Flow**: Prefer over RxJava or callbacks
- **ViewModel + StateFlow**: For state management

## Build System

### Gradle
- Use Gradle version catalogs (`libs.versions.toml`)
- Never hardcode dependency versions in `build.gradle`
- Use Kotlin DSL for Gradle files
- Keep build scripts clean and maintainable

### Dependencies
- Use stable versions from version catalogs
- Prefer Jetpack libraries over third-party when possible
- Keep dependencies updated but stable

## Architecture

### Recommended Patterns
- **MVVM**: Model-View-ViewModel
- **Clean Architecture**: Separate use cases, repositories, data sources
- **Dependency Injection**: Use Hilt
- **Repository Pattern**: For data access

### Code Organization
```
app/
├── src/main/
│   ├── java/com/example/app/
│   │   ├── di/          # Dependency injection modules
│   │   ├── ui/          # UI components (Compose)
│   │   │   ├── screens/ # Screens
│   │   │   ├── components/ # Reusable components
│   │   │   └── theme/   # App theme
│   │   ├── data/        # Data layer
│   │   │   ├── repository/
│   │   │   ├── datasource/
│   │   │   └── model/
│   │   ├── domain/      # Domain layer
│   │   │   ├── usecase/
│   │   │   └── model/
│   │   └── MainActivity.kt
│   └── AndroidManifest.xml
```

## UI Development (Jetpack Compose)

### Best Practices
- Use `remember` for state that survives recomposition
- Use `derivedStateOf` for derived state
- Prefer `LazyColumn`/`LazyRow` over `Column`/`Row` for lists
- Use `Modifier` for styling and layout
- Follow Material Design 3 guidelines

### Example Composable
```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Hello, Android!",
            style = MaterialTheme.typography.headlineMedium
        )
        
        Button(onClick = { viewModel.onAction() }) {
            Text("Click me")
        }
    }
}
```

## ViewModel

### Best Practices
- Extend `ViewModel()`
- Use `StateFlow` for UI state
- Use `Flow` for one-time events
- Keep business logic in use cases, not ViewModels

### Example ViewModel
```kotlin
@HiltViewModel
class MyViewModel @Inject constructor(
    private val useCase: MyUseCase
) : ViewModel() {
    
    private val _state = MutableStateFlow(MyState())
    val state: StateFlow<MyState> = _state.asStateFlow()
    
    fun onAction() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true)
            
            val result = useCase.execute()
            
            _state.value = _state.value.copy(
                isLoading = false,
                data = result
            )
        }
    }
}
```

## Testing

- **Unit Tests**: In `src/test/` - Use Robolectric for fast tests
- **Instrumentation Tests**: In `src/androidTest/` - Test on real devices
- **UI Tests**: Use Compose testing library

### Example Test
```kotlin
@Test
fun `my test`() = runTest {
    // Given
    val viewModel = MyViewModel(fakeUseCase)
    
    // When
    viewModel.onAction()
    
    // Then
    assertEquals(expected, viewModel.state.value)
}
```

## ADB Commands

Common ADB commands for debugging:
```bash
# Install app
adb install app-debug.apk

# Uninstall app
adb uninstall com.example.app

# Logcat
adb logcat | grep "MyApp"

# Clear app data
adb shell pm clear com.example.app

# Take screenshot
adb exec-out screencap -p > screenshot.png

# Record screen
adb shell screenrecord /sdcard/record.mp4
```

## Performance

- Use `LazyColumn` for scrollable lists
- Avoid heavy computations in composables
- Use `remember` to cache expensive calculations
- Profile with Android Profiler
- Watch for memory leaks

## Security

- Never store API keys in code
- Use Android Keystore for sensitive data
- Validate all user input
- Use HTTPS for network requests
- Request only necessary permissions
