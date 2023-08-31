//
// Copyright (c) 2023 Dynatrace LLC. All rights reserved.
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

import static java.util.Comparator.comparing;
import static java.util.Objects.requireNonNull;
import static java.util.stream.Collectors.joining;

import com.dynatrace.hash4j.distinctcount.HyperLogLog;
import com.dynatrace.hash4j.distinctcount.UltraLogLog;
import com.dynatrace.hash4j.random.PseudoRandomGenerator;
import com.dynatrace.hash4j.random.PseudoRandomGeneratorProvider;
import com.dynatrace.hash4j.util.PackedArray;
import java.io.ByteArrayOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.util.*;
import java.util.stream.IntStream;
import java.util.stream.LongStream;
import java.util.stream.Stream;
import org.apache.commons.compress.compressors.CompressorOutputStream;
import org.apache.commons.compress.compressors.bzip2.BZip2CompressorOutputStream;
import org.apache.commons.compress.compressors.deflate.DeflateCompressorOutputStream;
import org.apache.commons.compress.compressors.lzma.LZMACompressorOutputStream;
import org.apache.commons.compress.compressors.zstandard.ZstdCompressorOutputStream;

public class CompressionSimulation {

  private static final class Transition {
    private final BigInt distinctCount;
    private final long hash;

    public Transition(BigInt distinctCount, long hash) {
      this.distinctCount = distinctCount;
      this.hash = hash;
    }
  }

  private static final class Result {

    public Result(int configSize) {
      compressedBytes = new int[configSize];
    }

    private int[] compressedBytes;
  }

  private static final class Work {
    private HyperLogLog hll;
    private UltraLogLog ull;

    private byte[] hllExpanded;
    private final Transition[] transitions;
    private final int p;
    private final PseudoRandomGenerator prg;

    void reset(long seed, BigInt distinctCountOffset) {
      prg.reset(seed);
      hll.reset();
      ull.reset();
      int counter = 0;
      for (int nlz = 0; nlz <= 64 - p; ++nlz) {
        double factor = Math.pow(2., Math.min(64, 1 + p + nlz));
        for (int registerIdx = 0; registerIdx < (1 << p); ++registerIdx) {
          BigInt transitionDistinctCount = BigInt.floor(prg.nextExponential() * factor);
          transitionDistinctCount.increment(); // 1-based geometric distribution
          transitionDistinctCount.add(distinctCountOffset);
          long hash = ((long) registerIdx << -p) | (0x8000000000000000L >>> p >>> nlz);
          transitions[counter++] = new Transition(transitionDistinctCount, hash);
        }
      }
      Arrays.sort(transitions, comparing(transition -> transition.distinctCount));
    }

    void add(long hash) {
      hll.add(hash);
      ull.add(hash);
    }

    public Work(int p, PseudoRandomGenerator prg) {
      this.hll = HyperLogLog.create(p);
      this.ull = UltraLogLog.create(p);
      this.hllExpanded = new byte[1 << p];
      int transitionListLen = (1 << p) * (65 - p);
      this.transitions = new Transition[transitionListLen];
      this.p = p;
      this.prg = prg;
    }
  }

  private interface Selector {

    byte[] getState(byte[] hll6, byte[] hll8, byte[] ull);

    String getDescription();
  }

  private enum Selectors implements Selector {
    HLL6 {
      @Override
      public byte[] getState(byte[] hll6, byte[] hll8, byte[] ull) {
        return hll6;
      }

      @Override
      public String getDescription() {
        return "hll6";
      }
    },
    HLL8 {
      @Override
      public byte[] getState(byte[] hll6, byte[] hll8, byte[] ull) {
        return hll8;
      }

      @Override
      public String getDescription() {
        return "hll8";
      }
    },
    ULL {
      @Override
      public byte[] getState(byte[] hll6, byte[] hll8, byte[] ull) {
        return ull;
      }

      @Override
      public String getDescription() {
        return "ull";
      }
    };
  }

  private interface Compressor {

    int getCompressedSizeInBytes(byte[] data);

    String getDescription();
  }

  private abstract static class AbstractApacheCompressor implements Compressor {

    private static final ThreadLocal<ByteArrayOutputStream> BYTE_ARRAY_OUTPUT_STREAM_THREAD_LOCAL =
        ThreadLocal.withInitial(ByteArrayOutputStream::new);

    private final String description;

    public AbstractApacheCompressor(String description) {
      this.description = requireNonNull(description);
    }

    protected abstract CompressorOutputStream createCompressorOutputStream(
        final OutputStream outputStream, int dataSize) throws IOException;

    @Override
    public int getCompressedSizeInBytes(byte[] data) {
      ByteArrayOutputStream bos = BYTE_ARRAY_OUTPUT_STREAM_THREAD_LOCAL.get();
      bos.reset();
      try (CompressorOutputStream cos = createCompressorOutputStream(bos, data.length)) {
        cos.write(data, 0, data.length);
        cos.flush();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      return bos.size();
    }

    @Override
    public String getDescription() {
      return description;
    }
  }

  private static final Compressor LZMA_COMPRESSOR =
      new AbstractApacheCompressor("lzma") {
        @Override
        protected CompressorOutputStream createCompressorOutputStream(
            OutputStream outputStream, int dataSize) throws IOException {
          return new LZMACompressorOutputStream(outputStream);
        }
      };

  private static final Compressor DEFLATE_COMPRESSOR =
      new AbstractApacheCompressor("deflate") {
        @Override
        protected CompressorOutputStream createCompressorOutputStream(
            OutputStream outputStream, int dataSize) {
          return new DeflateCompressorOutputStream(outputStream);
        }
      };

  private static final Compressor ZSTD_COMPRESSOR =
      new AbstractApacheCompressor("zstd") {
        @Override
        protected CompressorOutputStream createCompressorOutputStream(
            OutputStream outputStream, int dataSize) throws IOException {
          return new ZstdCompressorOutputStream(outputStream);
        }
      };

  private static final Compressor BZIP2_COMPRESSOR =
      new AbstractApacheCompressor("bzip2") {
        @Override
        protected CompressorOutputStream createCompressorOutputStream(
            OutputStream outputStream, int dataSize) throws IOException {
          return new BZip2CompressorOutputStream(outputStream);
        }
      };

  private static final List<Compressor> COMPRESSORS =
      List.of(BZIP2_COMPRESSOR, LZMA_COMPRESSOR, DEFLATE_COMPRESSOR, ZSTD_COMPRESSOR);

  private static final class CompressionTestConfig {
    private final Compressor compressor;
    private final Selector selector;

    public CompressionTestConfig(Compressor compressor, Selector selector) {
      this.compressor = compressor;
      this.selector = selector;
    }

    public Compressor getCompressor() {
      return compressor;
    }

    public Selector getSelector() {
      return selector;
    }

    public String getHeader() {
      return "compressed bytes "
          + selector.getDescription()
          + " "
          + getCompressor().getDescription();
    }
  }

  private static final List<CompressionTestConfig> COMPRESSION_TEST_CONFIGS = createTestConfigs();

  private static List<CompressionTestConfig> createTestConfigs() {
    List<CompressionTestConfig> configs = new ArrayList<>();
    for (Selector selector : Selectors.values()) {
      for (Compressor compressor : COMPRESSORS) {
        configs.add(new CompressionTestConfig(compressor, selector));
      }
    }
    return configs;
  }

  public static void main(String[] args) {

    final String outputFile = args[0];
    final int p = Integer.parseInt(args[1]);
    final int sampleSize = 100;
    List<BigInt> targetDistinctCounts = TestUtils.getDistinctCountValues(1e21, 0.05);
    final BigInt largeScaleSimulationModeDistinctCountLimit = BigInt.fromLong(1000000);

    SplittableRandom seedRandom = new SplittableRandom(0xd722301e3c920bc8L);
    long[] seeds = seedRandom.longs(sampleSize).toArray();

    final List<List<Result>> results =
        Stream.generate(
                () ->
                    Stream.generate(() -> new Result(COMPRESSION_TEST_CONFIGS.size()))
                        .limit(sampleSize)
                        .toList())
            .limit(targetDistinctCounts.size())
            .toList();

    PseudoRandomGeneratorProvider prgProvider = PseudoRandomGeneratorProvider.splitMix64_V1();

    final ThreadLocal<Work> workData =
        ThreadLocal.withInitial(() -> new Work(p, prgProvider.create()));

    PackedArray.PackedArrayHandler packedArrayHandler = PackedArray.getHandler(6);

    IntStream.range(0, sampleSize)
        .parallel()
        .forEach(
            sampleIdx -> {
              Work work = workData.get();
              work.reset(seeds[sampleIdx], largeScaleSimulationModeDistinctCountLimit);

              final Transition[] transitions = work.transitions;

              BigInt trueDistinctCount = BigInt.createZero();
              int transitionIndex = 0;
              for (int distinctCountIndex = 0;
                  distinctCountIndex < targetDistinctCounts.size();
                  ++distinctCountIndex) {
                BigInt targetDistinctCount = targetDistinctCounts.get(distinctCountIndex);
                BigInt limit = targetDistinctCount.copy();
                limit.min(largeScaleSimulationModeDistinctCountLimit);

                while (trueDistinctCount.compareTo(limit) < 0) {
                  long hash = work.prg.nextLong();
                  work.add(hash);
                  trueDistinctCount.increment();
                }
                if (trueDistinctCount.compareTo(targetDistinctCount) < 0) {
                  while (transitionIndex < transitions.length
                      && transitions[transitionIndex].distinctCount.compareTo(targetDistinctCount)
                          <= 0) {
                    work.add(transitions[transitionIndex].hash);
                    transitionIndex += 1;
                  }
                  trueDistinctCount.set(targetDistinctCount);
                }

                for (int registerIdx = 0; registerIdx < (1 << p); ++registerIdx) {
                  work.hllExpanded[registerIdx] =
                      (byte) packedArrayHandler.get(work.hll.getState(), registerIdx);
                }

                Result result = results.get(distinctCountIndex).get(sampleIdx);

                for (int compressionConfigIdx = 0;
                    compressionConfigIdx < COMPRESSION_TEST_CONFIGS.size();
                    ++compressionConfigIdx) {
                  CompressionTestConfig compressionTestConfig =
                      COMPRESSION_TEST_CONFIGS.get(compressionConfigIdx);
                  byte[] state =
                      compressionTestConfig
                          .getSelector()
                          .getState(work.hll.getState(), work.hllExpanded, work.ull.getState());
                  result.compressedBytes[compressionConfigIdx] =
                      compressionTestConfig.getCompressor().getCompressedSizeInBytes(state);
                }
              }
            });

    try (FileWriter o = new FileWriter(outputFile)) {

      o.write("p = " + p + "; sample_size = " + sampleSize + '\n');
      o.write("true distinct count");
      o.write(
          COMPRESSION_TEST_CONFIGS.stream()
              .map(CompressionTestConfig::getHeader)
              .collect(joining("; ", "; ", "\n")));

      for (int distinctCountIdx = 0;
          distinctCountIdx < targetDistinctCounts.size();
          ++distinctCountIdx) {
        double distinctCount = targetDistinctCounts.get(distinctCountIdx).asDouble();

        long[] sumCompressedBytes = new long[COMPRESSION_TEST_CONFIGS.size()];
        for (int sampleIdx = 0; sampleIdx < sampleSize; ++sampleIdx) {
          Result r = results.get(distinctCountIdx).get(sampleIdx);
          for (int configIdx = 0; configIdx < COMPRESSION_TEST_CONFIGS.size(); ++configIdx) {
            sumCompressedBytes[configIdx] += r.compressedBytes[configIdx];
          }
        }

        double[] avgCompressedBytes =
            LongStream.of(sumCompressedBytes).mapToDouble(x -> x / (double) sampleSize).toArray();

        o.write(distinctCount + "");
        o.write(
            IntStream.range(0, COMPRESSION_TEST_CONFIGS.size())
                .mapToObj(configIdx -> Double.toString(avgCompressedBytes[configIdx]))
                .collect(joining("; ", "; ", "\n")));
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
