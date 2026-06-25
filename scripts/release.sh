#!/bin/bash

# Kutti Release Script
# Automates the process of creating releases for Android and Python packages

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
ANDROID_DIR="$REPO_ROOT/packages/android"
BUILD_DIR="$ANDROID_DIR/app/build/outputs/apk"
RELEASE_DIR="$REPO_ROOT/releases"
VERSION_FILE="$REPO_ROOT/VERSION"
CHANGELOG_FILE="$REPO_ROOT/CHANGELOG.md"

# Default values
VERSION=""
RELEASE_TYPE="beta"
BUILD_DEBUG=true
BUILD_RELEASE=true
BUILD_PYTHON=true
CREATE_RELEASE=true
UPLOAD_GITHUB=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --version|-v)
            VERSION="$2"
            shift 2
            ;;
        --type|-t)
            RELEASE_TYPE="$2"
            shift 2
            ;;
        --no-debug)
            BUILD_DEBUG=false
            shift
            ;;
        --no-release)
            BUILD_RELEASE=false
            shift
            ;;
        --no-python)
            BUILD_PYTHON=false
            shift
            ;;
        --no-github)
            CREATE_RELEASE=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --version, -v VERSION   Release version (e.g., v1.0.0)"
            echo "  --type, -t TYPE        Release type: alpha, beta, release (default: beta)"
            echo "  --no-debug            Skip debug APK build"
            echo "  --no-release           Skip release APK build"
            echo "  --no-python           Skip Python package build"
            echo "  --no-github           Skip GitHub release creation"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --version v1.0.0 --type release"
            echo "  $0 --version v0.1.0 --type alpha --no-release"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to print colored messages
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if we have a version
if [ -z "$VERSION" ]; then
    # Try to get version from git tag
    if git rev-parse --verify --tags "$(git tag --sort=-version:refname | head -1)" >/dev/null 2>&1; then
        VERSION=$(git tag --sort=-version:refname | head -1)
    else
        # Try to get from VERSION file
        if [ -f "$VERSION_FILE" ]; then
            VERSION=$(cat "$VERSION_FILE")
        else
            # Use timestamp
            VERSION="v1.0.0-$(date +%Y%m%d%H%M)"
        fi
    fi
fi

# Create releases directory
mkdir -p "$RELEASE_DIR"

print_header "Kutti Release $VERSION ($RELEASE_TYPE)"

# Step 1: Build Android APKs
if [ "$BUILD_DEBUG" = true ] || [ "$BUILD_RELEASE" = true ]; then
    print_header "Building Android APKs"
    
    cd "$ANDROID_DIR"
    
    # Install dependencies
    print_warning "Installing Android dependencies..."
    ./gradlew --version >/dev/null 2>&1 || {
        print_error "Gradle not found. Please install Android Studio or Gradle."
        exit 1
    }
    
    # Build debug APK
    if [ "$BUILD_DEBUG" = true ]; then
        print_warning "Building debug APK..."
        ./gradlew assembleDebug --no-daemon --stacktrace || {
            print_error "Debug APK build failed"
            exit 1
        }
        
        # Copy and rename debug APK
        if [ -f "$BUILD_DIR/debug/app-debug.apk" ]; then
            cp "$BUILD_DIR/debug/app-debug.apk" "$RELEASE_DIR/kutti-${VERSION}-debug.apk"
            print_success "Debug APK created: kutti-${VERSION}-debug.apk"
        fi
    fi
    
    # Build release APK
    if [ "$BUILD_RELEASE" = true ]; then
        print_warning "Building release APK..."
        
        # Check for signing config
        if [ -f "app/release.keystore" ]; then
            ./gradlew assembleRelease --no-daemon --stacktrace || {
                print_error "Release APK build failed"
                exit 1
            }
        else
            print_warning "No release keystore found. Using debug signing for release build."
            ./gradlew assembleDebug --no-daemon --stacktrace || {
                print_error "Release APK build failed"
                exit 1
            }
            cp "$BUILD_DIR/debug/app-debug.apk" "$RELEASE_DIR/kutti-${VERSION}-release.apk"
        fi
        
        # Copy and rename release APK
        if [ -f "$BUILD_DIR/release/app-release.apk" ]; then
            cp "$BUILD_DIR/release/app-release.apk" "$RELEASE_DIR/kutti-${VERSION}-release.apk"
            print_success "Release APK created: kutti-${VERSION}-release.apk"
        fi
    fi
    
    cd "$REPO_ROOT"
fi

# Step 2: Build Python package
if [ "$BUILD_PYTHON" = true ]; then
    print_header "Building Python Package"
    
    cd "$REPO_ROOT"
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || {
            print_error "Failed to install Python dependencies"
            exit 1
        }
    fi
    
    # Build package
    python setup.py sdist bdist_wheel || {
        print_error "Python package build failed"
        exit 1
    }
    
    # Copy Python packages to release directory
    if [ -d "dist" ]; then
        cp dist/* "$RELEASE_DIR/" || true
        print_success "Python packages created in $RELEASE_DIR/"
    fi
fi

# Step 3: Create changelog
print_header "Creating Changelog"

if [ -f "$CHANGELOG_FILE" ]; then
    # Update existing changelog
    echo "" >> "$CHANGELOG_FILE"
    echo "## $VERSION ($RELEASE_TYPE) - $(date +%Y-%m-%d)" >> "$CHANGELOG_FILE"
    echo "" >> "$CHANGELOG_FILE"
    echo "### Features" >> "$CHANGELOG_FILE"
    echo "- Complete personal AI CLI agent for Android" >> "$CHANGELOG_FILE"
    echo "- Built-in terminal emulator with Ubuntu environment" >> "$CHANGELOG_FILE"
    echo "- Multi-provider authentication support (9 providers)" >> "$CHANGELOG_FILE"
    echo "- OpenCode-compatible authentication system" >> "$CHANGELOG_FILE"
    echo "" >> "$CHANGELOG_FILE"
    echo "### Bug Fixes" >> "$CHANGELOG_FILE"
    echo "- Initial release" >> "$CHANGELOG_FILE"
    echo "" >> "$CHANGELOG_FILE"
    print_success "Changelog updated"
else
    # Create new changelog
    cat > "$CHANGELOG_FILE" << EOF
# Kutti Changelog

## $VERSION ($RELEASE_TYPE) - $(date +%Y-%m-%d)

### Features
- Complete personal AI CLI agent for Android
- Built-in terminal emulator with Ubuntu environment
- Multi-provider authentication support (9 providers)
- OpenCode-compatible authentication system

### Bug Fixes
- Initial release

---

All notable changes to this project will be documented in this file.
EOF
    print_success "Changelog created"
fi

# Step 4: Create GitHub release
if [ "$CREATE_RELEASE" = true ]; then
    print_header "Creating GitHub Release"
    
    # Check if we're in a git repository
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        # Create git tag
        git tag "$VERSION" || {
            print_warning "Failed to create git tag (may already exist)"
        }
        
        # Push tag
        git push origin "$VERSION" || {
            print_warning "Failed to push git tag"
        }
        
        # Create release notes
        RELEASE_NOTES="$RELEASE_DIR/release-notes-$VERSION.md"
        cat > "$RELEASE_NOTES" << EOF
# Kutti $VERSION ($RELEASE_TYPE)

## 🎉 What's New

Complete personal AI CLI agent for Android with built-in terminal emulator and Ubuntu environment.

### 📱 Android Features
- Full terminal emulator with Termux libraries
- Ubuntu environment via proot
- Multi-provider AI authentication
- Offline-capable development tools
- Agent loop with THINK→ACT→OBSERVE→EVALUATE phases

### 🐍 Python Features
- OpenCode-compatible authentication system
- 9 AI provider implementations (OpenAI, Anthropic, Groq, OpenRouter, Mistral, Gemini, Fireworks, Together, DeepSeek)
- Secure credential storage with multiple backends
- Dynamic model discovery and caching
- Unified request router

### 📦 Assets
- **kutti-${VERSION}-debug.apk**: Debug build for development and testing
- **kutti-${VERSION}-release.apk**: Release build for production use
- **kutti-${VERSION}.tar.gz**: Python source distribution
- **kutti-${VERSION}-py3-none-any.whl**: Python wheel package

### 🚀 Installation

#### Android
1. Download the APK file from assets below
2. Transfer to your Android device
3. Install the APK (enable "Unknown sources" in Settings > Security if needed)
4. Open Kutti and follow the setup instructions

#### Python
```bash
pip install kutti-${VERSION}-py3-none-any.whl
# or
pip install kutti-${VERSION}.tar.gz
```

### ⚠️ Requirements

**Android:**
- Android 8.0+ (API 26+)
- Minimum 2GB RAM recommended
- 500MB+ free storage for Ubuntu environment
- Internet connection for initial setup

**Python:**
- Python 3.8+
- pip 21.0+

### 🔧 First Run

On first launch, the Android app will:
1. Download Ubuntu rootfs (~200MB)
2. Set up the terminal environment
3. Configure the AI providers

This may take a few minutes depending on your internet speed.

### 📝 Notes
- Debug builds have full logging enabled
- Release builds are optimized for production use
- Both builds include all features and providers
- Python package includes the OpenCode-compatible authentication system

---

**Full Changelog**: [CHANGELOG.md](https://github.com/wsochi4-os/kay/blob/$VERSION/CHANGELOG.md)
EOF
        
        print_success "Release notes created"
        
        # List all release files
        print_warning "Release files:"
        ls -lh "$RELEASE_DIR/"
        
        print_success ""
        print_success "Release $VERSION ($RELEASE_TYPE) created successfully!"
        print_success ""
        print_success "Next steps:"
        print_success "1. Go to GitHub Releases page: https://github.com/wsochi4-os/kay/releases"
        print_success "2. Create a new release with tag $VERSION"
        print_success "3. Upload all files from $RELEASE_DIR/"
        print_success "4. Use the release notes from $RELEASE_NOTES"
        
    else
        print_warning "Not in a git repository. Skipping GitHub release creation."
    fi
fi

# Final summary
print_header "Release Summary"
echo ""
echo "Version: $VERSION"
echo "Type: $RELEASE_TYPE"
echo "Release directory: $RELEASE_DIR"
echo ""

if [ "$BUILD_DEBUG" = true ]; then
    if [ -f "$RELEASE_DIR/kutti-${VERSION}-debug.apk" ]; then
        echo "✓ Debug APK: kutti-${VERSION}-debug.apk"
        du -h "$RELEASE_DIR/kutti-${VERSION}-debug.apk"
    fi
fi

if [ "$BUILD_RELEASE" = true ]; then
    if [ -f "$RELEASE_DIR/kutti-${VERSION}-release.apk" ]; then
        echo "✓ Release APK: kutti-${VERSION}-release.apk"
        du -h "$RELEASE_DIR/kutti-${VERSION}-release.apk"
    fi
fi

if [ "$BUILD_PYTHON" = true ]; then
    for file in "$RELEASE_DIR"/*.tar.gz "$RELEASE_DIR"/*.whl; do
        if [ -f "$file" ]; then
            echo "✓ Python package: $(basename "$file")"
            du -h "$file"
        fi
    done
fi

echo ""
print_success "Release process completed!"

# Cleanup
# Remove build artifacts if requested
# Uncomment the following lines to clean up build files
# rm -rf "$ANDROID_DIR/app/build"
# rm -rf "$REPO_ROOT/dist"

# Remove pycache
find "$REPO_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

exit 0