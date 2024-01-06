//
// Copyright (c) 2023-2024 Dynatrace LLC. All rights reserved.
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
import com.dynatrace.hash4j.distinctcount.UltraLogLog;
import com.google.zetasketch.HyperLogLogPlusPlus;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.LongStream;
import org.apache.datasketches.cpc.CpcSketch;
import org.apache.datasketches.cpc.CpcUnion;
import org.apache.datasketches.hll.HllSketch;
import org.apache.datasketches.hll.TgtHllType;
import org.openjdk.jol.info.GraphLayout;

public class EmpiricalMVPComputation {

  private interface Config<T> {
    T create(int p);

    long getSerializedSizeInBytes(T sketch);

    default long getInMemorySizeInBytes(T sketch) {
      return GraphLayout.parseInstance(sketch).totalSize();
    }

    void add(T sketch, long nextLong);

    String getLabel();

    double getEstimate(T sketch, int p);
  }

  private static class Hash4jUltraLogLogMLConfig implements Config<UltraLogLog> {

    @Override
    public UltraLogLog create(int p) {
      return UltraLogLog.create(p);
    }

    @Override
    public long getSerializedSizeInBytes(UltraLogLog sketch) {
      return sketch.getState().length;
    }

    @Override
    public void add(UltraLogLog sketch, long nextLong) {
      sketch.add(nextLong);
    }

    @Override
    public String getLabel() {
      return "Hash4j UltraLogLog ML";
    }

    @Override
    public double getEstimate(UltraLogLog sketch, int p) {
      return sketch.getDistinctCountEstimate(UltraLogLog.MAXIMUM_LIKELIHOOD_ESTIMATOR);
    }
  }

  private static class Hash4jUltraLogLogFGRAConfig implements Config<UltraLogLog> {

    @Override
    public UltraLogLog create(int p) {
      return UltraLogLog.create(p);
    }

    @Override
    public long getSerializedSizeInBytes(UltraLogLog sketch) {
      return sketch.getState().length;
    }

    @Override
    public void add(UltraLogLog sketch, long nextLong) {
      sketch.add(nextLong);
    }

    @Override
    public String getLabel() {
      return "Hash4j UltraLogLog FGRA";
    }

    @Override
    public double getEstimate(UltraLogLog sketch, int p) {
      return sketch.getDistinctCountEstimate(UltraLogLog.OPTIMAL_FGRA_ESTIMATOR);
    }
  }

  private static class Hash4jHyperLogLogMLConfig implements Config<HyperLogLog> {

    @Override
    public HyperLogLog create(int p) {
      return HyperLogLog.create(p);
    }

    @Override
    public long getSerializedSizeInBytes(HyperLogLog sketch) {
      return sketch.getState().length;
    }

    @Override
    public void add(HyperLogLog sketch, long nextLong) {
      sketch.add(nextLong);
    }

    @Override
    public String getLabel() {
      return "Hash4j HyperLogLog ML";
    }

    @Override
    public double getEstimate(HyperLogLog sketch, int p) {
      return sketch.getDistinctCountEstimate(HyperLogLog.MAXIMUM_LIKELIHOOD_ESTIMATOR);
    }
  }

  private static class Hash4jHyperLogLogCRConfig implements Config<HyperLogLog> {

    @Override
    public HyperLogLog create(int p) {
      return HyperLogLog.create(p);
    }

    @Override
    public long getSerializedSizeInBytes(HyperLogLog sketch) {
      return sketch.getState().length;
    }

    @Override
    public void add(HyperLogLog sketch, long nextLong) {
      sketch.add(nextLong);
    }

    @Override
    public String getLabel() {
      return "Hash4j HyperLogLog CR";
    }

    @Override
    public double getEstimate(HyperLogLog sketch, int p) {
      return sketch.getDistinctCountEstimate(HyperLogLog.CORRECTED_RAW_ESTIMATOR);
    }
  }

  private static class ApacheDataSketchesCPCConfig implements Config<CpcSketch> {

    @Override
    public CpcSketch create(int p) {
      return new CpcSketch(p);
    }

    @Override
    public long getSerializedSizeInBytes(CpcSketch sketch) {
      return sketch.toByteArray().length;
    }

    @Override
    public void add(CpcSketch sketch, long nextLong) {
      sketch.update(nextLong);
    }

    @Override
    public String getLabel() {
      return "Apache Data Sketches Java CPC";
    }

    @Override
    public double getEstimate(CpcSketch sketch, int p) {
      CpcUnion union = new CpcUnion(p);
      union.update(sketch);
      return union.getResult().getEstimate(); // hack to ensure that hip estimator is not used
    }
  }

  private abstract static class ApacheDataSketchesHLLConfig implements Config<HllSketch> {

    protected abstract TgtHllType getType();

    protected abstract String getTypeName();

    @Override
    public HllSketch create(int p) {
      return new HllSketch(p, getType());
    }

    @Override
    public long getSerializedSizeInBytes(HllSketch sketch) {
      return sketch.toCompactByteArray().length;
    }

    @Override
    public void add(HllSketch sketch, long nextLong) {
      sketch.update(nextLong);
    }

    @Override
    public String getLabel() {
      return "Apache Data Sketches Java " + getTypeName();
    }

    @Override
    public double getEstimate(HllSketch sketch, int p) {
      return sketch.getCompositeEstimate();
    }
  }

  private static class ApacheDataSketchesHLL4Config extends ApacheDataSketchesHLLConfig {

    @Override
    protected TgtHllType getType() {
      return TgtHllType.HLL_4;
    }

    @Override
    protected String getTypeName() {
      return "HLL4";
    }
  }

  private static class ApacheDataSketchesHLL6Config extends ApacheDataSketchesHLLConfig {

    @Override
    protected TgtHllType getType() {
      return TgtHllType.HLL_6;
    }

    @Override
    protected String getTypeName() {
      return "HLL6";
    }
  }

  private static class ApacheDataSketchesHLL8Config extends ApacheDataSketchesHLLConfig {

    @Override
    protected TgtHllType getType() {
      return TgtHllType.HLL_8;
    }

    @Override
    protected String getTypeName() {
      return "HLL8";
    }
  }

  protected abstract static class ZetaSketchConfig implements Config<HyperLogLogPlusPlus<Long>> {

    protected abstract HyperLogLogPlusPlus.Builder contribute(
        int p, HyperLogLogPlusPlus.Builder builder);

    @Override
    public HyperLogLogPlusPlus<Long> create(int p) {
      return contribute(p, new HyperLogLogPlusPlus.Builder()).buildForLongs();
    }

    @Override
    public long getSerializedSizeInBytes(HyperLogLogPlusPlus<Long> sketch) {
      return sketch.serializeToByteArray().length;
    }

    @Override
    public void add(HyperLogLogPlusPlus<Long> sketch, long nextLong) {
      sketch.add(nextLong);
    }

    @Override
    public double getEstimate(HyperLogLogPlusPlus<Long> sketch, int p) {
      return sketch.result();
    }
  }

  protected static class ZetaSketchConfigDenseConfig extends ZetaSketchConfig {
    @Override
    protected HyperLogLogPlusPlus.Builder contribute(int p, HyperLogLogPlusPlus.Builder builder) {
      return builder.normalPrecision(p).noSparseMode();
    }

    @Override
    public String getLabel() {
      return "Google Zetasketch Dense";
    }
  }

  protected static class ZetaSketchConfigSparseConfig extends ZetaSketchConfig {
    @Override
    protected HyperLogLogPlusPlus.Builder contribute(int p, HyperLogLogPlusPlus.Builder builder) {
      return builder.sparsePrecision(p).normalPrecision(p);
    }

    @Override
    public String getLabel() {
      return "Google Zetasketch Sparse";
    }
  }

  private static long[] getDistinctCounts(long max, double relativeStep) {
    List<Long> result = new ArrayList<>();
    while (max > 0) {
      result.add(max);
      max = Math.min(max - 1, (long) Math.ceil(max / (1 + relativeStep)));
    }
    Collections.reverse(result);
    return result.stream().mapToLong(i -> i).toArray();
  }

  private static final class Statistics {

    private final long trueDistinctCount;

    private long sumInMemorySizeInBytes = 0;

    private long minimumInMemorySizeInBytes = Long.MAX_VALUE;

    private long maximumInMemorySizeInBytes = Long.MIN_VALUE;
    private long sumSerializationSizeInBytes = 0;

    private long minimumSerializationSizeInBytes = Long.MAX_VALUE;

    private long maximumSerializationSizeInBytes = Long.MIN_VALUE;

    private long count = 0;

    private double sumDistinctCountEstimationError = 0;

    private double sumDistinctCountEstimationErrorSquared = 0;

    private Statistics(long trueDistinctCount) {
      this.trueDistinctCount = trueDistinctCount;
    }

    public void add(
        long inMemorySizeInBytes, long serializedSizeInBytes, double distinctCountEstimate) {
      count += 1;
      minimumInMemorySizeInBytes = Math.min(minimumInMemorySizeInBytes, inMemorySizeInBytes);
      maximumInMemorySizeInBytes = Math.max(maximumInMemorySizeInBytes, inMemorySizeInBytes);
      sumInMemorySizeInBytes += inMemorySizeInBytes;
      minimumSerializationSizeInBytes =
          Math.min(minimumSerializationSizeInBytes, serializedSizeInBytes);
      maximumSerializationSizeInBytes =
          Math.max(maximumSerializationSizeInBytes, serializedSizeInBytes);
      sumSerializationSizeInBytes += serializedSizeInBytes;
      double distinctCountEstimationError = distinctCountEstimate - trueDistinctCount;
      sumDistinctCountEstimationError += distinctCountEstimationError;
      sumDistinctCountEstimationErrorSquared +=
          distinctCountEstimationError * distinctCountEstimationError;
    }

    public double getAverageSerializationSizeInBytes() {
      return sumSerializationSizeInBytes / (double) count;
    }

    public double getAverageInMemorySizeInBytes() {
      return sumInMemorySizeInBytes / (double) count;
    }

    public double getRelativeEstimationBias() {
      return (sumDistinctCountEstimationError / count) / trueDistinctCount;
    }

    public double getRelativeEstimationRmse() {
      return Math.sqrt(sumDistinctCountEstimationErrorSquared / count) / trueDistinctCount;
    }

    public long getTrueDistinctCount() {
      return trueDistinctCount;
    }

    public long getMinimumInMemorySizeInBytes() {
      return minimumInMemorySizeInBytes;
    }

    public long getMaximumInMemorySizeInBytes() {
      return maximumInMemorySizeInBytes;
    }

    public long getMinimumSerializationSizeInBytes() {
      return minimumSerializationSizeInBytes;
    }

    public long getMaximumSerializationSizeInBytes() {
      return maximumSerializationSizeInBytes;
    }

    double getEstimatedInMemoryMVP() {
      return getAverageInMemorySizeInBytes()
          * 8.
          * sumDistinctCountEstimationErrorSquared
          / ((double) count * trueDistinctCount * trueDistinctCount);
    }

    double getEstimatedSerializationMVP() {
      return getAverageSerializationSizeInBytes()
          * 8.
          * sumDistinctCountEstimationErrorSquared
          / ((double) count * trueDistinctCount * trueDistinctCount);
    }
  }

  private static <T> void test(Config<T> config) {
    int p = 12;
    int numCycles = 10000;
    List<Statistics> statistics =
        LongStream.of(getDistinctCounts(1000000, 0.05)).mapToObj(Statistics::new).toList();

    SplittableRandom rng = new SplittableRandom(0);

    for (int i = 0; i < numCycles; ++i) {
      T sketch = config.create(p);

      int distinctCountsIdx = 0;
      long distinctCount = 0;
      while (true) {
        if (distinctCount == statistics.get(distinctCountsIdx).trueDistinctCount) {
          statistics
              .get(distinctCountsIdx)
              .add(
                  config.getInMemorySizeInBytes(sketch),
                  config.getSerializedSizeInBytes(sketch),
                  config.getEstimate(sketch, p));
          distinctCountsIdx += 1;
          if (distinctCountsIdx == statistics.size()) break;
        }
        config.add(sketch, rng.nextLong());
        distinctCount += 1;
      }
    }

    try (FileWriter o =
        new FileWriter(
            "../results/comparison-empirical-mvp/" + config.getLabel() + ".csv",
            StandardCharsets.UTF_8)) {

      o.write(
          "p = "
              + p
              + "; number of cycles = "
              + numCycles
              + "; data structure = "
              + config.getLabel()
              + '\n');
      o.write("true distinct count");
      o.write("; minimum memory size");
      o.write("; average memory size");
      o.write("; maximum memory size");
      o.write("; minimum serialization size");
      o.write("; average serialization size");
      o.write("; maximum serialization size");
      o.write("; relative distinct count estimation bias");
      o.write("; relative distinct count estimation rmse");
      o.write("; estimated memory MVP");
      o.write("; estimated serialization MVP");

      o.write('\n');
      for (Statistics s : statistics) {
        o.write(Long.toString(s.getTrueDistinctCount()));
        o.write("; " + s.getMinimumInMemorySizeInBytes());
        o.write("; " + s.getAverageInMemorySizeInBytes());
        o.write("; " + s.getMaximumInMemorySizeInBytes());
        o.write("; " + s.getMinimumSerializationSizeInBytes());
        o.write("; " + s.getAverageSerializationSizeInBytes());
        o.write("; " + s.getMaximumSerializationSizeInBytes());
        o.write("; " + s.getRelativeEstimationBias());
        o.write("; " + s.getRelativeEstimationRmse());
        o.write("; " + s.getEstimatedInMemoryMVP());
        o.write("; " + s.getEstimatedSerializationMVP());
        o.write('\n');
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(String[] args) {
    test(new Hash4jUltraLogLogMLConfig());
    test(new Hash4jUltraLogLogFGRAConfig());
    test(new Hash4jHyperLogLogMLConfig());
    test(new Hash4jHyperLogLogCRConfig());
    test(new ApacheDataSketchesCPCConfig());
    test(new ApacheDataSketchesHLL4Config());
    test(new ApacheDataSketchesHLL6Config());
    test(new ApacheDataSketchesHLL8Config());
    test(new ZetaSketchConfigDenseConfig());
    test(new ZetaSketchConfigSparseConfig());
  }
}
