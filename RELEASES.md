# Kutti Releases & Installation

This document explains how to build, release, and install Kutti on different platforms.

## 📱 Android Installation

### Option 1: Download Pre-built APK (Recommended)

1. **Go to the Releases page**: [https://github.com/wsochi4-os/kay/releases](https://github.com/wsochi4-os/kay/releases)

2. **Download the APK**:
   - **kutti-v1.0.0-debug.apk** - Debug build for development and testing
   - **kutti-v1.0.0-release.apk** - Release build for production use

3. **Transfer to your Android device**:
   - Via USB cable
   - Via cloud storage (Google Drive, Dropbox, etc.)
   - Via email or messaging app

4. **Install the APK**:
   - Open the file on your Android device
   - If blocked, enable "Unknown sources" in Settings > Security
   - Confirm installation

5. **First Run**:
   - The app will download Ubuntu rootfs (~200MB)
   - Set up the terminal environment
   - Configure AI providers
   - This may take a few minutes

### Option 2: Build from Source

#### Prerequisites
- Android Studio (latest version)
- Android SDK 34+
- Java JDK 17+
- Android NDK 26.2+
- Minimum 8GB RAM recommended

#### Build Steps

```bash
# Clone the repository
git clone https://github.com/wsochi4-os/kay.git
cd kay

# Navigate to Android project
cd packages/android

# Install dependencies (Android Studio will do this automatically)
# Or manually:
./gradlew --version

# Build debug APK
./gradlew assembleDebug

# APK will be at: app/build/outputs/apk/debug/app-debug.apk

# Build release APK (requires signing)
# See android-signing-template.properties for signing setup
./gradlew assembleRelease

# APK will be at: app/build/outputs/apk/release/app-release.apk
```

#### Signing for Release

To build a signed release APK:

1. **Create a keystore** (if you don't have one):
```bash
keytool -genkey -v -keystore release.keystore \
  -alias kutti -keyalg RSA -keysize 2048 -validity 10000
```

2. **Copy the template**:
```bash
cp ../../android-signing-template.properties app/android-signing.properties
```

3. **Edit `app/android-signing.properties`** with your keystore details:
```properties
STORE_FILE=release.keystore
STORE_PASSWORD=your_password
KEY_ALIAS=kutti
KEY_PASSWORD=your_password
```

4. **Build signed APK**:
```bash
./gradlew assembleRelease
```

## 🐍 Python Installation

### Option 1: Install from PyPI (Coming Soon)

```bash
pip install kutti
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/wsochi4-os/kay.git
cd kay

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Or build and install the package
python setup.py install
```

### Option 3: Install from Release Assets

1. Download the `.whl` or `.tar.gz` file from the [Releases page](https://github.com/wsochi4-os/kay/releases)

2. Install with pip:
```bash
pip install kutti-v1.0.0-py3-none-any.whl
# or
pip install kutti-v1.0.0.tar.gz
```

## 🚀 Quick Start

### Android

After installation:

1. **Open the Kutti app**
2. **Complete the setup wizard**:
   - Accept permissions
   - Download Ubuntu rootfs
   - Set up terminal environment
3. **Authenticate with AI providers**:
   - Go to Settings > Authentication
   - Add your API keys for OpenAI, Anthropic, Groq, etc.
4. **Start using the terminal**:
   - Open the terminal tab
   - Run commands like `ls`, `cd`, `python`, etc.
5. **Use AI features**:
   - Open the chat tab
   - Select a provider and model
   - Start chatting with AI

### Python CLI

After installation:

```bash
# Show help
python kutti.py --help

# List available providers
python kutti.py providers list

# Login to a provider
python kutti.py login openai

# Set active provider
python kutti.py providers use groq

# List available models
python kutti.py models list

# Show session info
python kutti.py session
```

## 🔄 Creating Releases

### Manual Release Process

1. **Update version**:
```bash
echo "v1.0.1" > VERSION
```

2. **Run the release script**:
```bash
chmod +x scripts/release.sh
./scripts/release.sh --version v1.0.1 --type beta
```

3. **Upload to GitHub**:
   - Go to [Releases page](https://github.com/wsochi4-os/kay/releases)
   - Click "Draft a new release"
   - Tag version: `v1.0.1`
   - Title: `Kutti v1.0.1 (beta)`
   - Upload all files from `releases/` directory
   - Copy release notes from `releases/release-notes-v1.0.1.md`
   - Publish release

### Automated Release (GitHub Actions)

The repository includes a GitHub Actions workflow that automatically:

1. **Builds Android APKs** (debug and release)
2. **Builds Python packages** (sdist and wheel)
3. **Creates GitHub releases** with all assets

#### Triggering a Release

**Option 1: Push a tag**
```bash
git tag v1.0.1
git push origin v1.0.1
```

**Option 2: Use workflow dispatch**
1. Go to Actions tab in GitHub
2. Select "Android Build and Release" workflow
3. Click "Run workflow"
4. Enter version (e.g., `v1.0.1`)
5. Select release type (alpha, beta, release)
6. Click "Run workflow"

## 📦 Release Types

| Type | Description | Use Case |
|------|-------------|----------|
| **alpha** | Early testing, may be unstable | Internal testing, developers |
| **beta** | Feature complete, minor bugs possible | Public testing, early adopters |
| **release** | Stable, production-ready | General public |

## 📋 Release Checklist

- [ ] Update `VERSION` file
- [ ] Update `CHANGELOG.md`
- [ ] Test all features
- [ ] Build debug APK
- [ ] Build release APK (if signed)
- [ ] Build Python packages
- [ ] Create GitHub release
- [ ] Upload all assets
- [ ] Write release notes
- [ ] Test installation from release assets
- [ ] Announce release

## 🔧 Troubleshooting

### Android Build Issues

**Error: Gradle not found**
- Install Android Studio or standalone Gradle
- Ensure `gradle` is in your PATH

**Error: SDK not found**
- Install Android SDK via Android Studio
- Set `ANDROID_HOME` environment variable

**Error: Keystore not found**
- Create a keystore using `keytool`
- Or use debug signing for development

### Python Installation Issues

**Error: Missing dependencies**
```bash
pip install -r requirements.txt
```

**Error: Python version too old**
- Upgrade to Python 3.8+

## 📊 Version History

| Version | Date | Type | Changes |
|---------|------|------|---------|
| v1.0.0 | 2024-XX-XX | release | Initial release |

## 🎯 Roadmap

### v1.1.0 (Planned)
- OAuth support for providers
- More AI providers
- Improved terminal features
- Better error handling

### v2.0.0 (Future)
- Plugin marketplace
- Cloud sync
- Team collaboration
- Advanced AI features

---

## 📞 Support

- **Issues**: [https://github.com/wsochi4-os/kay/issues](https://github.com/wsochi4-os/kay/issues)
- **Discussions**: [https://github.com/wsochi4-os/kay/discussions](https://github.com/wsochi4-os/kay/discussions)
- **Documentation**: [https://github.com/wsochi4-os/kay#readme](https://github.com/wsochi4-os/kay#readme)

## 🏆 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.