//
// Copyright (c) 2022-2024 Dynatrace LLC. All rights reserved.
//
// This software and associated documentation files (the "Software")
// are being made available by Dynatrace LLC for purposes of
// illustrating the implementation of certain algorithms which have
// been published by Dynatrace LLC. Permission is hereby granted,
// free of charge, to any person obtaining a copy of the Software,
// to view and use the Software for internal, non-productive,
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

import com.dynatrace.hash4j.distinctcount.HyperLogLog;
import com.dynatrace.hash4j.distinctcount.MartingaleEstimator;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.SplittableRandom;
import java.util.stream.Stream;
import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;

public class HyperLogLogPerformanceTest {

  private static final VarHandle INT_HANDLE =
      MethodHandles.byteArrayViewVarHandle(int[].class, ByteOrder.LITTLE_ENDIAN);

  private static int getInt(byte[] b, int off) {
    return (int) INT_HANDLE.get(b, off);
  }

  private static HyperLogLog generate(SplittableRandom random, long numElements, int precision) {
    HyperLogLog sketch = HyperLogLog.create(precision);
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
    final HyperLogLog sketch = HyperLogLog.create(addState.precision);
    for (long i = 0; i < addState.numElements; ++i) {
      sketch.add(addState.random.nextLong());
    }
    blackhole.consume(sketch);
  }

  @Benchmark
  @BenchmarkMode(Mode.AverageTime)
  public void distinctCountAddWithMartingaleEstimator(AddState addState, Blackhole blackhole) {
    final HyperLogLog sketch = HyperLogLog.create(addState.precision);
    final MartingaleEstimator martingaleEstimator = new MartingaleEstimator();
    for (long i = 0; i < addState.numElements; ++i) {
      sketch.add(addState.random.nextLong(), martingaleEstimator);
    }
    blackhole.consume(martingaleEstimator.getDistinctCountEstimate());
  }

  public enum Estimator {
    MAXIMUM_LIKELIHOOD_ESTIMATOR(HyperLogLog.MAXIMUM_LIKELIHOOD_ESTIMATOR),
    CORRECTED_RAW_ESTIMATOR(HyperLogLog.CORRECTED_RAW_ESTIMATOR);

    private final HyperLogLog.Estimator estimator;

    Estimator(HyperLogLog.Estimator estimator) {
      this.estimator = estimator;
    }
  }

  @State(Scope.Benchmark)
  public static class EstimationState {

    HyperLogLog[] sketches = null;

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
          memorySizeForExamplesInBytes / HyperLogLog.create(precision).getState().length;
      sketches = new HyperLogLog[numExamples];
      for (int i = 0; i < numExamples; ++i) {
        if (i < numMaxDifferentExamples) {
          sketches[i] = generate(random, numElements, precision);
        } else {
          byte[] data = sketches[i % numMaxDifferentExamples].getState();
          sketches[i] = HyperLogLog.wrap(Arrays.copyOf(data, data.length));
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
    HyperLogLog.Estimator estimator = estimationState.estimator.estimator;
    for (int i = 0; i < estimationState.sketches.length; ++i) {
      double estimate = estimator.estimate(estimationState.sketches[i]);
      blackhole.consume(estimate);
    }
  }

  @State(Scope.Benchmark)
  public static class RegisterScanState {

    HyperLogLog[] sketches = null;

    @Param({"16", "15", "14", "13", "12", "11", "10", "9", "8"})
    public int precision;

    @Param public Estimator estimator;

    @Param({"10000000"})
    public int memorySizeForExamplesInBytes;

    @Setup(Level.Trial)
    public void init() {
      int numExamples =
          memorySizeForExamplesInBytes / HyperLogLog.create(precision).getState().length;
      sketches =
          Stream.generate(() -> HyperLogLog.create(precision))
              .limit(numExamples)
              .toArray(i -> new HyperLogLog[i]);
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

      for (int off = 0; off + 6 <= state.length; off += 6) {
        int s0 = getInt(state, off);
        int s1 = getInt(state, off + 2);
        int r0 = s0 & 0x3F;
        int r1 = (s0 >>> 6) & 0x3F;
        int r2 = (s0 >>> 12) & 0x3F;
        int r3 = (s0 >>> 18) & 0x3F;
        int r4 = (s1 >>> 8) & 0x3F;
        int r5 = (s1 >>> 14) & 0x3F;
        int r6 = (s1 >>> 20) & 0x3F;
        int r7 = (s1 >>> 26) & 0x3F;
        sum += r0;
        sum += r1;
        sum += r2;
        sum += r3;
        sum += r4;
        sum += r5;
        sum += r6;
        sum += r7;
      }
      blackhole.consume(sum);
    }
  }
}
