# UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting

This repository contains the source code to reproduce the results and figures presented in the paper ["UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting"](https://arxiv.org/abs/2308.16862).

## Abstract
Since its invention HyperLogLog has become the standard algorithm for approximate distinct counting. Due to its space efficiency and suitability for distributed systems, it is widely used and also implemented in numerous databases. This work presents UltraLogLog, which shares the same practical properties as HyperLogLog. It is commutative, idempotent, mergeable, and has a fast guaranteed constant-time insert operation. At the same time, it requires 28% less space to encode the same amount of distinct count information, which can be extracted using the maximum likelihood method. Alternatively, a simpler and faster estimator is proposed, which still achieves a space reduction of 24%, but at an estimation speed comparable to that of HyperLogLog. In a non-distributed setting where martingale estimation can be used, UltraLogLog is able to reduce space by 17%. Moreover, its smaller entropy and its 8-bit registers lead to better compaction when using standard compression algorithms. All this is verified by experimental results that are in perfect agreement with the theoretical analysis which also outlines potential for even more space-efficient data structures. A production-ready Java implementation of UltraLogLog has been released as part of the open-source [Hash4j library](https://github.com/dynatrace-oss/hash4j).

## Steps to reproduce the results and figures on Windows 10/11
1. Install the Windows Subsystem for Linux (WSL) with [Ubuntu 22.04.2 LTS](https://apps.microsoft.com/store/detail/ubuntu-22042-lts/9PN20MSR04DW).

2. Install all required packages:
   ```
   sudo apt update && sudo apt --yes install openjdk-17-jre python-is-python3 python3-pip texlive texlive-latex-extra texlive-fonts-extra texlive-science cm-super && pip install matplotlib matplotlib-label-lines scipy
   ```
3. Clone the repository including submodules:
   ```
   git clone --recurse-submodules https://github.com/dynatrace-research/ultraloglog-paper.git
   ```
4. Run the performance benchmarks in the root directory (takes ~8h):
   ```
    ./gradlew runBenchmarks
   ```
5. Run the compression simulations in the root directory (takes ~2h):
   ```
    ./gradlew runCompressionSimulation
   ```
6. Run the estimation error simulations in the `hash4j` directory (takes ~50h):
   ```
   ./gradlew simulateEstimationErrors
   ```
7. Compute the empirical memory-variance product (MVP) based on the actual allocated memory and the serialization size as given in `results\comparison-empirical-mvp` by running the `runEmpiricalMVPComputation` task in the root directory (takes ~2h, not needed for the figures):
   ```
   ./gradlew runEmpiricalMVPComputation
   ```
8. Generate all figures in the `paper` directory by executing the `pdfFigures` task in the root directory (takes ~5min):
   ```
   ./gradlew pdfFigures
   ```