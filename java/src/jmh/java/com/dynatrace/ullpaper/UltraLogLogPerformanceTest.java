//
// Copyright (c) 2024 Dynatrace LLC. All rights reserved.
//
// This software and associated documentation files (the "Software")
// are being made available by Dynatrace LLC for the sole purpose of
// illustrating the implementation of certain algorithms which have
// been published by Dynatrace LLC. Permission is hereby granted,
// free of charge, to any person obtaining a copy of the Software,
// to view and use the Software for internal, non-production,
// non-commercial purposes only – the Software may not be used to
// process live data or distributed, sublicensed, modified and/or
// sold either alone or as part of or in combination with any other
// software.
//
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
// OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
// NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
// WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.
//
package com.dynatrace.ullpaper;

import com.dynatrace.hash4j.distinctcount.MartingaleEstimator;
import com.dynatrace.hash4j.distinctcount.UltraLogLog;
import java.util.Arrays;
import java.util.SplittableRandom;
import java.util.stream.Stream;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

public class UltraLogLogPerformanceTest {

  private static UltraLogLog generate(SplittableRandom random, long numElements, int precision) {
    UltraLogLog sketch = UltraLogLog.create(precision);
    random.longs(numElements).forEach(sketch::add);
    return sketch;
  }

  @State(Scope.Thread)
  public static class AddState {

    @Param({
      "10000000",
      "5000000",
      "2000000",
      "1000000",
      "500000",
      "200000",
      "100000",
      "50000",
      "20000",
      "10000",
      "5000",
      "2000",
      "1000",
      "500",
      "200",
      "100",
      "50",
      "20",
      "10",
      "5",
      "2",
      "1",
      "0"
    })
    public int numElements;

    @Param({"16", "14", "12", "10", "8"})
    public int precision;

    public SplittableRandom random;

    @Setup(Level.Trial)
    public void init() {
      random = new SplittableRandom();
    }
  }

  @Benchmark
  @BenchmarkMode(Mode.AverageTime)
  public void distinctCountAdd(AddState addState, Blackhole blackhole) {
    final UltraLogLog sketch = UltraLogLog.create(addState.precision);
    for (long i = 0; i < addState.numElements; ++i) {
      sketch.add(addState.random.nextLong());
    }
    blackhole.consume(sketch);
  }

  @Benchmark
  @BenchmarkMode(Mode.AverageTime)
  public void distinctCountAddWithMartingaleEstimator(AddState addState, Blackhole blackhole) {
    final UltraLogLog sketch = UltraLogLog.create(addState.precision);
    final MartingaleEstimator martingaleEstimator = new MartingaleEstimator();
    for (long i = 0; i < addState.numElements; ++i) {
      sketch.add(addState.random.nextLong(), martingaleEstimator);
    }
    blackhole.consume(martingaleEstimator.getDistinctCountEstimate());
  }

  public enum Estimator {
    MAXIMUM_LIKELIHOOD_ESTIMATOR(UltraLogLog.MAXIMUM_LIKELIHOOD_ESTIMATOR),
    OPTIMAL_FGRA_ESTIMATOR(UltraLogLog.OPTIMAL_FGRA_ESTIMATOR);

    private final UltraLogLog.Estimator estimator;

    Estimator(UltraLogLog.Estimator estimator) {
      this.estimator = estimator;
    }
  }

  @State(Scope.Benchmark)
  public static class EstimationState {

    UltraLogLog[] sketches = null;

    @Param({
      "10000000",
      "5000000",
      "2000000",
      "1000000",
      "500000",
      "200000",
      "100000",
      "50000",
      "20000",
      "10000",
      "5000",
      "2000",
      "1000",
      "500",
      "200",
      "100",
      "50",
      "20",
      "10",
      "5",
      "2",
      "1",
      "0"
    })
    public int numElements;

    @Param({"16", "15", "14", "13", "12", "11", "10", "9", "8"})
    public int precision;

    @Param public Estimator estimator;

    @Param({"100"})
    public int numMaxDifferentExamples;

    @Param({"10000000"})
    public int memorySizeForExamplesInBytes;

    @Setup(Level.Trial)
    public void init() {
      SplittableRandom random = new SplittableRandom();
      int numExamples =
          memorySizeForExamplesInBytes / UltraLogLog.create(precision).getState().length;
      sketches = new UltraLogLog[numExamples];
      for (int i = 0; i < numExamples; ++i) {
        if (i < numMaxDifferentExamples) {
          sketches[i] = generate(random, numElements, precision);
        } else {
          byte[] data = sketches[i % numMaxDifferentExamples].getState();
          sketches[i] = UltraLogLog.wrap(Arrays.copyOf(data, data.length));
        }
      }
    }

    @TearDown(Level.Trial)
    public void finish() {
      sketches = null;
    }
  }

  @Benchmark
  @BenchmarkMode(Mode.AverageTime)
  public void distinctCountEstimation(EstimationState estimationState, Blackhole blackhole) {
    UltraLogLog.Estimator estimator = estimationState.estimator.estimator;
    for (int i = 0; i < estimationState.sketches.length; ++i) {
      double estimate = estimator.estimate(estimationState.sketches[i]);
      blackhole.consume(estimate);
    }
  }

  @State(Scope.Benchmark)
  public static class RegisterScanState {

    UltraLogLog[] sketches = null;

    @Param({"16", "15", "14", "13", "12", "11", "10", "9", "8"})
    public int precision;

    @Param public Estimator estimator;

    @Param({"10000000"})
    public int memorySizeForExamplesInBytes;

    @Setup(Level.Trial)
    public void init() {
      int numExamples =
          memorySizeForExamplesInBytes / UltraLogLog.create(precision).getState().length;
      sketches =
          Stream.generate(() -> UltraLogLog.create(precision))
              .limit(numExamples)
              .toArray(i -> new UltraLogLog[i]);
    }

    @TearDown(Level.Trial)
    public void finish() {
      sketches = null;
    }
  }

  @Benchmark
  @BenchmarkMode(Mode.AverageTime)
  public void registerScan(RegisterScanState registerScanState, Blackhole blackhole) {
    for (int i = 0; i < registerScanState.sketches.length; ++i) {
      byte[] state = registerScanState.sketches[i].getState();
      int sum = 0;
      for (byte b : state) {
        int r = b & 0xFF;
        sum += r;
      }
      blackhole.consume(sum);
    }
  }
}
