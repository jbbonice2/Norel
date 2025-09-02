#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoRaWAN Simulation Results Analysis and Visualization Script

Based on dlor_analysis_script.py with enhanced features for NS-3.42 results:
- Automatic parsing of NS-3 simulation results
- Advanced scientific visualizations with matplotlib/seaborn
- Performance matrices and comparative analysis
- Energy correlation analysis
- Automated report generation
- Support for all 5 experimental scenarios

Author: LoRaWAN Research Team
Compatible with: NS-3.42 LoRaWAN Module
"""

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for scientific plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class LoRaWANAnalyzer:
    """
    Comprehensive analyzer for LoRaWAN simulation results
    """
    
    def __init__(self, results_directory):
        """
        Initialize analyzer with results directory
        
        Args:
            results_directory (str): Path to simulation results directory
        """
        self.results_dir = Path(results_directory)
        self.data = {}
        self.summary_data = None
        self.algorithms = ['random', 'round-robin', 'adr', 'd-lora', 'rs-lora', 'norel']
        self.algorithm_colors = {
            'random': '#FF6B6B',
            'round-robin': '#4ECDC4', 
            'adr': '#45B7D1',
            'd-lora': '#96CEB4',
            'rs-lora': '#FFEAA7',
            'norel': '#DDA0DD'
        }
        
        # Create output directories
        self.figures_dir = self.results_dir / 'figures'
        self.figures_dir.mkdir(exist_ok=True)
        
        print(f"📊 LoRaWAN Analyzer initialized")
        print(f"📁 Results directory: {self.results_dir}")
        print(f"🎨 Figures will be saved to: {self.figures_dir}")
    
    def load_data(self):
        """
        Load and parse all simulation result files
        """
        print("📥 Loading simulation data...")
        
        # Load summary CSV if available
        summary_file = self.results_dir / 'summary' / 'results_summary.csv'
        if summary_file.exists():
            print(f"📋 Loading summary data from {summary_file}")
            self.summary_data = pd.read_csv(summary_file)
        else:
            print("⚠️  No summary CSV found, parsing individual files...")
            self._parse_individual_files()
        
        # Load scenario-specific data
        self._load_scenario_data()
        
        print(f"✅ Data loading complete. Found {len(self.data)} scenarios.")
    
    def _parse_individual_files(self):
        """
        Parse individual result files if summary CSV is not available
        """
        results = []
        
        for txt_file in self.results_dir.rglob('*.txt'):
            if 'summary' in str(txt_file):
                continue
                
            try:
                data = self._parse_result_file(txt_file)
                if data:
                    results.append(data)
            except Exception as e:
                print(f"⚠️  Error parsing {txt_file}: {e}")
        
        if results:
            self.summary_data = pd.DataFrame(results)
    
    def _parse_result_file(self, filepath):
        """
        Parse a single result file
        
        Args:
            filepath (Path): Path to result file
            
        Returns:
            dict: Parsed data or None if parsing fails
        """
        data = {}
        
        # Extract info from filename
        filename = filepath.stem
        parts = filename.split('_')
        
        if len(parts) >= 3:
            data['Scenario'] = '_'.join(parts[:2])
            data['Algorithm'] = parts[2]
            if len(parts) >= 4:
                devices_part = parts[3].replace('dev', '')
                try:
                    data['Devices'] = int(devices_part)
                except ValueError:
                    data['Devices'] = 0
        
        # Parse file content
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if ',' in line and not line.startswith('#'):
                        key, value = line.strip().split(',', 1)
                        try:
                            data[key] = float(value)
                        except ValueError:
                            data[key] = value
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None
        
        return data
    
    def _load_scenario_data(self):
        """
        Load scenario-specific data for detailed analysis
        """
        scenarios = [
            'scenario1_device_density',
            'scenario2_sf_variation', 
            'scenario3_interval_variation',
            'scenario4_mobility_variation',
            'scenario5_network_density'
        ]
        
        for scenario in scenarios:
            scenario_dir = self.results_dir / scenario
            if scenario_dir.exists():
                scenario_data = []
                for txt_file in scenario_dir.glob('*.txt'):
                    data = self._parse_result_file(txt_file)
                    if data:
                        scenario_data.append(data)
                
                if scenario_data:
                    self.data[scenario] = pd.DataFrame(scenario_data)
    
    def generate_overview_report(self):
        """
        Generate comprehensive overview report
        """
        print("📈 Generating overview report...")
        
        if self.summary_data is None or self.summary_data.empty:
            print("⚠️  No data available for overview report")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('LoRaWAN Simulation Results Overview', fontsize=16, fontweight='bold')
        
        # 1. PDR by Algorithm
        self._plot_metric_by_algorithm(axes[0, 0], 'PDR', 'Packet Delivery Ratio (%)', 
                                      lambda x: x * 100, 'Higher is better')
        
        # 2. Energy Efficiency by Algorithm  
        self._plot_metric_by_algorithm(axes[0, 1], 'EnergyEfficiency', 'Energy Efficiency (packets/J)',
                                      lambda x: x, 'Higher is better')
        
        # 3. Throughput by Algorithm
        self._plot_metric_by_algorithm(axes[0, 2], 'Throughput', 'Throughput (packets/s)',
                                      lambda x: x, 'Higher is better')
        
        # 4. Average RSSI by Algorithm
        self._plot_metric_by_algorithm(axes[1, 0], 'AvgRSSI', 'Average RSSI (dBm)',
                                      lambda x: x, 'Higher is better')
        
        # 5. Average SNR by Algorithm
        self._plot_metric_by_algorithm(axes[1, 1], 'AvgSNR', 'Average SNR (dB)',
                                      lambda x: x, 'Higher is better')
        
        # 6. Average ToA by Algorithm
        self._plot_metric_by_algorithm(axes[1, 2], 'AvgToA', 'Average Time on Air (ms)',
                                      lambda x: x * 1000, 'Lower is better')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'overview_report.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Overview report saved to {self.figures_dir / 'overview_report.png'}")
    
    def _plot_metric_by_algorithm(self, ax, metric, ylabel, transform, direction):
        """
        Plot a metric grouped by algorithm
        """
        if metric not in self.summary_data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Group by algorithm and calculate statistics
        grouped = self.summary_data.groupby('Algorithm')[metric].agg(['mean', 'std', 'count']).reset_index()
        grouped = grouped[grouped['count'] > 0]  # Remove empty groups
        
        if grouped.empty:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Transform data
        grouped['mean_transformed'] = grouped['mean'].apply(transform)
        grouped['std_transformed'] = grouped['std'].apply(transform)
        
        # Create bar plot
        bars = ax.bar(grouped['Algorithm'], grouped['mean_transformed'], 
                     yerr=grouped['std_transformed'], capsize=5,
                     color=[self.algorithm_colors.get(alg, '#666666') for alg in grouped['Algorithm']])
        
        ax.set_title(f'{ylabel}\n({direction})', fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, grouped['mean_transformed']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01 * max(grouped['mean_transformed']),
                   f'{value:.2f}', ha='center', va='bottom', fontsize=10)
    
    def analyze_scenario1_device_density(self):
        """
        Analyze Scenario 1: Device Density Variation
        """
        print("📊 Analyzing Scenario 1: Device Density Variation...")
        
        scenario_key = 'scenario1_device_density'
        if scenario_key not in self.data:
            print(f"⚠️  No data found for {scenario_key}")
            return
        
        data = self.data[scenario_key]
        if data.empty:
            print(f"⚠️  Empty data for {scenario_key}")
            return
        
        # Create figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Scenario 1: Device Density Impact Analysis', fontsize=16, fontweight='bold')
        
        # Plot metrics vs device count
        metrics = [
            ('PDR', 'Packet Delivery Ratio (%)', lambda x: x * 100),
            ('EnergyEfficiency', 'Energy Efficiency (packets/J)', lambda x: x),
            ('Throughput', 'Throughput (packets/s)', lambda x: x),
            ('AvgRSSI', 'Average RSSI (dBm)', lambda x: x),
            ('AvgSNR', 'Average SNR (dB)', lambda x: x),
            ('AvgToA', 'Average ToA (ms)', lambda x: x * 1000)
        ]
        
        for idx, (metric, ylabel, transform) in enumerate(metrics):
            row, col = idx // 3, idx % 3
            self._plot_metric_vs_devices(axes[row, col], data, metric, ylabel, transform)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'scenario1_device_density.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Generate correlation matrix
        self._generate_correlation_matrix(data, 'Scenario 1: Device Density Correlations', 
                                        'scenario1_correlations.png')
        
        print(f"✅ Scenario 1 analysis saved to {self.figures_dir}")
    
    def _plot_metric_vs_devices(self, ax, data, metric, ylabel, transform):
        """
        Plot metric vs number of devices for different algorithms
        """
        if metric not in data.columns or 'Devices' not in data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Plot each algorithm
        for algorithm in self.algorithms:
            alg_data = data[data['Algorithm'] == algorithm]
            if not alg_data.empty and metric in alg_data.columns:
                devices = alg_data['Devices'].values
                values = alg_data[metric].apply(transform).values
                
                ax.plot(devices, values, marker='o', linewidth=2, markersize=6,
                       label=algorithm.replace('-', ' ').title(),
                       color=self.algorithm_colors.get(algorithm, '#666666'))
        
        ax.set_xlabel('Number of Devices')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def analyze_scenario2_sf_variation(self):
        """
        Analyze Scenario 2: Spreading Factor Variation
        """
        print("📊 Analyzing Scenario 2: Spreading Factor Variation...")
        
        scenario_key = 'scenario2_sf_variation'
        if scenario_key not in self.data:
            print(f"⚠️  No data found for {scenario_key}")
            return
        
        data = self.data[scenario_key]
        if data.empty:
            print(f"⚠️  Empty data for {scenario_key}")
            return
        
        # Extract SF from scenario name
        data['SF'] = data['Scenario'].str.extract(r'sf(\d+)').astype(int)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Scenario 2: Spreading Factor Impact Analysis', fontsize=16, fontweight='bold')
        
        # Plot key metrics vs SF
        self._plot_metric_vs_sf(axes[0, 0], data, 'PDR', 'Packet Delivery Ratio (%)', lambda x: x * 100)
        self._plot_metric_vs_sf(axes[0, 1], data, 'EnergyEfficiency', 'Energy Efficiency (packets/J)', lambda x: x)
        self._plot_metric_vs_sf(axes[1, 0], data, 'Throughput', 'Throughput (packets/s)', lambda x: x)
        self._plot_metric_vs_sf(axes[1, 1], data, 'AvgToA', 'Average ToA (ms)', lambda x: x * 1000)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'scenario2_sf_variation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Scenario 2 analysis saved to {self.figures_dir}")
    
    def _plot_metric_vs_sf(self, ax, data, metric, ylabel, transform):
        """
        Plot metric vs spreading factor for different algorithms
        """
        if metric not in data.columns or 'SF' not in data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Plot each algorithm
        for algorithm in self.algorithms:
            alg_data = data[data['Algorithm'] == algorithm]
            if not alg_data.empty:
                sf_values = alg_data['SF'].values
                metric_values = alg_data[metric].apply(transform).values
                
                ax.plot(sf_values, metric_values, marker='o', linewidth=2, markersize=6,
                       label=algorithm.replace('-', ' ').title(),
                       color=self.algorithm_colors.get(algorithm, '#666666'))
        
        ax.set_xlabel('Spreading Factor')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def analyze_scenario3_interval_variation(self):
        """
        Analyze Scenario 3: Transmission Interval Variation
        """
        print("📊 Analyzing Scenario 3: Transmission Interval Variation...")
        
        scenario_key = 'scenario3_interval_variation'
        if scenario_key not in self.data:
            print(f"⚠️  No data found for {scenario_key}")
            return
        
        data = self.data[scenario_key]
        if data.empty:
            print(f"⚠️  Empty data for {scenario_key}")
            return
        
        # Extract interval from scenario name
        interval_map = {'5min': 5, '10min': 10, '15min': 15, '30min': 30, '60min': 60}
        data['Interval'] = data['Scenario'].str.extract(r'interval_(\w+)')[0].map(interval_map)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Scenario 3: Transmission Interval Impact Analysis', fontsize=16, fontweight='bold')
        
        # Plot key metrics vs interval
        self._plot_metric_vs_interval(axes[0, 0], data, 'PDR', 'Packet Delivery Ratio (%)', lambda x: x * 100)
        self._plot_metric_vs_interval(axes[0, 1], data, 'Throughput', 'Throughput (packets/s)', lambda x: x)
        self._plot_metric_vs_interval(axes[1, 0], data, 'EnergyEfficiency', 'Energy Efficiency (packets/J)', lambda x: x)
        self._plot_metric_vs_interval(axes[1, 1], data, 'TotalPacketsSent', 'Total Packets Sent', lambda x: x)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'scenario3_interval_variation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Scenario 3 analysis saved to {self.figures_dir}")
    
    def _plot_metric_vs_interval(self, ax, data, metric, ylabel, transform):
        """
        Plot metric vs transmission interval for different algorithms
        """
        if metric not in data.columns or 'Interval' not in data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Plot each algorithm
        for algorithm in self.algorithms:
            alg_data = data[data['Algorithm'] == algorithm]
            if not alg_data.empty:
                intervals = alg_data['Interval'].values
                values = alg_data[metric].apply(transform).values
                
                ax.plot(intervals, values, marker='o', linewidth=2, markersize=6,
                       label=algorithm.replace('-', ' ').title(),
                       color=self.algorithm_colors.get(algorithm, '#666666'))
        
        ax.set_xlabel('Transmission Interval (minutes)')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def analyze_scenario4_mobility_variation(self):
        """
        Analyze Scenario 4: Mobility Variation
        """
        print("📊 Analyzing Scenario 4: Mobility Variation...")
        
        scenario_key = 'scenario4_mobility_variation'
        if scenario_key not in self.data:
            print(f"⚠️  No data found for {scenario_key}")
            return
        
        data = self.data[scenario_key]
        if data.empty:
            print(f"⚠️  Empty data for {scenario_key}")
            return
        
        # Extract mobility percentage from scenario name
        data['MobilityPct'] = data['Scenario'].str.extract(r'mobility_(\d+)pct').astype(int)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Scenario 4: Mobility Impact Analysis', fontsize=16, fontweight='bold')
        
        # Plot key metrics vs mobility
        self._plot_metric_vs_mobility(axes[0, 0], data, 'PDR', 'Packet Delivery Ratio (%)', lambda x: x * 100)
        self._plot_metric_vs_mobility(axes[0, 1], data, 'EnergyEfficiency', 'Energy Efficiency (packets/J)', lambda x: x)
        self._plot_metric_vs_mobility(axes[1, 0], data, 'AvgRSSI', 'Average RSSI (dBm)', lambda x: x)
        self._plot_metric_vs_mobility(axes[1, 1], data, 'AvgSNR', 'Average SNR (dB)', lambda x: x)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'scenario4_mobility_variation.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Scenario 4 analysis saved to {self.figures_dir}")
    
    def _plot_metric_vs_mobility(self, ax, data, metric, ylabel, transform):
        """
        Plot metric vs mobility percentage for different algorithms
        """
        if metric not in data.columns or 'MobilityPct' not in data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Plot each algorithm
        for algorithm in self.algorithms:
            alg_data = data[data['Algorithm'] == algorithm]
            if not alg_data.empty:
                mobility = alg_data['MobilityPct'].values
                values = alg_data[metric].apply(transform).values
                
                ax.plot(mobility, values, marker='o', linewidth=2, markersize=6,
                       label=algorithm.replace('-', ' ').title(),
                       color=self.algorithm_colors.get(algorithm, '#666666'))
        
        ax.set_xlabel('Mobile Nodes (%)')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def analyze_scenario5_network_density(self):
        """
        Analyze Scenario 5: Network Density Variation
        """
        print("📊 Analyzing Scenario 5: Network Density Variation...")
        
        scenario_key = 'scenario5_network_density'
        if scenario_key not in self.data:
            print(f"⚠️  No data found for {scenario_key}")
            return
        
        data = self.data[scenario_key]
        if data.empty:
            print(f"⚠️  Empty data for {scenario_key}")
            return
        
        # Extract node count and calculate density
        data['Nodes'] = data['Scenario'].str.extract(r'density_(\d+)nodes').astype(int)
        data['Density'] = data['Nodes'] / 12.57  # nodes per km² (π * r² where r=2km)
        
        # Create figure
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Scenario 5: Network Density Scalability Analysis', fontsize=16, fontweight='bold')
        
        # Plot metrics vs density
        metrics = [
            ('PDR', 'Packet Delivery Ratio (%)', lambda x: x * 100),
            ('EnergyEfficiency', 'Energy Efficiency (packets/J)', lambda x: x),
            ('Throughput', 'Throughput (packets/s)', lambda x: x),
            ('AvgRSSI', 'Average RSSI (dBm)', lambda x: x),
            ('AvgSNR', 'Average SNR (dB)', lambda x: x),
            ('TotalPacketsReceived', 'Total Packets Received', lambda x: x)
        ]
        
        for idx, (metric, ylabel, transform) in enumerate(metrics):
            row, col = idx // 3, idx % 3
            self._plot_metric_vs_density(axes[row, col], data, metric, ylabel, transform)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'scenario5_network_density.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Scenario 5 analysis saved to {self.figures_dir}")
    
    def _plot_metric_vs_density(self, ax, data, metric, ylabel, transform):
        """
        Plot metric vs network density for different algorithms
        """
        if metric not in data.columns or 'Density' not in data.columns:
            ax.text(0.5, 0.5, f'No data for {metric}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(ylabel)
            return
        
        # Plot each algorithm
        for algorithm in self.algorithms:
            alg_data = data[data['Algorithm'] == algorithm]
            if not alg_data.empty:
                density = alg_data['Density'].values
                values = alg_data[metric].apply(transform).values
                
                ax.plot(density, values, marker='o', linewidth=2, markersize=6,
                       label=algorithm.replace('-', ' ').title(),
                       color=self.algorithm_colors.get(algorithm, '#666666'))
        
        ax.set_xlabel('Network Density (nodes/km²)')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _generate_correlation_matrix(self, data, title, filename):
        """
        Generate correlation matrix heatmap
        """
        # Select numeric columns for correlation
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        correlation_cols = [col for col in numeric_cols if col in 
                           ['PDR', 'EnergyEfficiency', 'Throughput', 'AvgToA', 'AvgRSSI', 'AvgSNR']]
        
        if len(correlation_cols) < 2:
            print(f"⚠️  Insufficient numeric data for correlation matrix")
            return
        
        # Calculate correlation matrix
        corr_matrix = data[correlation_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0,
                   square=True, fmt='.3f', cbar_kws={'shrink': 0.8})
        plt.title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.figures_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_performance_matrix(self):
        """
        Generate comprehensive performance comparison matrix
        """
        print("📊 Generating performance comparison matrix...")
        
        if self.summary_data is None or self.summary_data.empty:
            print("⚠️  No summary data available for performance matrix")
            return
        
        # Key metrics for comparison
        metrics = ['PDR', 'EnergyEfficiency', 'Throughput', 'AvgRSSI', 'AvgSNR']
        
        # Calculate algorithm performance rankings
        performance_matrix = pd.DataFrame(index=self.algorithms, columns=metrics)
        
        for metric in metrics:
            if metric in self.summary_data.columns:
                # Calculate mean performance per algorithm
                alg_performance = self.summary_data.groupby('Algorithm')[metric].mean()
                
                # Rank algorithms (1 = best)
                rankings = alg_performance.rank(ascending=False if metric != 'AvgToA' else True)
                
                for alg in self.algorithms:
                    if alg in rankings.index:
                        performance_matrix.loc[alg, metric] = rankings[alg]
        
        # Convert to numeric and calculate overall score
        performance_matrix = performance_matrix.apply(pd.to_numeric, errors='coerce')
        performance_matrix['OverallScore'] = performance_matrix.mean(axis=1)
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        
        # Heatmap of rankings (lower is better)
        sns.heatmap(performance_matrix.iloc[:, :-1], annot=True, cmap='RdYlGn_r', 
                   center=3.5, vmin=1, vmax=6, fmt='.1f',
                   cbar_kws={'label': 'Algorithm Rank (1=Best, 6=Worst)'})
        
        plt.title('Algorithm Performance Matrix\n(Ranking across all metrics)', 
                 fontsize=14, fontweight='bold')
        plt.ylabel('Algorithms')
        plt.xlabel('Performance Metrics')
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'performance_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save rankings to CSV
        performance_matrix.to_csv(self.figures_dir / 'performance_rankings.csv')
        
        print(f"✅ Performance matrix saved to {self.figures_dir}")
        
        # Print summary
        print("\n🏆 Algorithm Performance Summary:")
        overall_rankings = performance_matrix['OverallScore'].sort_values()
        for i, (alg, score) in enumerate(overall_rankings.items(), 1):
            print(f"{i:2d}. {alg.replace('-', ' ').title():15s} (Score: {score:.2f})")
    
    def generate_energy_analysis(self):
        """
        Generate detailed energy efficiency analysis
        """
        print("⚡ Generating energy efficiency analysis...")
        
        if self.summary_data is None or self.summary_data.empty:
            print("⚠️  No data available for energy analysis")
            return
        
        # Create energy analysis figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Energy Efficiency Analysis', fontsize=16, fontweight='bold')
        
        # 1. Energy Efficiency vs PDR
        if 'EnergyEfficiency' in self.summary_data.columns and 'PDR' in self.summary_data.columns:
            for algorithm in self.algorithms:
                alg_data = self.summary_data[self.summary_data['Algorithm'] == algorithm]
                if not alg_data.empty:
                    axes[0, 0].scatter(alg_data['PDR'] * 100, alg_data['EnergyEfficiency'],
                                     label=algorithm.replace('-', ' ').title(),
                                     color=self.algorithm_colors.get(algorithm, '#666666'),
                                     alpha=0.7, s=50)
            
            axes[0, 0].set_xlabel('Packet Delivery Ratio (%)')
            axes[0, 0].set_ylabel('Energy Efficiency (packets/J)')
            axes[0, 0].set_title('Energy Efficiency vs PDR')
            axes[0, 0].legend(fontsize=8)
            axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Energy Efficiency vs Network Load (devices)
        if 'EnergyEfficiency' in self.summary_data.columns and 'Devices' in self.summary_data.columns:
            for algorithm in self.algorithms:
                alg_data = self.summary_data[self.summary_data['Algorithm'] == algorithm]
                if not alg_data.empty:
                    axes[0, 1].scatter(alg_data['Devices'], alg_data['EnergyEfficiency'],
                                     label=algorithm.replace('-', ' ').title(),
                                     color=self.algorithm_colors.get(algorithm, '#666666'),
                                     alpha=0.7, s=50)
            
            axes[0, 1].set_xlabel('Number of Devices')
            axes[0, 1].set_ylabel('Energy Efficiency (packets/J)')
            axes[0, 1].set_title('Energy Efficiency vs Network Size')
            axes[0, 1].legend(fontsize=8)
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Energy consumption distribution
        if 'TotalEnergyConsumed' in self.summary_data.columns:
            energy_by_alg = []
            labels = []
            for algorithm in self.algorithms:
                alg_data = self.summary_data[self.summary_data['Algorithm'] == algorithm]
                if not alg_data.empty and 'TotalEnergyConsumed' in alg_data.columns:
                    energy_by_alg.append(alg_data['TotalEnergyConsumed'].mean())
                    labels.append(algorithm.replace('-', ' ').title())
            
            if energy_by_alg:
                colors = [self.algorithm_colors.get(alg.lower().replace(' ', '-'), '#666666') for alg in labels]
                axes[1, 0].pie(energy_by_alg, labels=labels, colors=colors, autopct='%1.1f%%')
                axes[1, 0].set_title('Average Energy Consumption Distribution')
        
        # 4. Energy-Performance Trade-off
        if all(col in self.summary_data.columns for col in ['EnergyEfficiency', 'Throughput']):
            for algorithm in self.algorithms:
                alg_data = self.summary_data[self.summary_data['Algorithm'] == algorithm]
                if not alg_data.empty:
                    axes[1, 1].scatter(alg_data['Throughput'], alg_data['EnergyEfficiency'],
                                     label=algorithm.replace('-', ' ').title(),
                                     color=self.algorithm_colors.get(algorithm, '#666666'),
                                     alpha=0.7, s=50)
            
            axes[1, 1].set_xlabel('Throughput (packets/s)')
            axes[1, 1].set_ylabel('Energy Efficiency (packets/J)')
            axes[1, 1].set_title('Energy-Performance Trade-off')
            axes[1, 1].legend(fontsize=8)
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'energy_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Energy analysis saved to {self.figures_dir}")
    
    def generate_comprehensive_report(self):
        """
        Generate comprehensive text report with statistics
        """
        print("📝 Generating comprehensive report...")
        
        report_file = self.results_dir / 'comprehensive_report.md'
        
        with open(report_file, 'w') as f:
            f.write("# LoRaWAN Simulation Results - Comprehensive Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Executive Summary\n\n")
            
            if self.summary_data is not None and not self.summary_data.empty:
                total_simulations = len(self.summary_data)
                unique_scenarios = self.summary_data['Scenario'].nunique()
                f.write(f"- **Total Simulations:** {total_simulations}\n")
                f.write(f"- **Unique Scenarios:** {unique_scenarios}\n")
                f.write(f"- **Algorithms Tested:** {', '.join(self.algorithms)}\n\n")
                
                # Best performing algorithm overall
                if 'PDR' in self.summary_data.columns:
                    best_pdr = self.summary_data.groupby('Algorithm')['PDR'].mean().idxmax()
                    best_pdr_value = self.summary_data.groupby('Algorithm')['PDR'].mean().max()
                    f.write(f"- **Best PDR Algorithm:** {best_pdr} ({best_pdr_value*100:.1f}%)\n")
                
                if 'EnergyEfficiency' in self.summary_data.columns:
                    best_energy = self.summary_data.groupby('Algorithm')['EnergyEfficiency'].mean().idxmax()
                    best_energy_value = self.summary_data.groupby('Algorithm')['EnergyEfficiency'].mean().max()
                    f.write(f"- **Most Energy Efficient:** {best_energy} ({best_energy_value:.2f} packets/J)\n")
                
                f.write("\n")
            
            # Scenario summaries
            for scenario_name, scenario_data in self.data.items():
                if scenario_data is not None and not scenario_data.empty:
                    f.write(f"## {scenario_name.replace('_', ' ').title()}\n\n")
                    
                    f.write(f"- **Simulations:** {len(scenario_data)}\n")
                    
                    if 'Algorithm' in scenario_data.columns:
                        algorithms_tested = scenario_data['Algorithm'].unique()
                        f.write(f"- **Algorithms:** {', '.join(algorithms_tested)}\n")
                    
                    # Key findings for each scenario
                    if 'PDR' in scenario_data.columns:
                        best_alg = scenario_data.groupby('Algorithm')['PDR'].mean().idxmax()
                        best_pdr = scenario_data.groupby('Algorithm')['PDR'].mean().max()
                        worst_alg = scenario_data.groupby('Algorithm')['PDR'].mean().idxmin()
                        worst_pdr = scenario_data.groupby('Algorithm')['PDR'].mean().min()
                        
                        f.write(f"- **Best PDR:** {best_alg} ({best_pdr*100:.1f}%)\n")
                        f.write(f"- **Worst PDR:** {worst_alg} ({worst_pdr*100:.1f}%)\n")
                        f.write(f"- **PDR Range:** {(best_pdr - worst_pdr)*100:.1f} percentage points\n")
                    
                    f.write("\n")
            
            f.write("## Methodology\n\n")
            f.write("This analysis was performed on NS-3.42 LoRaWAN simulation results. ")
            f.write("The following metrics were evaluated:\n\n")
            f.write("- **PDR (Packet Delivery Ratio):** Percentage of packets successfully received\n")
            f.write("- **Energy Efficiency:** Packets delivered per unit of energy consumed\n")
            f.write("- **Throughput:** Packets successfully delivered per second\n")
            f.write("- **ToA (Time on Air):** Average transmission time per packet\n")
            f.write("- **RSSI:** Received Signal Strength Indicator\n")
            f.write("- **SNR:** Signal-to-Noise Ratio\n\n")
            
            f.write("## Conclusions and Recommendations\n\n")
            f.write("Based on the comprehensive analysis of all scenarios:\n\n")
            
            if self.summary_data is not None and not self.summary_data.empty:
                # Algorithm performance summary
                if 'PDR' in self.summary_data.columns:
                    pdr_rankings = self.summary_data.groupby('Algorithm')['PDR'].mean().sort_values(ascending=False)
                    f.write("**PDR Performance Ranking:**\n")
                    for i, (alg, pdr) in enumerate(pdr_rankings.items(), 1):
                        f.write(f"{i}. {alg.replace('-', ' ').title()}: {pdr*100:.1f}%\n")
                    f.write("\n")
                
                if 'EnergyEfficiency' in self.summary_data.columns:
                    energy_rankings = self.summary_data.groupby('Algorithm')['EnergyEfficiency'].mean().sort_values(ascending=False)
                    f.write("**Energy Efficiency Ranking:**\n")
                    for i, (alg, eff) in enumerate(energy_rankings.items(), 1):
                        f.write(f"{i}. {alg.replace('-', ' ').title()}: {eff:.3f} packets/J\n")
                    f.write("\n")
            
            f.write("---\n")
            f.write("*Report generated by LoRaWAN Analyzer*\n")
        
        print(f"✅ Comprehensive report saved to {report_file}")
    
    def run_complete_analysis(self):
        """
        Run complete analysis workflow
        """
        print("🚀 Starting complete LoRaWAN simulation analysis...\n")
        
        # Load data
        self.load_data()
        
        if self.summary_data is None or self.summary_data.empty:
            print("❌ No data available for analysis. Please check your results directory.")
            return
        
        print(f"📊 Analyzing {len(self.summary_data)} simulation results...\n")
        
        # Generate all analyses
        try:
            self.generate_overview_report()
            self.analyze_scenario1_device_density()
            self.analyze_scenario2_sf_variation()
            self.analyze_scenario3_interval_variation()
            self.analyze_scenario4_mobility_variation()
            self.analyze_scenario5_network_density()
            self.generate_performance_matrix()
            self.generate_energy_analysis()
            self.generate_comprehensive_report()
            
            print("\n🎉 Complete analysis finished successfully!")
            print(f"📁 All results saved to: {self.figures_dir}")
            print(f"📝 Comprehensive report: {self.results_dir / 'comprehensive_report.md'}")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()


def main():
    """
    Main function to run the analysis
    """
    parser = argparse.ArgumentParser(
        description='LoRaWAN Simulation Results Analysis and Visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python analyze-results.py /path/to/results
  python analyze-results.py /path/to/results --scenario 1
  python analyze-results.py ./results/session_20240101_120000 --output-dir ./analysis
        '''
    )
    
    parser.add_argument('results_dir', 
                       help='Path to simulation results directory')
    parser.add_argument('--scenario', type=int, choices=[1, 2, 3, 4, 5],
                       help='Analyze specific scenario only (1-5)')
    parser.add_argument('--output-dir', 
                       help='Output directory for analysis results (default: results_dir/figures)')
    parser.add_argument('--format', choices=['png', 'pdf', 'svg'], default='png',
                       help='Output format for figures (default: png)')
    
    args = parser.parse_args()
    
    # Validate results directory
    if not os.path.exists(args.results_dir):
        print(f"❌ Results directory not found: {args.results_dir}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = LoRaWANAnalyzer(args.results_dir)
    
    # Override output directory if specified
    if args.output_dir:
        analyzer.figures_dir = Path(args.output_dir)
        analyzer.figures_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    if args.scenario:
        # Run specific scenario analysis
        analyzer.load_data()
        scenario_methods = {
            1: analyzer.analyze_scenario1_device_density,
            2: analyzer.analyze_scenario2_sf_variation,
            3: analyzer.analyze_scenario3_interval_variation,
            4: analyzer.analyze_scenario4_mobility_variation,
            5: analyzer.analyze_scenario5_network_density
        }
        
        if args.scenario in scenario_methods:
            scenario_methods[args.scenario]()
            print(f"✅ Scenario {args.scenario} analysis completed")
        else:
            print(f"❌ Invalid scenario number: {args.scenario}")
    else:
        # Run complete analysis
        analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()