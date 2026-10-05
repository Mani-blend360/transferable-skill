#!/bin/bash
# Cross-platform skill installer for portfolio-performance-dashboard
# Detects platform and installs to the appropriate skills directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="portfolio-performance-dashboard"
SKILL_VERSION="1.1.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utility functions
log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

# Detect OS
detect_os() {
    case "$(uname)" in
        Darwin) echo "macos" ;;
        Linux) echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Detect agent platform (heuristic)
detect_agent_platform() {
    if [ -d ".claude" ] || [ -d "$HOME/.claude" ]; then
        echo "claude-code"
    elif [ -d ".codex" ] || [ -d "$HOME/.codex" ]; then
        echo "openai-codex"
    elif [ -d ".cortex" ] || [ -d "$HOME/.snowflake" ]; then
        echo "snowflake-cortex-code"
    else
        echo "unknown"
    fi
}

# Get install path for platform
get_install_path() {
    local platform="$1"
    local scope="$2"  # "project" or "global"

    case "$platform" in
        claude-code)
            if [ "$scope" = "global" ]; then
                echo "$HOME/.claude/skills/$SKILL_NAME"
            else
                echo ".claude/skills/$SKILL_NAME"
            fi
            ;;
        openai-codex)
            if [ "$scope" = "global" ]; then
                echo "$HOME/.codex/skills/$SKILL_NAME"
            else
                echo ".codex/skills/$SKILL_NAME"
            fi
            ;;
        snowflake-cortex-code)
            if [ "$scope" = "global" ]; then
                echo "$HOME/.snowflake/cortex/skills/$SKILL_NAME"
            else
                echo ".cortex/skills/$SKILL_NAME"
            fi
            ;;
        *)
            echo ""
            ;;
    esac
}

# Validate skill folder integrity
validate_skill() {
    log_info "Validating skill folder integrity..."

    local required_files=(
        "SKILL.md"
        "scripts/render_dashboard.py"
        "scripts/validate_dashboard_input.py"
        "references/dashboard-input-schema.md"
        "references/ui-states.md"
        "references/interaction-contract.md"
    )

    local missing=0
    for file in "${required_files[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$file" ]; then
            log_error "Missing required file: $file"
            ((missing++))
        fi
    done

    if [ $missing -gt 0 ]; then
        log_error "Skill validation failed: $missing required files missing"
        return 1
    fi

    log_success "Skill validation passed"
    return 0
}

# Verify Python availability and version
verify_python() {
    log_info "Checking Python availability..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.7 or later."
        return 1
    fi

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python $python_version found"

    # Optional: verify tests pass
    if [ "$1" = "--test" ]; then
        log_info "Running test suite..."
        if python3 "$SCRIPT_DIR/tests/test_validate_dashboard_input.py" &>/dev/null; then
            log_success "Test suite passed"
        else
            log_warning "Test suite had issues; installation will continue"
        fi
    fi

    return 0
}

# Perform installation
install_skill() {
    local platform="$1"
    local scope="$2"
    local install_path="$3"

    log_info "Installing $SKILL_NAME v$SKILL_VERSION to $install_path"

    # Create directory if it doesn't exist
    if [ ! -d "$(dirname "$install_path")" ]; then
        mkdir -p "$(dirname "$install_path")"
        log_success "Created directory: $(dirname "$install_path")"
    fi

    # Remove existing installation if present
    if [ -d "$install_path" ]; then
        log_warning "Existing installation found; backing up to ${install_path}.bak"
        rm -rf "${install_path}.bak" 2>/dev/null || true
        mv "$install_path" "${install_path}.bak"
    fi

    # Copy skill folder
    cp -r "$SCRIPT_DIR" "$install_path"
    log_success "Installed to: $install_path"

    # Set executable permissions on scripts
    chmod +x "$install_path/scripts/render_dashboard.py" 2>/dev/null || true
    chmod +x "$install_path/scripts/validate_dashboard_input.py" 2>/dev/null || true
    chmod +x "$install_path/scripts/publish_request.py" 2>/dev/null || true
    chmod +x "$install_path/scripts/dry_run_platforms.py" 2>/dev/null || true
    chmod +x "$install_path/install.sh" 2>/dev/null || true

    # Verify installation
    if [ ! -f "$install_path/SKILL.md" ]; then
        log_error "Installation verification failed"
        return 1
    fi

    log_success "Installation verified"

    return 0
}

# Show usage instructions
show_usage_instructions() {
    local platform="$1"
    local install_path="$2"

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Skill: $SKILL_NAME v$SKILL_VERSION"
    echo "Platform: $platform"
    echo "Location: $install_path"
    echo ""

    case "$platform" in
        claude-code)
            echo -e "${YELLOW}Next steps for Claude Code:${NC}"
            echo "  1. After running portfolio-monthly-performance-analysis"
            echo "  2. Ask: 'Show the dashboard for the results'"
            echo "  3. Dashboard renders with interactive visualizations"
            ;;
        openai-codex)
            echo -e "${YELLOW}Next steps for OpenAI Codex:${NC}"
            echo "  1. After portfolio-monthly-performance-analysis completes"
            echo "  2. Invoke: portfolio-performance-dashboard <RESULTS.json>"
            echo "  3. Dashboard appears in Codex chat"
            ;;
        snowflake-cortex-code)
            echo -e "${YELLOW}Next steps for Snowflake Cortex Code:${NC}"
            echo "  1. After analysis results are available"
            echo "  2. Invoke: \$portfolio-performance-dashboard"
            echo "  3. Or: 'Render the dashboard for these results'"
            ;;
    esac

    echo ""
    echo -e "${YELLOW}Quick test:${NC}"
    echo "  cd '$install_path'"
    echo "  python3 scripts/validate_dashboard_input.py ../portfolio-monthly-performance-analysis/test-results.json"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - SKILL.md for full usage instructions"
    echo "  - references/dashboard-input-schema.md for input format"
    echo "  - references/ui-states.md for rendering states"
    echo ""
}

# Main installer flow
main() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ Portfolio Performance Dashboard Skill Installer           ║${NC}"
    echo -e "${BLUE}║ Cross-platform for Claude Code, Codex, Cortex Code       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Parse command-line arguments
    local platform=""
    local scope="project"  # Default to project scope
    local skip_test=true

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --platform)
                platform="$2"
                shift 2
                ;;
            --global)
                scope="global"
                shift
                ;;
            --test)
                skip_test=false
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Detect platform if not specified
    if [ -z "$platform" ]; then
        platform=$(detect_agent_platform)
        if [ "$platform" = "unknown" ]; then
            log_warning "Could not auto-detect platform"
            echo ""
            echo "Available platforms:"
            echo "  --platform claude-code          for Claude Code"
            echo "  --platform openai-codex         for OpenAI Codex (legacy)"
            echo "  --platform snowflake-cortex-code for Snowflake Cortex Code"
            echo ""
            read -p "Select platform (or press Ctrl+C to cancel): " platform
        fi
    fi

    # Validate selected platform
    case "$platform" in
        claude-code|openai-codex|snowflake-cortex-code) ;;
        *)
            log_error "Unknown platform: $platform"
            exit 1
            ;;
    esac

    log_info "Platform: $platform"
    log_info "Scope: $scope"
    echo ""

    # Validate skill folder
    if ! validate_skill; then
        exit 1
    fi

    # Verify Python
    if ! verify_python $([ "$skip_test" = false ] && echo "--test"); then
        exit 1
    fi

    # Get installation path
    local install_path=$(get_install_path "$platform" "$scope")
    if [ -z "$install_path" ]; then
        log_error "Could not determine install path for platform: $platform"
        exit 1
    fi

    echo ""

    # Confirm before installation
    echo -e "${YELLOW}Installing to: $install_path${NC}"
    read -p "Continue? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled"
        exit 0
    fi

    # Perform installation
    if install_skill "$platform" "$scope" "$install_path"; then
        show_usage_instructions "$platform" "$install_path"
        log_success "Done!"
        exit 0
    else
        log_error "Installation failed"
        exit 1
    fi
}

# Show help
show_help() {
    cat << EOF
Usage: ./install.sh [OPTIONS]

Install the portfolio-performance-dashboard skill to your platform.

OPTIONS:
  --platform PLATFORM    Target platform (claude-code, openai-codex, snowflake-cortex-code)
                        Auto-detected if not specified
  --global              Install globally (~/.claude/skills, etc.) instead of project-local
  --test                Run test suite after validation (recommended)
  --help                Show this help message

EXAMPLES:
  # Auto-detect and install locally
  ./install.sh

  # Install globally for Claude Code
  ./install.sh --platform claude-code --global

  # Install and run tests
  ./install.sh --test

PLATFORMS:
  claude-code           Claude Code (VS Code, JetBrains, Web, CLI)
  openai-codex          OpenAI Codex (legacy support)
  snowflake-cortex-code Snowflake Cortex Code

For more information, see SKILL.md
EOF
}

# Run main function
main "$@"
