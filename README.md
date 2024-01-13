# UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting

This repository contains the source code to reproduce the results and figures presented in the paper ["UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog for Approximate Distinct Counting"](https://arxiv.org/abs/2308.16862).

## Abstract
Since its invention HyperLogLog has become the standard algorithm for approximate distinct counting. Due to its space efficiency and suitability for distributed systems, it is widely used and also implemented in numerous databases. This work presents UltraLogLog, which shares the same practical properties as HyperLogLog. It is commutative, idempotent, mergeable, and has a fast guaranteed constant-time insert operation. At the same time, it requires 28% less space to encode the same amount of distinct count information, which can be extracted using the maximum likelihood method. Alternatively, a simpler and faster estimator is proposed, which still achieves a space reduction of 24%, but at an estimation speed comparable to that of HyperLogLog. In a non-distributed setting where martingale estimation can be used, UltraLogLog is able to reduce space by 17%. Moreover, its smaller entropy and its 8-bit registers lead to better compaction when using standard compression algorithms. All this is verified by experimental results that are in perfect agreement with the theoretical analysis which also outlines potential for even more space-efficient data structures. A production-ready Java implementation of UltraLogLog has been released as part of the open-source [Hash4j library](https://github.com/dynatrace-oss/hash4j).

## Steps to reproduce the results and figures presented in the paper
1. Create an Amazon EC2 [c5.metal](https://aws.amazon.com/ec2/instance-types/c5/) instance with Ubuntu Server 22.04 LTS and 20GiB of storage.
2. Clone the repository including submodules:
   ```
   git clone https://github.com/dynatrace-research/ultraloglog-paper.git && cd ultraloglog-paper && git submodule init && git submodule update
   ```
3. Install all required packages:
   ```
   sudo apt update && sudo NEEDRESTART_MODE=a apt --yes install openjdk-11-jdk openjdk-21-jdk python-is-python3 python3-pip texlive texlive-latex-extra texlive-fonts-extra texlive-science cm-super && pip install -r python/requirements.txt
   ```
4. To reproduce the performance benchmark results `results/benchmark-results.json` disable Turbo Boost ([set P-state to 1](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/processor_state_control.html)), run the `runBenchmarks` task in the root directory (takes ~9.5h), and enable Turbo Boost again:
   ```
   sudo sh -c "echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo"; ./gradlew runBenchmarks; sudo sh -c "echo 0 > /sys/devices/system/cpu/intel_pstate/no_turbo"
   ```
5. To reproduce the compression simulation results `results/compression/*.csv` run the `runCompressionSimulation` task in the root directory (takes ~45min):
   ```
   ./gradlew runCompressionSimulation
   ```
6. To reproduce the estimation error results `hash4j/test-results/*.csv` run the `simulateEstimationErrors` tasks in the `hash4j` directory  (takes ~17h):
   ```
   cd hash4j; ./gradlew simulateEstimationErrors; cd ..
   ```
7. (Re-)generate all figures in the `paper` directory by executing the `pdfFigures` task in the root directory (takes ~15min):
   ```
   ./gradlew pdfFigures
   ```
   The produced figures can be found in the `paper` directory. Furthermore, numeric constants given in the paper can be found in `results\mvp.txt`.
8. To examine the empirical memory-variance product (MVP) based on the actual allocated memory and the serialization size of different data structure implementations for approximate distinct counting run the `runEmpiricalMVPComputation` task in the root directory (takes ~2.5h, not needed for the figures):
   ```
   ./gradlew runEmpiricalMVPComputation
   ```
   The results can be found in the `results\comparison-empirical-mvp` folder. In particular, the results in `Apache Data Sketches Java CPC.csv` confirm the statement in the introduction section of the paper that the memory footprint of the CPC implementation of [Apache DataSketches](https://github.com/apache/datasketches-java) is more than twice as large as the serialization size.