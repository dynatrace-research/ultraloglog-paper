// This file was taken and derived from 
// https://github.com/mkarppa/hyperlogloglog/tree/50670ae4d70b4f1164c94a6b7cc4b32e2bf70982.
//
// This file was originally published under the following license:
//
//
// MIT License
//
// Copyright (c) 2022 Matti Karppa
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#ifndef HYPERLOGLOGLOG_HYPERLOGLOG
#define HYPERLOGLOGLOG_HYPERLOGLOG

#include "common.hpp"
#include "PackedVector.hpp"
#include "Hash.hpp"
#include <cstdint>
#include <cmath>

namespace hyperlogloglog {
  /**
   * Basic HyperLogLog. The template parameter Word determines the
   * word type and length (that is, the length of the hashes).
   */
  template<typename Word = uint64_t>
  class HyperLogLog {
  public:
    /**
     * Basic constructor
     * m : the number of registers
     */
    explicit HyperLogLog(int m) :
      m(m), logW(log2i(sizeof(Word)*CHAR_BIT)),
      logM(log2i(m)), M(logW,m) {
    }

    

    /**
     * Returns the size of the sketch (the number of bits)
     */
    inline size_t bitSize() const {
      return M.bitSize();
    }



    /**
     * Adds a new element to the sketch
     */
    template<typename Object,
             typename XHashFun = decltype(farmhash<Object>),
             typename JHashFun = decltype(fibonacciHash<Word>)>
    inline void add(const Object& o, XHashFun h = farmhash<Object>,
                    JHashFun f = fibonacciHash<Word>) {
      static_assert(std::is_same<decltype(h(o)),Word>::value,
                    "Hash function type does not match the Word type of the class");
      addHash(h(o), f);
    }



    /**
     * Adds a new hash to the sketch. Potentially useful if a
     * different kind of hashing scheme is used outside the class.
     */
    template<typename JHashFun = decltype(fibonacciHash<Word>)>
    inline void addHash(Word x, JHashFun f = fibonacciHash<Word>) {
      static_assert(std::is_same<decltype(f(x,logM)),Word>::value,
                    "Hash function type does not match the Word type of the class");
      addJr(f(x,logM), rho(x));
    }



    /**
     * Adds the specific j and r values to the sketch. This may be
     * useful if full control is required of the hashing faculties.
     * j must satisfy 0 <= j < m but no checks are made
     * r must satisfy 0 <= r < log(word length) (64 for uint64_t) but no checks are made
     */
    inline void addJr(Word j, Word r) {
      Word r0 = M.get(j);
      if (r > r0)
        M.set(j, r);      
    }
    


    /**
     * Returns a vector that contains the register values
     */
    std::vector<uint8_t> exportRegisters() const {
      std::vector<uint8_t> v(m);
      for (int i = 0; i < m; ++i)
        v[i] = M.get(i);
      return v;
    }



    /**
     * Returns the present estimate
     */
    double estimate() const {
      double E = 0;
      int V = 0;
      for (int j = 0; j < m; ++j) {
        Word r = M.get(j);
        V += (r == 0);
        E += 1.0 / (1ull << r);
      }
      E = alpha(m) * m * m / E;
      if (E <= 5.0 / 2.0 * m && V != 0) {
        return m*log(static_cast<double>(m)/V);
      }
      else if (E <= (1ull << 32)/30) {
        return E;
      }
      else {
        return -(1ll << 32) * log(1-E/(1ll << 32));
      }
    }



    /**
     * Merges this sketch with the other sketch and returns a new sketch
     *
     * Note: if the sketches were constructed with different hash
     * functions, the result will be nonsensical. It is up to the
     * caller to ensure that the exact same hash functions were used.
     */
    HyperLogLog merge(const HyperLogLog& that) const {
      if (m != that.m)
        throw std::invalid_argument("Mismatch in the number of registers");
      HyperLogLog H(m);
      for (int j = 0; j < m; ++j)
        H.M.set(j, std::max(M.get(j), that.M.get(j)));
      return H;
    }

    
    
    /**
     * Returns the correction coefficient
     */
    static double alpha(int m) {
      switch(m) {
      case 16:
        return 0.673;
      case 32:
        return 0.697;
      case 64:
        return 0.709;
      default:
        return 0.7213 / (1.0 + 1.079/m);
      }
    }



    /**
     * Returns the number of registers
     */
    inline int getM() const {
      return m;
    }

    
  private:
    int m;
    int logW; // register length
    int logM; // register address length
    PackedVector<Word> M;
  };
}

#endif // HYPERLOGLOGLOG_HYPERLOGLOG
