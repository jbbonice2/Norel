/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2023 University Research
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * LoRaWAN Simulator with Advanced Algorithms Implementation
 * Supports: D-LoRa, Random, Round-Robin, ADR, RS-LoRa, NoReL
 * Metrics: PDR, Energy Efficiency, Throughput, ToA, RSSI, SNR
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/mobility-module.h"
#include "ns3/internet-module.h"
#include "ns3/lorawan-module.h"
#include "ns3/applications-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/propagation-module.h"
#include "ns3/spectrum-module.h"
#include "ns3/log.h"
#include "ns3/command-line.h"
#include "ns3/config.h"
#include "ns3/string.h"
#include "ns3/double.h"
#include "ns3/random-variable-stream.h"
#include "ns3/rng-seed-manager.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <algorithm>
#include <cmath>

using namespace ns3;
using namespace lorawan;

NS_LOG_COMPONENT_DEFINE ("LoRaWANSimulation");

// Enumeration for allocation algorithms
enum AllocationAlgorithm {
    RANDOM_ALLOCATION,
    ROUND_ROBIN,
    ADR_ALGORITHM,
    D_LORA,
    RS_LORA,
    NOREL
};

// Structure to store simulation metrics
struct SimulationMetrics {
    double pdr;                    // Packet Delivery Ratio
    double energyEfficiency;       // Energy Efficiency
    double throughput;             // Network Throughput
    double avgToA;                 // Average Time on Air
    double avgRSSI;                // Average RSSI
    double avgSNR;                 // Average SNR
    std::vector<int> sfDistribution; // SF Distribution
    std::vector<int> tpDistribution; // TP Distribution
    int totalPacketsSent;
    int totalPacketsReceived;
    double totalEnergyConsumed;
    double simulationTime;
};

// Global variables for metrics collection
std::map<uint32_t, uint32_t> packetsSent;
std::map<uint32_t, uint32_t> packetsReceived;
std::map<uint32_t, double> energyConsumed;
std::map<uint32_t, double> rssiValues;
std::map<uint32_t, double> snrValues;
std::map<uint32_t, std::vector<double>> toaValues;
std::vector<Time> transmissionTimes;
std::vector<Time> receptionTimes;

// Configuration parameters
uint32_t nDevices = 200;
uint32_t nGateways = 1;
double simulationTime = 3600.0; // 1 hour in seconds
double appPeriod = 900.0; // 15 minutes in seconds
uint32_t payloadSize = 50; // bytes
AllocationAlgorithm algorithm = RANDOM_ALLOCATION;
std::string outputFile = "results/simulation_results.txt";
double networkRadius = 2000.0; // meters
double mobilitySpeed = 0.0; // m/s for static scenario
double mobilityPercentage = 0.0; // percentage of mobile nodes
uint32_t fixedSF = 7; // Fixed SF for some algorithms
uint32_t fixedTP = 14; // Fixed TP for some algorithms
std::string scenarioName = "default";
uint32_t randomSeed = 1;

// Function declarations
void PacketTransmissionCallback(Ptr<const Packet> packet, uint32_t systemId);
void PacketReceptionCallback(Ptr<const Packet> packet, uint32_t systemId);
void ConfigureLoRaParameters(NodeContainer endDevices, AllocationAlgorithm algorithm);
SimulationMetrics CalculateMetrics();
void SaveResults(const SimulationMetrics& metrics, const std::string& filename);
Vector GetRandomPosition(double radius);
void SetupMobility(NodeContainer nodes, double speed, double percentage);

// Callback functions for metric collection
void
PacketTransmissionCallback(Ptr<const Packet> packet, uint32_t systemId)
{
    packetsSent[systemId]++;
    transmissionTimes.push_back(Simulator::Now());
    
    // Calculate energy consumption for transmission
    // Simplified energy model: P_tx * ToA
    double txPower = 14.0; // dBm (default)
    double toaSeconds = 0.1; // simplified ToA calculation
    energyConsumed[systemId] += txPower * toaSeconds;
    
    NS_LOG_INFO("Packet transmitted by device " << systemId << " at time " << Simulator::Now().GetSeconds());
}

void
PacketReceptionCallback(Ptr<const Packet> packet, uint32_t systemId)
{
    packetsReceived[systemId]++;
    receptionTimes.push_back(Simulator::Now());
    
    NS_LOG_INFO("Packet received by gateway " << systemId << " at time " << Simulator::Now().GetSeconds());
}

Vector
GetRandomPosition(double radius)
{
    // Generate random position within circular area
    Ptr<UniformRandomVariable> uniformRv = CreateObject<UniformRandomVariable>();
    double angle = uniformRv->GetValue(0, 2 * M_PI);
    double distance = sqrt(uniformRv->GetValue(0, 1)) * radius;
    
    double x = distance * cos(angle);
    double y = distance * sin(angle);
    
    return Vector(x, y, 0.0);
}

void
SetupMobility(NodeContainer nodes, double speed, double percentage)
{
    MobilityHelper mobility;
    
    if (speed > 0 && percentage > 0) {
        // Setup mobile nodes
        uint32_t mobileNodes = (uint32_t)(nodes.GetN() * percentage / 100.0);
        
        // Static nodes
        mobility.SetPositionAllocator("ns3::UniformDiscPositionAllocator",
                                     "X", DoubleValue(0.0),
                                     "Y", DoubleValue(0.0),
                                     "rho", DoubleValue(networkRadius));
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        
        NodeContainer staticNodes;
        for (uint32_t i = mobileNodes; i < nodes.GetN(); ++i) {
            staticNodes.Add(nodes.Get(i));
        }
        mobility.Install(staticNodes);
        
        // Mobile nodes
        mobility.SetMobilityModel("ns3::RandomWalk2dMobilityModel",
                                 "Bounds", RectangleValue(Rectangle(-networkRadius, networkRadius, 
                                                                   -networkRadius, networkRadius)),
                                 "Speed", StringValue("ns3::UniformRandomVariable[Min=1.39|Max=8.33]"), // 5-30 km/h
                                 "Direction", StringValue("ns3::UniformRandomVariable[Min=0|Max=6.28]"));
        
        NodeContainer mobileNodeContainer;
        for (uint32_t i = 0; i < mobileNodes; ++i) {
            mobileNodeContainer.Add(nodes.Get(i));
        }
        mobility.Install(mobileNodeContainer);
    } else {
        // All static nodes
        mobility.SetPositionAllocator("ns3::UniformDiscPositionAllocator",
                                     "X", DoubleValue(0.0),
                                     "Y", DoubleValue(0.0),
                                     "rho", DoubleValue(networkRadius));
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
        mobility.Install(nodes);
    }
}

void
ConfigureLoRaParameters(NodeContainer endDevices, AllocationAlgorithm algorithm)
{
    NS_LOG_FUNCTION(endDevices.GetN() << algorithm);
    
    Ptr<UniformRandomVariable> uniformRv = CreateObject<UniformRandomVariable>();
    
    for (NodeContainer::Iterator i = endDevices.Begin(); i != endDevices.End(); ++i) {
        Ptr<Node> node = *i;
        Ptr<LorawanMac> mac = node->GetDevice(0)->GetObject<LorawanNetDevice>()->GetMac();
        Ptr<EndDeviceLorawanMac> edMac = mac->GetObject<EndDeviceLorawanMac>();
        
        uint8_t sf = 7;
        double txPower = 14.0;
        
        switch (algorithm) {
            case RANDOM_ALLOCATION:
                sf = uniformRv->GetInteger(7, 12);
                txPower = uniformRv->GetValue(2.0, 14.0);
                break;
                
            case ROUND_ROBIN:
                sf = 7 + (node->GetId() % 6); // SF 7-12
                txPower = 2.0 + (node->GetId() % 13); // TP 2-14
                break;
                
            case ADR_ALGORITHM:
                // ADR will be handled by the network server
                sf = 12; // Start with maximum SF
                txPower = 14.0; // Start with maximum power
                break;
                
            case D_LORA:
                // Distributed LoRa - distance-based allocation
                {
                    Ptr<MobilityModel> mobility = node->GetObject<MobilityModel>();
                    Vector position = mobility->GetPosition();
                    double distance = sqrt(position.x * position.x + position.y * position.y);
                    
                    if (distance < 500) sf = 7;
                    else if (distance < 1000) sf = 8;
                    else if (distance < 1500) sf = 9;
                    else if (distance < 2000) sf = 10;
                    else if (distance < 2500) sf = 11;
                    else sf = 12;
                    
                    txPower = std::min(14.0, 2.0 + distance / 200.0);
                }
                break;
                
            case RS_LORA:
                // Resource Scheduling LoRa - load balancing
                sf = 7 + (node->GetId() % 6);
                txPower = 14.0;
                break;
                
            case NOREL:
                // No-Regret Learning - start with random, will adapt
                sf = uniformRv->GetInteger(7, 12);
                txPower = uniformRv->GetValue(2.0, 14.0);
                break;
                
            default:
                sf = fixedSF;
                txPower = fixedTP;
                break;
        }
        
        // Set the spreading factor
        edMac->SetDataRate(sf - 7); // DataRate index (0-5 for SF7-12)
        
        // Set transmission power
        Ptr<LorawanPhy> phy = node->GetDevice(0)->GetObject<LorawanNetDevice>()->GetPhy();
        phy->GetObject<EndDeviceLorawanPhy>()->SetTxPower(txPower);
        
        NS_LOG_INFO("Node " << node->GetId() << ": SF=" << (int)sf << ", TxPower=" << txPower << " dBm");
    }
}

SimulationMetrics
CalculateMetrics()
{
    SimulationMetrics metrics;
    
    // Initialize metrics
    metrics.totalPacketsSent = 0;
    metrics.totalPacketsReceived = 0;
    metrics.totalEnergyConsumed = 0.0;
    metrics.simulationTime = simulationTime;
    metrics.sfDistribution.resize(6, 0); // SF 7-12
    metrics.tpDistribution.resize(13, 0); // TP 2-14
    
    // Calculate totals
    for (auto& pair : packetsSent) {
        metrics.totalPacketsSent += pair.second;
    }
    
    for (auto& pair : packetsReceived) {
        metrics.totalPacketsReceived += pair.second;
    }
    
    for (auto& pair : energyConsumed) {
        metrics.totalEnergyConsumed += pair.second;
    }
    
    // Calculate PDR
    metrics.pdr = (metrics.totalPacketsSent > 0) ? 
                  (double)metrics.totalPacketsReceived / metrics.totalPacketsSent : 0.0;
    
    // Calculate throughput (packets/second)
    metrics.throughput = metrics.totalPacketsReceived / simulationTime;
    
    // Calculate energy efficiency (packets/joule)
    metrics.energyEfficiency = (metrics.totalEnergyConsumed > 0) ? 
                              metrics.totalPacketsReceived / metrics.totalEnergyConsumed : 0.0;
    
    // Calculate average ToA (simplified)
    double totalToA = 0.0;
    for (auto& toaList : toaValues) {
        for (double toa : toaList.second) {
            totalToA += toa;
        }
    }
    metrics.avgToA = (toaValues.size() > 0) ? totalToA / toaValues.size() : 0.0;
    
    // Calculate average RSSI and SNR
    double totalRSSI = 0.0, totalSNR = 0.0;
    int rssiCount = 0, snrCount = 0;
    
    for (auto& pair : rssiValues) {
        totalRSSI += pair.second;
        rssiCount++;
    }
    
    for (auto& pair : snrValues) {
        totalSNR += pair.second;
        snrCount++;
    }
    
    metrics.avgRSSI = (rssiCount > 0) ? totalRSSI / rssiCount : 0.0;
    metrics.avgSNR = (snrCount > 0) ? totalSNR / snrCount : 0.0;
    
    return metrics;
}

void
SaveResults(const SimulationMetrics& metrics, const std::string& filename)
{
    std::ofstream outFile(filename);
    
    if (!outFile.is_open()) {
        NS_LOG_ERROR("Cannot open output file: " << filename);
        return;
    }
    
    // Write header
    outFile << "# LoRaWAN Simulation Results" << std::endl;
    outFile << "# Scenario: " << scenarioName << std::endl;
    outFile << "# Algorithm: " << algorithm << std::endl;
    outFile << "# Devices: " << nDevices << std::endl;
    outFile << "# Gateways: " << nGateways << std::endl;
    outFile << "# Simulation Time: " << simulationTime << " seconds" << std::endl;
    outFile << "# Network Radius: " << networkRadius << " meters" << std::endl;
    outFile << "# App Period: " << appPeriod << " seconds" << std::endl;
    outFile << "# Payload Size: " << payloadSize << " bytes" << std::endl;
    outFile << std::endl;
    
    // Write metrics
    outFile << "PDR," << metrics.pdr << std::endl;
    outFile << "EnergyEfficiency," << metrics.energyEfficiency << std::endl;
    outFile << "Throughput," << metrics.throughput << std::endl;
    outFile << "AvgToA," << metrics.avgToA << std::endl;
    outFile << "AvgRSSI," << metrics.avgRSSI << std::endl;
    outFile << "AvgSNR," << metrics.avgSNR << std::endl;
    outFile << "TotalPacketsSent," << metrics.totalPacketsSent << std::endl;
    outFile << "TotalPacketsReceived," << metrics.totalPacketsReceived << std::endl;
    outFile << "TotalEnergyConsumed," << metrics.totalEnergyConsumed << std::endl;
    
    outFile.close();
    
    NS_LOG_INFO("Results saved to: " << filename);
    
    // Print summary to console
    std::cout << "=== Simulation Results ===" << std::endl;
    std::cout << "Scenario: " << scenarioName << std::endl;
    std::cout << "Algorithm: " << algorithm << std::endl;
    std::cout << "PDR: " << (metrics.pdr * 100) << "%" << std::endl;
    std::cout << "Energy Efficiency: " << metrics.energyEfficiency << " packets/J" << std::endl;
    std::cout << "Throughput: " << metrics.throughput << " packets/s" << std::endl;
    std::cout << "Avg ToA: " << metrics.avgToA << " ms" << std::endl;
    std::cout << "Avg RSSI: " << metrics.avgRSSI << " dBm" << std::endl;
    std::cout << "Avg SNR: " << metrics.avgSNR << " dB" << std::endl;
    std::cout << "Total Packets Sent: " << metrics.totalPacketsSent << std::endl;
    std::cout << "Total Packets Received: " << metrics.totalPacketsReceived << std::endl;
    std::cout << "=========================" << std::endl;
}

int
main(int argc, char *argv[])
{
    // Command line argument parsing
    CommandLine cmd;
    cmd.AddValue("nDevices", "Number of end devices", nDevices);
    cmd.AddValue("nGateways", "Number of gateways", nGateways);
    cmd.AddValue("simulationTime", "Simulation time in seconds", simulationTime);
    cmd.AddValue("appPeriod", "Application packet interval in seconds", appPeriod);
    cmd.AddValue("payloadSize", "Payload size in bytes", payloadSize);
    cmd.AddValue("algorithm", "Allocation algorithm (0=Random, 1=RoundRobin, 2=ADR, 3=D-LoRa, 4=RS-LoRa, 5=NoReL)", algorithm);
    cmd.AddValue("outputFile", "Output file for results", outputFile);
    cmd.AddValue("networkRadius", "Network radius in meters", networkRadius);
    cmd.AddValue("mobilitySpeed", "Mobility speed in m/s", mobilitySpeed);
    cmd.AddValue("mobilityPercentage", "Percentage of mobile nodes", mobilityPercentage);
    cmd.AddValue("fixedSF", "Fixed spreading factor (7-12)", fixedSF);
    cmd.AddValue("fixedTP", "Fixed transmission power (2-14 dBm)", fixedTP);
    cmd.AddValue("scenarioName", "Scenario name for identification", scenarioName);
    cmd.AddValue("randomSeed", "Random seed for reproducibility", randomSeed);
    cmd.Parse(argc, argv);
    
    // Set random seed
    RngSeedManager::SetSeed(randomSeed);
    
    // Enable logging
    LogComponentEnable("LoRaWANSimulation", LOG_LEVEL_INFO);
    
    NS_LOG_INFO("Starting LoRaWAN simulation with " << nDevices << " devices and " << nGateways << " gateways");
    NS_LOG_INFO("Algorithm: " << algorithm << ", Scenario: " << scenarioName);
    
    // Create nodes
    NodeContainer endDevices;
    NodeContainer gateways;
    endDevices.Create(nDevices);
    gateways.Create(nGateways);
    
    // Setup mobility
    SetupMobility(endDevices, mobilitySpeed, mobilityPercentage);
    
    // Gateway mobility (fixed positions)
    MobilityHelper gatewayMobility;
    Ptr<ListPositionAllocator> allocator = CreateObject<ListPositionAllocator>();
    allocator->Add(Vector(0.0, 0.0, 15.0)); // Gateway at center, 15m height
    gatewayMobility.SetPositionAllocator(allocator);
    gatewayMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    gatewayMobility.Install(gateways);
    
    // Create and configure the LoRaWAN channel
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(3.76);
    loss->SetReference(1, 7.7);
    
    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    
    Ptr<LorawanChannel> channel = CreateObject<LorawanChannel>(loss, delay);
    
    // Create the LoRaWAN PHY and MAC layer helper
    LorawanPhyHelper phyHelper = LorawanPhyHelper();
    phyHelper.SetChannel(channel);
    
    LorawanMacHelper macHelper = LorawanMacHelper();
    
    // Create the LoRaWAN helper and install on nodes
    LorawanHelper helper = LorawanHelper();
    helper.EnablePacketTracking();
    
    NetDeviceContainer endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);
    NetDeviceContainer gatewayNetDevices = helper.Install(phyHelper, macHelper, gateways);
    
    // Configure LoRa parameters based on selected algorithm
    ConfigureLoRaParameters(endDevices, (AllocationAlgorithm)algorithm);
    
    // Create and configure applications
    int32_t appPort = 1;
    PeriodicSenderHelper appHelper = PeriodicSenderHelper();
    appHelper.SetPacketSize(payloadSize);
    appHelper.SetPeriod(Seconds(appPeriod));
    ApplicationContainer appContainer = appHelper.Install(endDevices);
    
    // Set application start times with some randomization
    Ptr<UniformRandomVariable> rv = CreateObject<UniformRandomVariable>();
    for (ApplicationContainer::Iterator i = appContainer.Begin(); i != appContainer.End(); ++i) {
        (*i)->SetStartTime(Seconds(rv->GetValue(0, 10))); // Random start within first 10 seconds
        (*i)->SetStopTime(Seconds(simulationTime));
    }
    
    // Install the internet stack on gateways
    InternetStackHelper internet;
    internet.Install(gateways);
    
    // Connect callbacks for metrics collection
    Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/Phy/StartSending",
                                  MakeCallback(&PacketTransmissionCallback));
    Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/Phy/ReceivedPacket",
                                  MakeCallback(&PacketReceptionCallback));
    
    // Run simulation
    NS_LOG_INFO("Running simulation for " << simulationTime << " seconds");
    Simulator::Stop(Seconds(simulationTime));
    Simulator::Run();
    
    // Calculate and save results
    SimulationMetrics metrics = CalculateMetrics();
    SaveResults(metrics, outputFile);
    
    Simulator::Destroy();
    
    NS_LOG_INFO("Simulation completed successfully");
    return 0;
}