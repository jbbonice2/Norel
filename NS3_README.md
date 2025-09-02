# LoRaWAN Simulator with NS-3.42

## Overview

This project provides a comprehensive LoRaWAN simulation environment built on NS-3.42, implementing advanced allocation algorithms and experimental scenarios for research purposes. The simulator includes sophisticated algorithms, automated scenario execution, and advanced analysis tools.

## 🚀 Features

### Advanced LoRaWAN Algorithms
- **D-LoRa**: Distributed LoRa with distance-based allocation
- **Random**: Random SF and TP allocation
- **Round-Robin**: Systematic SF and TP distribution
- **ADR**: Adaptive Data Rate (LoRaWAN standard)
- **RS-LoRa**: Resource Scheduling LoRa
- **NoReL**: No-Regret Learning algorithm

### Comprehensive Metrics
- **PDR**: Packet Delivery Ratio
- **Energy Efficiency**: Packets per Joule
- **Throughput**: Packets per second
- **ToA**: Time on Air
- **RSSI**: Received Signal Strength Indicator
- **SNR**: Signal-to-Noise Ratio

### Automated Scenarios
1. **Device Density Variation**: 50-1000 devices on 4 km²
2. **Spreading Factor Variation**: SF7-SF12 impact analysis
3. **Transmission Interval Variation**: 5-60 minute intervals
4. **Mobility Variation**: 0-100% mobile nodes with realistic speeds
5. **Network Density Variation**: Scalability testing (12.5-100 nodes/km²)

### Advanced Analysis Tools
- Scientific visualizations with matplotlib/seaborn
- Performance matrices and comparative analysis
- Energy correlation analysis
- Automated report generation
- Export to multiple formats (PNG, PDF, SVG)

## 📋 Requirements

### System Requirements
- **NS-3.42** or later with LoRaWAN module
- **Python 3.8+** for analysis scripts
- **GCC 9+** for compilation
- **Linux/macOS** (recommended)

### Python Dependencies
```bash
pip install numpy pandas matplotlib seaborn pathlib
```

### NS-3 Dependencies
- LoRaWAN module for NS-3
- Standard NS-3 modules (core, network, mobility, internet, applications)

## 🛠️ Installation

### 1. Install NS-3.42 with LoRaWAN Module

```bash
# Download NS-3.42
wget https://www.nsnam.org/releases/ns-allinone-3.42.tar.bz2
tar -xf ns-allinone-3.42.tar.bz2
cd ns-allinone-3.42/ns-3.42

# Configure and build
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

### 2. Clone This Repository

```bash
git clone https://github.com/jbbonice2/Norel.git
cd Norel
```

### 3. Build the LoRaWAN Simulator

```bash
# Copy the simulator to NS-3 examples directory
cp src/lorawan-simulation.cc /path/to/ns-3.42/src/lorawan/examples/

# Build the simulator
cd /path/to/ns-3.42
./ns3 build
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
# Additional dependencies for analysis
pip install matplotlib seaborn pandas numpy
```

## 🚀 Quick Start

### Basic Simulation

```bash
# Run a simple simulation with 200 devices
./build/src/lorawan/examples/lorawan-simulation \
    --nDevices=200 \
    --algorithm=5 \
    --simulationTime=3600 \
    --scenarioName="test_run"
```

### Automated Scenario Execution

```bash
# Run all 5 scenarios with default parameters
./scripts/run-scenarios.sh

# Run specific scenarios
./scripts/run-scenarios.sh 1 2  # Device density and SF variation

# Custom parameters
./scripts/run-scenarios.sh --time 7200 --radius 3000 all
```

### Results Analysis

```bash
# Analyze all results
python scripts/analysis/analyze-results.py results/session_TIMESTAMP/

# Analyze specific scenario
python scripts/analysis/analyze-results.py results/session_TIMESTAMP/ --scenario 1

# Custom output format
python scripts/analysis/analyze-results.py results/session_TIMESTAMP/ --format pdf
```

## 📊 Simulation Parameters

### Core Parameters
| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `nDevices` | Number of end devices | 200 | 1-10000 |
| `nGateways` | Number of gateways | 1 | 1-10 |
| `simulationTime` | Simulation duration (seconds) | 3600 | 60-86400 |
| `appPeriod` | Packet interval (seconds) | 900 | 60-7200 |
| `payloadSize` | Payload size (bytes) | 50 | 1-255 |
| `networkRadius` | Network radius (meters) | 2000 | 100-10000 |

### Algorithm Selection
| Value | Algorithm | Description |
|-------|-----------|-------------|
| 0 | Random | Random SF and TP allocation |
| 1 | Round-Robin | Systematic distribution |
| 2 | ADR | Adaptive Data Rate |
| 3 | D-LoRa | Distance-based allocation |
| 4 | RS-LoRa | Resource scheduling |
| 5 | NoReL | No-regret learning |

### Mobility Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `mobilitySpeed` | Speed in m/s | 0 (static) |
| `mobilityPercentage` | % of mobile nodes | 0 |

## 📈 Experimental Scenarios

### Scenario 1: Device Density Variation
- **Purpose**: Analyze scalability with increasing device density
- **Variables**: 50, 200, 400, 700, 1000 devices
- **Fixed**: 15-minute intervals, 50-byte payload, 4 km² area
- **Metrics**: PDR degradation, interference impact, energy efficiency

### Scenario 2: Spreading Factor Variation
- **Purpose**: Study SF impact on network performance
- **Variables**: SF7, SF8, SF9, SF10, SF12
- **Fixed**: 200 nodes, standard intervals
- **Metrics**: ToA variation, capacity utilization, collision rates

### Scenario 3: Transmission Interval Variation
- **Purpose**: Evaluate traffic load impact
- **Variables**: 5, 10, 15, 30, 60 minute intervals
- **Fixed**: 200 devices, mixed SFs
- **Metrics**: Network congestion, duty cycle utilization

### Scenario 4: Mobility Variation
- **Purpose**: Assess mobility impact on performance
- **Variables**: 0%, 25%, 50%, 75%, 100% mobile nodes
- **Fixed**: 150 nodes, 5-30 km/h speeds, random trajectories
- **Metrics**: Handover effects, RSSI variations

### Scenario 5: Network Density Variation
- **Purpose**: Scalability analysis
- **Variables**: 50, 100, 200, 300, 400 nodes (12.5-100 nodes/km²)
- **Fixed**: Standard parameters
- **Metrics**: Interference scaling, resource allocation efficiency

## 📊 Output and Analysis

### Result Files Structure
```
results/
└── session_TIMESTAMP/
    ├── scenario1_device_density/
    │   ├── scenario1_density_random_dev50.txt
    │   ├── scenario1_density_adr_dev200.txt
    │   └── ...
    ├── scenario2_sf_variation/
    ├── scenario3_interval_variation/
    ├── scenario4_mobility_variation/
    ├── scenario5_network_density/
    ├── summary/
    │   ├── simulation_summary.txt
    │   └── results_summary.csv
    └── figures/
        ├── overview_report.png
        ├── scenario1_device_density.png
        ├── performance_matrix.png
        ├── energy_analysis.png
        └── comprehensive_report.md
```

### Key Visualizations
- **Overview Report**: Multi-metric algorithm comparison
- **Scenario Analysis**: Detailed performance under varying conditions
- **Performance Matrix**: Algorithm ranking across all metrics
- **Energy Analysis**: Energy-performance trade-offs
- **Correlation Matrices**: Metric interdependencies

## 🔧 Advanced Usage

### Custom Algorithm Implementation

To add a new allocation algorithm:

1. **Add to enum** in `lorawan-simulation.cc`:
```cpp
enum AllocationAlgorithm {
    // ... existing algorithms
    MY_CUSTOM_ALGORITHM
};
```

2. **Implement logic** in `ConfigureLoRaParameters()`:
```cpp
case MY_CUSTOM_ALGORITHM:
    // Your allocation logic here
    sf = calculateCustomSF(node);
    txPower = calculateCustomTP(node);
    break;
```

3. **Update scripts** to include the new algorithm in analysis.

### Custom Metrics Collection

Add custom metrics by:

1. **Declare variables** in global scope
2. **Update callbacks** to collect new data
3. **Modify `CalculateMetrics()`** to compute new metrics
4. **Update analysis scripts** to visualize new metrics

### Batch Execution

For large-scale experiments:

```bash
# Multiple runs with different seeds
for seed in {1..10}; do
    ./scripts/run-scenarios.sh --seed $seed --time 3600
done

# Parameter sweeps
for radius in 1000 2000 3000; do
    ./scripts/run-scenarios.sh --radius $radius
done
```

## 📚 Scientific Applications

### Research Areas
- **LoRaWAN Performance Optimization**
- **IoT Network Scalability**
- **Energy-Efficient Communication**
- **Adaptive Resource Allocation**
- **Machine Learning in Wireless Networks**

### Validated Use Cases
- Dense urban IoT deployments
- Agricultural sensor networks
- Smart city applications
- Industrial IoT monitoring
- Environmental sensing networks

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-algorithm`)
3. Implement changes with tests
4. Update documentation
5. Submit pull request

### Code Style
- Follow NS-3 coding conventions
- Use descriptive variable names
- Add comprehensive comments
- Include validation tests

## 📖 Publications and Citations

If you use this simulator in your research, please cite:

```bibtex
@ARTICLE{Toro2022Learning,
  author={Toro-Betancur, Veronica and Premsankar, Gopika and Liu, Chen-Feng and Slabicki, Mariusz and Bennis, Mehdi and Francesco, Mario Di},
  journal={IEEE Transactions on Industrial Informatics}, 
  title={Learning How to Configure LoRa Networks with No Regret: a Distributed Approach}, 
  year={2022},
  doi={10.1109/TII.2022.3187721}
}
```

## 🐛 Troubleshooting

### Common Issues

**NS-3 Build Errors**
- Ensure NS-3.42+ with LoRaWAN module
- Check GCC version compatibility
- Verify all dependencies installed

**Simulation Crashes**
- Check memory limits for large simulations
- Validate parameter ranges
- Review log files for specific errors

**Analysis Script Errors**
- Install required Python packages
- Check file permissions
- Verify results directory structure

**Performance Issues**
- Reduce simulation time for testing
- Use fewer devices for initial runs
- Enable only necessary logging

### Getting Help

1. **Check Documentation**: Review this README and code comments
2. **Search Issues**: Look for similar problems in GitHub issues
3. **Create Issue**: Provide detailed error information and system specs
4. **Discussion Forum**: Join community discussions for broader questions

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NS-3 Community**: For the excellent simulation framework
- **LoRaWAN Module Authors**: For the comprehensive LoRaWAN implementation
- **Original NoReL Authors**: For the foundational research
- **Contributors**: All researchers and developers who contributed to this project

## 📞 Contact

For questions, suggestions, or collaborations:

- **GitHub Issues**: [Create an issue](https://github.com/jbbonice2/Norel/issues)
- **Email**: [Contact maintainers](mailto:maintainer@example.com)
- **Research Group**: [University/Institution link]

---

**Happy Simulating! 🚀📡**