#!/usr/bin/env python

"""
Script to analyze network metrics using Pyshark from a Mininet simulation
and save results to a CSV file.
"""

import pyshark
import argparse
import csv
from datetime import datetime


def parse_arguments():
    parser = argparse.ArgumentParser(description="Network metrics analysis using Pyshark")
    parser.add_argument(
        "-i", "--interface", required=True, help="Interface to capture traffic (e.g., s1-eth1)"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="Duration of the capture in seconds"
    )
    parser.add_argument(
        "-o", "--output", default="network_metrics.csv", help="Output CSV file for metrics"
    )
    return parser.parse_args()


def analyze_packets(packets):
    metrics = {
        "packet_count": 0,
        "bytes_transferred": 0,
        "start_time": None,
        "end_time": None,
        "delay_samples": [],
    }

    previous_packet_time = None

    for packet in packets:
        try:
            # Count the packet
            metrics["packet_count"] += 1

            # Get packet size
            metrics["bytes_transferred"] += int(packet.length)

            # Track start and end time
            timestamp = datetime.fromtimestamp(float(packet.sniff_timestamp))
            if metrics["start_time"] is None:
                metrics["start_time"] = timestamp
            metrics["end_time"] = timestamp

            # Calculate delay (difference between current and previous packet)
            if previous_packet_time:
                delay = (timestamp - previous_packet_time).total_seconds()
                metrics["delay_samples"].append(delay)
            previous_packet_time = timestamp

        except AttributeError:
            # Skip packets that are missing attributes
            continue

    return metrics


def calculate_metrics(metrics):
    duration = (metrics["end_time"] - metrics["start_time"]).total_seconds()
    throughput = (metrics["bytes_transferred"] * 8) / duration if duration > 0 else 0
    average_delay = (
        sum(metrics["delay_samples"]) / len(metrics["delay_samples"])
        if metrics["delay_samples"]
        else 0
    )

    return {
        "total_packets": metrics["packet_count"],
        "total_bytes": metrics["bytes_transferred"],
        "duration": duration,
        "throughput_bps": throughput,
        "average_delay_s": average_delay,
    }


def save_metrics_to_csv(calculated_metrics, output_file):
    fieldnames = [
        "total_packets",
        "total_bytes",
        "duration_s",
        "throughput_bps",
        "average_delay_s",
    ]

    # Check if the file exists to write header only once
    try:
        with open(output_file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if file is empty
            csvfile.seek(0, 2)  # Go to the end of the file
            if csvfile.tell() == 0:  # If file is empty
                writer.writeheader()

            # Write the metrics
            writer.writerow(calculated_metrics)
            print(f"Metrics saved to {output_file}")
    except IOError as e:
        print(f"Error saving metrics to CSV: {e}")


def print_metrics(calculated_metrics):
    print("==== Network Metrics ====")
    print(f"Total Packets Captured: {calculated_metrics['total_packets']}")
    print(f"Total Data Transferred: {calculated_metrics['total_bytes']} bytes")
    print(f"Duration: {calculated_metrics['duration_s']:.2f} seconds")
    print(f"Throughput: {calculated_metrics['throughput_bps']:.2f} bps")
    print(f"Average Delay: {calculated_metrics['average_delay_s']:.6f} seconds")
    print("=========================")


def main():
    args = parse_arguments()
    print(f"Starting capture on interface {args.interface} for {args.timeout} seconds...")

    capture = pyshark.LiveCapture(interface=args.interface)
    capture.sniff(timeout=args.timeout)

    print("Analyzing packets...")
    metrics = analyze_packets(capture)
    calculated_metrics = calculate_metrics(metrics)

    print_metrics(calculated_metrics)

    # Save metrics to CSV
    save_metrics_to_csv(calculated_metrics, args.output)


if __name__ == "__main__":
    main()

