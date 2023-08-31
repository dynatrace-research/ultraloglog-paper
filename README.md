# UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting

This repository contains the source code to reproduce the results and figures presented in the paper "UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting".

## Abstract
Since its invention HyperLogLog has become the standard algorithm for approximate distinct counting. Due to its space efficiency and suitability for distributed systems, it is widely used and also implemented in numerous databases. This work presents UltraLogLog, which shares the same practical properties as HyperLogLog. It is commutative, idempotent, mergeable, and has a fast guaranteed constant-time insert operation. At the same time, it requires 28% less space to encode the same amount of distinct count information, which can be extracted using the maximum likelihood method. Alternatively, a simpler and faster estimator is proposed, which still achieves a space reduction of 24%, but at an estimation speed comparable to that of HyperLogLog. In a non-distributed setting where martingale estimation can be used, UltraLogLog is able to reduce space by 17%. Moreover, its smaller entropy and its 8-bit registers lead to better compaction when using standard compression algorithms. All this is verified by experimental results that are in perfect agreement with the theoretical analysis which also outlines potential for even more space-efficient data structures. A production-ready Java implementation of UltraLogLog has been released as part of the open-source Hash4j library.

## Steps to reproduce the results and figures on Windows 11
1. Install Windows Subsystem for Linux (WSL) with [Ubuntu 22.04.2 LTS](https://apps.microsoft.com/store/detail/ubuntu-22042-lts/9PN20MSR04DW)

2. Install required packages:
   ```
   sudo apt update && sudo apt install python-is-python3 [TODO determine required packages]
   pip install matplotlib-label-lines
   ```
3. Clone repository including submodules:
   ```
   git clone --recursive https://github.com/dynatrace-research/ultraloglog-paper.git
   ```
4. Run performance benchmarks in the root folder (takes several hours):
   ```
    ./gradlew runBenchmarks
   ```
5. Run compression simulations in the root folder:
   ```
    ./gradlew runCompressionSimulation
   ```
6. Run estimation error simulations in the `hash4j` folder (takes several hours):
   ```
   ./gradlew simulateEstimationErrors
   ```
7. Generate all figures:
   ```
   ./gradlew pdfFigures
   ```