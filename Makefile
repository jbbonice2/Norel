# Makefile for LoRaWAN NS-3.42 Integration
# Simplifies building and running the LoRaWAN simulator

# Configuration
NS3_PATH ?= /opt/ns-3.42
BUILD_DIR = $(NS3_PATH)/build
LORAWAN_DIR = $(NS3_PATH)/src/lorawan/examples
SIM_BINARY = $(BUILD_DIR)/src/lorawan/examples/lorawan-simulation
RESULTS_DIR = results

# Default target
.PHONY: all
all: build

# Help target
.PHONY: help
help:
	@echo "LoRaWAN NS-3.42 Simulator Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build the NS-3 simulator"
	@echo "  install        - Copy source files to NS-3 directory"
	@echo "  clean          - Clean build artifacts"
	@echo "  test           - Run a quick test simulation"
	@echo "  scenarios      - Run all experimental scenarios"
	@echo "  analyze        - Analyze latest results"
	@echo "  demo           - Run demo simulation with visualization"
	@echo "  help           - Show this help message"
	@echo ""
	@echo "Configuration:"
	@echo "  NS3_PATH       - Path to NS-3 installation (default: /opt/ns-3.42)"
	@echo "  RESULTS_DIR    - Results directory (default: results)"
	@echo ""
	@echo "Examples:"
	@echo "  make NS3_PATH=/home/user/ns-3.42 build"
	@echo "  make test"
	@echo "  make scenarios"

# Check if NS-3 path exists
.PHONY: check-ns3
check-ns3:
	@if [ ! -d "$(NS3_PATH)" ]; then \
		echo "Error: NS-3 path not found: $(NS3_PATH)"; \
		echo "Please set NS3_PATH to your NS-3 installation directory"; \
		echo "Example: make NS3_PATH=/path/to/ns-3.42 build"; \
		exit 1; \
	fi
	@if [ ! -f "$(NS3_PATH)/ns3" ]; then \
		echo "Error: NS-3 build script not found at $(NS3_PATH)/ns3"; \
		echo "Please ensure NS-3 is properly installed"; \
		exit 1; \
	fi

# Install source files to NS-3 directory
.PHONY: install
install: check-ns3
	@echo "Installing LoRaWAN simulator source to NS-3..."
	@mkdir -p $(LORAWAN_DIR)
	@cp src/lorawan-simulation.cc $(LORAWAN_DIR)/
	@echo "Source files installed successfully"

# Build the simulator
.PHONY: build
build: check-ns3 install
	@echo "Building NS-3 with LoRaWAN simulator..."
	cd $(NS3_PATH) && ./ns3 configure --enable-examples --enable-tests
	cd $(NS3_PATH) && ./ns3 build
	@if [ -f "$(SIM_BINARY)" ]; then \
		echo "Build successful! Simulator at: $(SIM_BINARY)"; \
	else \
		echo "Build failed! Please check NS-3 build logs"; \
		exit 1; \
	fi

# Clean build artifacts
.PHONY: clean
clean: check-ns3
	@echo "Cleaning NS-3 build artifacts..."
	cd $(NS3_PATH) && ./ns3 clean
	@echo "Clean completed"

# Run a quick test simulation
.PHONY: test
test: build
	@echo "Running test simulation..."
	@mkdir -p $(RESULTS_DIR)/test
	$(SIM_BINARY) \
		--nDevices=50 \
		--simulationTime=300 \
		--algorithm=0 \
		--scenarioName="test" \
		--outputFile="$(RESULTS_DIR)/test/test_results.txt"
	@echo "Test simulation completed"
	@echo "Results saved to: $(RESULTS_DIR)/test/"

# Run all experimental scenarios
.PHONY: scenarios
scenarios: build
	@echo "Running all experimental scenarios..."
	@echo "This may take several hours depending on your system"
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh
	@echo "All scenarios completed"

# Analyze latest results
.PHONY: analyze
analyze:
	@echo "Analyzing latest simulation results..."
	@LATEST_DIR=$$(find $(RESULTS_DIR) -name "session_*" -type d | sort | tail -1); \
	if [ -n "$$LATEST_DIR" ]; then \
		echo "Analyzing results in: $$LATEST_DIR"; \
		python3 scripts/analysis/analyze-results.py "$$LATEST_DIR"; \
	else \
		echo "No simulation results found in $(RESULTS_DIR)"; \
		echo "Please run 'make scenarios' or 'make test' first"; \
	fi

# Run demo simulation with multiple algorithms
.PHONY: demo
demo: build
	@echo "Running demonstration with multiple algorithms..."
	@mkdir -p $(RESULTS_DIR)/demo
	@for algo in 0 1 2 3 4 5; do \
		echo "Running algorithm $$algo..."; \
		$(SIM_BINARY) \
			--nDevices=100 \
			--simulationTime=600 \
			--algorithm=$$algo \
			--scenarioName="demo_algo$$algo" \
			--outputFile="$(RESULTS_DIR)/demo/demo_algo$$algo.txt"; \
	done
	@echo "Demo completed. Analyzing results..."
	@python3 scripts/analysis/analyze-results.py "$(RESULTS_DIR)/demo"

# Install Python dependencies
.PHONY: install-python-deps
install-python-deps:
	@echo "Installing Python dependencies for analysis..."
	pip3 install numpy pandas matplotlib seaborn pathlib
	@echo "Python dependencies installed"

# Quick setup for new users
.PHONY: setup
setup: install-python-deps build test
	@echo "Setup completed successfully!"
	@echo "You can now run:"
	@echo "  make scenarios  - Run all experimental scenarios"
	@echo "  make demo       - Run demonstration"
	@echo "  make analyze    - Analyze results"

# Run specific scenario
.PHONY: scenario1 scenario2 scenario3 scenario4 scenario5
scenario1: build
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh 1

scenario2: build
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh 2

scenario3: build
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh 3

scenario4: build
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh 4

scenario5: build
	NS3_BUILD_DIR=$(BUILD_DIR) ./scripts/run-scenarios.sh 5

# Check simulator binary
.PHONY: check-binary
check-binary:
	@if [ -f "$(SIM_BINARY)" ]; then \
		echo "Simulator binary found: $(SIM_BINARY)"; \
		echo "Version info:"; \
		$(SIM_BINARY) --version 2>/dev/null || echo "No version info available"; \
	else \
		echo "Simulator binary not found. Please run 'make build' first"; \
	fi

# Show system information
.PHONY: info
info:
	@echo "LoRaWAN NS-3.42 Simulator Information"
	@echo "====================================="
	@echo "NS-3 Path:         $(NS3_PATH)"
	@echo "Build Directory:   $(BUILD_DIR)"
	@echo "LoRaWAN Examples:  $(LORAWAN_DIR)"
	@echo "Simulator Binary:  $(SIM_BINARY)"
	@echo "Results Directory: $(RESULTS_DIR)"
	@echo ""
	@echo "System Information:"
	@echo "OS:                $$(uname -s)"
	@echo "Architecture:      $$(uname -m)"
	@echo "GCC Version:       $$(gcc --version 2>/dev/null | head -1 || echo 'Not found')"
	@echo "Python Version:    $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo ""
	@echo "NS-3 Status:"
	@if [ -d "$(NS3_PATH)" ]; then \
		echo "NS-3 Directory:    Found"; \
	else \
		echo "NS-3 Directory:    Not found"; \
	fi
	@if [ -f "$(SIM_BINARY)" ]; then \
		echo "Simulator Binary:  Built"; \
	else \
		echo "Simulator Binary:  Not built"; \
	fi

# Debug build for development
.PHONY: debug
debug: check-ns3 install
	@echo "Building NS-3 in debug mode..."
	cd $(NS3_PATH) && ./ns3 configure --build-profile=debug --enable-examples --enable-tests
	cd $(NS3_PATH) && ./ns3 build
	@echo "Debug build completed"

# Optimized build for performance
.PHONY: optimized
optimized: check-ns3 install
	@echo "Building NS-3 in optimized mode..."
	cd $(NS3_PATH) && ./ns3 configure --build-profile=optimized --enable-examples --enable-tests
	cd $(NS3_PATH) && ./ns3 build
	@echo "Optimized build completed"

# Create documentation
.PHONY: docs
docs:
	@echo "Generating documentation..."
	@if command -v doxygen >/dev/null 2>&1; then \
		doxygen Doxyfile 2>/dev/null || echo "Doxygen configuration not found"; \
	else \
		echo "Doxygen not found. Please install doxygen to generate documentation"; \
	fi

# Package results for sharing
.PHONY: package
package:
	@echo "Packaging simulation results..."
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "lorawan_results_$$TIMESTAMP.tar.gz" $(RESULTS_DIR)/; \
	echo "Results packaged as: lorawan_results_$$TIMESTAMP.tar.gz"

# Validate installation
.PHONY: validate
validate: check-ns3
	@echo "Validating installation..."
	@echo "Checking NS-3 installation..."
	@if [ -f "$(NS3_PATH)/ns3" ]; then \
		echo "✓ NS-3 build script found"; \
	else \
		echo "✗ NS-3 build script missing"; \
	fi
	@if [ -d "$(NS3_PATH)/src/lorawan" ]; then \
		echo "✓ LoRaWAN module found"; \
	else \
		echo "✗ LoRaWAN module missing"; \
	fi
	@echo "Checking Python dependencies..."
	@python3 -c "import numpy, pandas, matplotlib, seaborn" 2>/dev/null && \
		echo "✓ Python dependencies available" || \
		echo "✗ Python dependencies missing (run 'make install-python-deps')"
	@echo "Checking simulator binary..."
	@if [ -f "$(SIM_BINARY)" ]; then \
		echo "✓ Simulator binary built"; \
	else \
		echo "✗ Simulator binary missing (run 'make build')"; \
	fi
	@echo "Validation completed"