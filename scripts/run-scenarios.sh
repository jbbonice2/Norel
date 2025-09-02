#!/bin/bash

# ============================================================================
# LoRaWAN Simulation Scenarios Automation Script
# Compatible with NS-3.42 LoRaWAN Module
# 
# Implements 5 comprehensive scenarios based on experiment_scenarios.py:
# 1. Device Density Variation
# 2. Spreading Factor Variation  
# 3. Transmission Interval Variation
# 4. Mobility Variation
# 5. Network Density Variation
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================================================
# Configuration and Setup
# ============================================================================

# Simulation binary path (adjust for your NS-3 installation)
NS3_BUILD_DIR="${NS3_BUILD_DIR:-../../build}"
SIMULATOR="${NS3_BUILD_DIR}/src/lorawan/examples/lorawan-simulation"

# Results directory
RESULTS_DIR="$(dirname "$0")/../results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SESSION_DIR="${RESULTS_DIR}/session_${TIMESTAMP}"

# Default simulation parameters
DEFAULT_SIMULATION_TIME=3600    # 1 hour
DEFAULT_NETWORK_RADIUS=2000     # 2km radius (4km² area)
DEFAULT_PAYLOAD_SIZE=50         # bytes
DEFAULT_RANDOM_SEED=1

# Algorithm mappings
declare -A ALGORITHMS=(
    ["random"]=0
    ["round-robin"]=1
    ["adr"]=2
    ["d-lora"]=3
    ["rs-lora"]=4
    ["norel"]=5
)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# Utility Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_scenario() {
    echo -e "${PURPLE}[SCENARIO]${NC} $1"
}

# Create directory structure
setup_directories() {
    log_info "Setting up directory structure..."
    mkdir -p "${SESSION_DIR}"
    mkdir -p "${SESSION_DIR}/scenario1_device_density"
    mkdir -p "${SESSION_DIR}/scenario2_sf_variation"
    mkdir -p "${SESSION_DIR}/scenario3_interval_variation"
    mkdir -p "${SESSION_DIR}/scenario4_mobility_variation"
    mkdir -p "${SESSION_DIR}/scenario5_network_density"
    
    # Create summary directory
    mkdir -p "${SESSION_DIR}/summary"
    
    log_success "Directories created in ${SESSION_DIR}"
}

# Check if NS-3 simulator exists
check_simulator() {
    if [ ! -f "${SIMULATOR}" ]; then
        log_error "Simulator not found at ${SIMULATOR}"
        log_info "Please build NS-3 first or set NS3_BUILD_DIR environment variable"
        log_info "Example: export NS3_BUILD_DIR=/path/to/ns3/build"
        exit 1
    fi
    log_success "Simulator found at ${SIMULATOR}"
}

# Run a single simulation
run_simulation() {
    local scenario_name="$1"
    local algorithm="$2"
    local devices="$3"
    local gateways="$4"
    local sim_time="$5"
    local app_period="$6"
    local payload_size="$7"
    local network_radius="$8"
    local mobility_speed="$9"
    local mobility_percentage="${10}"
    local fixed_sf="${11}"
    local output_dir="${12}"
    
    local output_file="${output_dir}/${scenario_name}_${algorithm}_dev${devices}.txt"
    local algo_num="${ALGORITHMS[$algorithm]}"
    
    log_info "Running: ${scenario_name} with ${algorithm} algorithm (${devices} devices)"
    
    # Execute simulation
    "${SIMULATOR}" \
        --nDevices="${devices}" \
        --nGateways="${gateways}" \
        --simulationTime="${sim_time}" \
        --appPeriod="${app_period}" \
        --payloadSize="${payload_size}" \
        --algorithm="${algo_num}" \
        --networkRadius="${network_radius}" \
        --mobilitySpeed="${mobility_speed}" \
        --mobilityPercentage="${mobility_percentage}" \
        --fixedSF="${fixed_sf}" \
        --scenarioName="${scenario_name}" \
        --randomSeed="${DEFAULT_RANDOM_SEED}" \
        --outputFile="${output_file}" \
        > "${output_file}.log" 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "Completed: ${scenario_name} with ${algorithm}"
    else
        log_error "Failed: ${scenario_name} with ${algorithm}"
        return 1
    fi
}

# ============================================================================
# Scenario 1: Device Density Variation
# ============================================================================
scenario1_device_density() {
    log_scenario "Starting Scenario 1: Device Density Variation"
    log_info "Testing: 50, 200, 400, 700, 1000 devices on 4 km² area"
    log_info "Fixed: 15-minute intervals, 50-byte payload"
    
    local output_dir="${SESSION_DIR}/scenario1_device_density"
    local device_counts=(50 200 400 700 1000)
    local algorithms=("random" "round-robin" "adr" "d-lora" "rs-lora" "norel")
    
    local total_runs=$((${#device_counts[@]} * ${#algorithms[@]}))
    local current_run=0
    
    for devices in "${device_counts[@]}"; do
        for algorithm in "${algorithms[@]}"; do
            current_run=$((current_run + 1))
            log_info "Progress: ${current_run}/${total_runs} - Testing ${devices} devices with ${algorithm}"
            
            run_simulation \
                "scenario1_density" \
                "${algorithm}" \
                "${devices}" \
                1 \
                "${DEFAULT_SIMULATION_TIME}" \
                900 \
                "${DEFAULT_PAYLOAD_SIZE}" \
                "${DEFAULT_NETWORK_RADIUS}" \
                0 \
                0 \
                7 \
                "${output_dir}"
        done
    done
    
    log_success "Scenario 1 completed: ${total_runs} simulations"
}

# ============================================================================
# Scenario 2: Spreading Factor Variation
# ============================================================================
scenario2_sf_variation() {
    log_scenario "Starting Scenario 2: Spreading Factor Variation"
    log_info "Testing: SF7, SF8, SF9, SF10, SF12 with 200 nodes"
    log_info "Analysis: Impact on network load"
    
    local output_dir="${SESSION_DIR}/scenario2_sf_variation"
    local sf_values=(7 8 9 10 12)
    local algorithms=("random" "round-robin" "adr" "d-lora" "rs-lora" "norel")
    
    local total_runs=$((${#sf_values[@]} * ${#algorithms[@]}))
    local current_run=0
    
    for sf in "${sf_values[@]}"; do
        for algorithm in "${algorithms[@]}"; do
            current_run=$((current_run + 1))
            log_info "Progress: ${current_run}/${total_runs} - Testing SF${sf} with ${algorithm}"
            
            run_simulation \
                "scenario2_sf${sf}" \
                "${algorithm}" \
                200 \
                1 \
                "${DEFAULT_SIMULATION_TIME}" \
                900 \
                "${DEFAULT_PAYLOAD_SIZE}" \
                "${DEFAULT_NETWORK_RADIUS}" \
                0 \
                0 \
                "${sf}" \
                "${output_dir}"
        done
    done
    
    log_success "Scenario 2 completed: ${total_runs} simulations"
}

# ============================================================================
# Scenario 3: Transmission Interval Variation
# ============================================================================
scenario3_interval_variation() {
    log_scenario "Starting Scenario 3: Transmission Interval Variation"
    log_info "Testing: 5, 10, 15, 30, 60 minute intervals with 200 devices"
    log_info "Analysis: Impact on traffic load"
    
    local output_dir="${SESSION_DIR}/scenario3_interval_variation"
    local intervals=(300 600 900 1800 3600)  # 5, 10, 15, 30, 60 minutes in seconds
    local interval_names=("5min" "10min" "15min" "30min" "60min")
    local algorithms=("random" "round-robin" "adr" "d-lora" "rs-lora" "norel")
    
    local total_runs=$((${#intervals[@]} * ${#algorithms[@]}))
    local current_run=0
    
    for i in "${!intervals[@]}"; do
        local interval="${intervals[$i]}"
        local interval_name="${interval_names[$i]}"
        
        for algorithm in "${algorithms[@]}"; do
            current_run=$((current_run + 1))
            log_info "Progress: ${current_run}/${total_runs} - Testing ${interval_name} interval with ${algorithm}"
            
            run_simulation \
                "scenario3_interval_${interval_name}" \
                "${algorithm}" \
                200 \
                1 \
                "${DEFAULT_SIMULATION_TIME}" \
                "${interval}" \
                "${DEFAULT_PAYLOAD_SIZE}" \
                "${DEFAULT_NETWORK_RADIUS}" \
                0 \
                0 \
                7 \
                "${output_dir}"
        done
    done
    
    log_success "Scenario 3 completed: ${total_runs} simulations"
}

# ============================================================================
# Scenario 4: Mobility Variation
# ============================================================================
scenario4_mobility_variation() {
    log_scenario "Starting Scenario 4: Mobility Variation"
    log_info "Testing: 0%, 25%, 50%, 75%, 100% mobility with 150 nodes"
    log_info "Speed range: 5-30 km/h, random trajectories"
    
    local output_dir="${SESSION_DIR}/scenario4_mobility_variation"
    local mobility_percentages=(0 25 50 75 100)
    local algorithms=("random" "round-robin" "adr" "d-lora" "rs-lora" "norel")
    local mobility_speed=8.33  # Average speed ~30 km/h in m/s
    
    local total_runs=$((${#mobility_percentages[@]} * ${#algorithms[@]}))
    local current_run=0
    
    for mobility_pct in "${mobility_percentages[@]}"; do
        for algorithm in "${algorithms[@]}"; do
            current_run=$((current_run + 1))
            log_info "Progress: ${current_run}/${total_runs} - Testing ${mobility_pct}% mobility with ${algorithm}"
            
            run_simulation \
                "scenario4_mobility_${mobility_pct}pct" \
                "${algorithm}" \
                150 \
                1 \
                "${DEFAULT_SIMULATION_TIME}" \
                900 \
                "${DEFAULT_PAYLOAD_SIZE}" \
                "${DEFAULT_NETWORK_RADIUS}" \
                "${mobility_speed}" \
                "${mobility_pct}" \
                7 \
                "${output_dir}"
        done
    done
    
    log_success "Scenario 4 completed: ${total_runs} simulations"
}

# ============================================================================
# Scenario 5: Network Density Variation
# ============================================================================
scenario5_network_density() {
    log_scenario "Starting Scenario 5: Network Density Variation"
    log_info "Testing: 50, 100, 200, 300, 400 nodes (12.5 to 100 nodes/km²)"
    log_info "Analysis: Scalability performance"
    
    local output_dir="${SESSION_DIR}/scenario5_network_density"
    local node_counts=(50 100 200 300 400)
    local algorithms=("random" "round-robin" "adr" "d-lora" "rs-lora" "norel")
    
    local total_runs=$((${#node_counts[@]} * ${#algorithms[@]}))
    local current_run=0
    
    for nodes in "${node_counts[@]}"; do
        # Calculate density: nodes per km² (area = π * r² = π * 2² = ~12.57 km²)
        local density=$(echo "scale=1; ${nodes} / 12.57" | bc -l)
        
        for algorithm in "${algorithms[@]}"; do
            current_run=$((current_run + 1))
            log_info "Progress: ${current_run}/${total_runs} - Testing ${nodes} nodes (${density} nodes/km²) with ${algorithm}"
            
            run_simulation \
                "scenario5_density_${nodes}nodes" \
                "${algorithm}" \
                "${nodes}" \
                1 \
                "${DEFAULT_SIMULATION_TIME}" \
                900 \
                "${DEFAULT_PAYLOAD_SIZE}" \
                "${DEFAULT_NETWORK_RADIUS}" \
                0 \
                0 \
                7 \
                "${output_dir}"
        done
    done
    
    log_success "Scenario 5 completed: ${total_runs} simulations"
}

# ============================================================================
# Summary Generation
# ============================================================================
generate_summary() {
    log_info "Generating simulation summary..."
    
    local summary_file="${SESSION_DIR}/summary/simulation_summary.txt"
    local csv_file="${SESSION_DIR}/summary/results_summary.csv"
    
    # Create summary report
    cat > "${summary_file}" << EOF
LoRaWAN Simulation Session Summary
Generated: $(date)
Session ID: ${TIMESTAMP}

Configuration:
- Simulation Time: ${DEFAULT_SIMULATION_TIME} seconds
- Network Radius: ${DEFAULT_NETWORK_RADIUS} meters
- Default Payload: ${DEFAULT_PAYLOAD_SIZE} bytes
- Random Seed: ${DEFAULT_RANDOM_SEED}

Scenarios Executed:
1. Device Density Variation: 5 densities × 6 algorithms = 30 simulations
2. Spreading Factor Variation: 5 SFs × 6 algorithms = 30 simulations
3. Interval Variation: 5 intervals × 6 algorithms = 30 simulations
4. Mobility Variation: 5 mobility levels × 6 algorithms = 30 simulations
5. Network Density Variation: 5 densities × 6 algorithms = 30 simulations

Total Simulations: 150
Results Location: ${SESSION_DIR}

Algorithms Tested:
- Random Allocation
- Round-Robin
- ADR (Adaptive Data Rate)
- D-LoRa (Distributed LoRa)
- RS-LoRa (Resource Scheduling LoRa)
- NoReL (No-Regret Learning)

EOF

    # Create CSV header for analysis script
    echo "Scenario,Algorithm,Devices,PDR,EnergyEfficiency,Throughput,AvgToA,AvgRSSI,AvgSNR,TotalPacketsSent,TotalPacketsReceived" > "${csv_file}"
    
    # Extract key metrics from all result files
    find "${SESSION_DIR}" -name "*.txt" -not -path "*/summary/*" | while read -r file; do
        if [ -f "${file}" ] && [ -s "${file}" ]; then
            # Extract scenario and algorithm from filename
            local basename=$(basename "${file}" .txt)
            local scenario=$(echo "${basename}" | cut -d'_' -f1-2)
            local algorithm=$(echo "${basename}" | cut -d'_' -f3)
            local devices=$(echo "${basename}" | cut -d'_' -f4 | sed 's/dev//')
            
            # Extract metrics (assuming specific format from simulator)
            local pdr=$(grep "^PDR," "${file}" | cut -d',' -f2 || echo "0")
            local energy=$(grep "^EnergyEfficiency," "${file}" | cut -d',' -f2 || echo "0")
            local throughput=$(grep "^Throughput," "${file}" | cut -d',' -f2 || echo "0")
            local toa=$(grep "^AvgToA," "${file}" | cut -d',' -f2 || echo "0")
            local rssi=$(grep "^AvgRSSI," "${file}" | cut -d',' -f2 || echo "0")
            local snr=$(grep "^AvgSNR," "${file}" | cut -d',' -f2 || echo "0")
            local sent=$(grep "^TotalPacketsSent," "${file}" | cut -d',' -f2 || echo "0")
            local received=$(grep "^TotalPacketsReceived," "${file}" | cut -d',' -f2 || echo "0")
            
            echo "${scenario},${algorithm},${devices},${pdr},${energy},${throughput},${toa},${rssi},${snr},${sent},${received}" >> "${csv_file}"
        fi
    done
    
    log_success "Summary generated: ${summary_file}"
    log_success "CSV data for analysis: ${csv_file}"
}

# ============================================================================
# Main Execution
# ============================================================================

print_banner() {
    cat << 'EOF'
 _      ____  _____       __        ___    _   _   _____  _           
| |    / __ \|  __ \      \ \      / / \  | \ | | |  ___|| |          
| |   | |  | | |__) |__    \ \    / / _ \ |  \| | | |__  | |          
| |   | |  | |  _  /   /    \ \  / / ___ \| . ` | |___ \ | |          
| |___| |__| | | \ \  |_     \ \/ /_/   \_\_|\_|  ___| | |_____       
|______\____/|_|  \_\  |_|    \_____|    |_____|  |____/ |_____|      
                                                                      
    Simulation Scenarios Automation Script                           
    NS-3.42 LoRaWAN Implementation                                   
                                                                      
EOF
}

show_help() {
    cat << EOF
Usage: $0 [OPTIONS] [SCENARIOS]

SCENARIOS:
  all                 Run all 5 scenarios (default)
  1, density          Device density variation
  2, sf               Spreading factor variation
  3, interval         Transmission interval variation
  4, mobility         Mobility variation
  5, network          Network density variation

OPTIONS:
  -h, --help          Show this help message
  -t, --time TIME     Simulation time in seconds (default: ${DEFAULT_SIMULATION_TIME})
  -r, --radius RADIUS Network radius in meters (default: ${DEFAULT_NETWORK_RADIUS})
  -p, --payload SIZE  Payload size in bytes (default: ${DEFAULT_PAYLOAD_SIZE})
  -s, --seed SEED     Random seed (default: ${DEFAULT_RANDOM_SEED})
  --ns3-build DIR     NS-3 build directory (default: ${NS3_BUILD_DIR})
  --results-dir DIR   Results directory (default: ${RESULTS_DIR})

EXAMPLES:
  $0                  # Run all scenarios with default parameters
  $0 1 2              # Run only scenarios 1 and 2
  $0 density sf       # Same as above, using names
  $0 --time 7200 all  # Run all scenarios for 2 hours each

EOF
}

main() {
    local scenarios_to_run=()
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--time)
                DEFAULT_SIMULATION_TIME="$2"
                shift 2
                ;;
            -r|--radius)
                DEFAULT_NETWORK_RADIUS="$2"
                shift 2
                ;;
            -p|--payload)
                DEFAULT_PAYLOAD_SIZE="$2"
                shift 2
                ;;
            -s|--seed)
                DEFAULT_RANDOM_SEED="$2"
                shift 2
                ;;
            --ns3-build)
                NS3_BUILD_DIR="$2"
                SIMULATOR="${NS3_BUILD_DIR}/src/lorawan/examples/lorawan-simulation"
                shift 2
                ;;
            --results-dir)
                RESULTS_DIR="$2"
                SESSION_DIR="${RESULTS_DIR}/session_${TIMESTAMP}"
                shift 2
                ;;
            all)
                scenarios_to_run=(1 2 3 4 5)
                shift
                ;;
            1|density)
                scenarios_to_run+=(1)
                shift
                ;;
            2|sf)
                scenarios_to_run+=(2)
                shift
                ;;
            3|interval)
                scenarios_to_run+=(3)
                shift
                ;;
            4|mobility)
                scenarios_to_run+=(4)
                shift
                ;;
            5|network)
                scenarios_to_run+=(5)
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Default to all scenarios if none specified
    if [ ${#scenarios_to_run[@]} -eq 0 ]; then
        scenarios_to_run=(1 2 3 4 5)
    fi
    
    # Print banner and start
    print_banner
    log_info "Starting LoRaWAN simulation scenarios"
    log_info "Session timestamp: ${TIMESTAMP}"
    
    # Setup and validation
    check_simulator
    setup_directories
    
    # Record start time
    local start_time=$(date +%s)
    
    # Run selected scenarios
    for scenario in "${scenarios_to_run[@]}"; do
        case $scenario in
            1) scenario1_device_density ;;
            2) scenario2_sf_variation ;;
            3) scenario3_interval_variation ;;
            4) scenario4_mobility_variation ;;
            5) scenario5_network_density ;;
        esac
    done
    
    # Generate summary
    generate_summary
    
    # Calculate total execution time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))
    local seconds=$((duration % 60))
    
    log_success "All scenarios completed successfully!"
    log_info "Total execution time: ${hours}h ${minutes}m ${seconds}s"
    log_info "Results available in: ${SESSION_DIR}"
    log_info "Run the analysis script: python scripts/analysis/analyze-results.py ${SESSION_DIR}"
}

# Execute main function with all arguments
main "$@"