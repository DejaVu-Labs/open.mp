# ------------------------------------------------------------
# Stage 1: Build the server
# ------------------------------------------------------------
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

ENV CC=clang
ENV CXX=clang++

# Install build tools and Python for Conan
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        clang \
        lld \
        cmake \
        ninja-build \
        git \
        python3 \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Conan 2.x
RUN pip3 install --no-cache-dir conan==2.18.1

# Detect default profile once so subsequent commands use same settings
RUN conan profile detect --force && \
    echo "Detected Conan profile configured"

# Copy project sources
WORKDIR /workspace
COPY . /workspace

# Install dependencies and generate toolchain
RUN conan install . \
        --output-folder=build \
        --build=missing \
        -s compiler=clang \
        -s compiler.version=14 \
        -s compiler.libcxx=libstdc++11 \
        -s compiler.cppstd=gnu17

# Configure and build
RUN /bin/bash -c "\
    source $(find build -name conanbuild.sh -print -quit) && \
    cmake -B build \
          -G Ninja \
          -DCMAKE_TOOLCHAIN_FILE=$(find build -name conan_toolchain.cmake -print -quit) \
          -DCMAKE_BUILD_TYPE=Release \
          -DBUILD_ABI_CHECK_TOOL=OFF \
          -DBUILD_UNICODE_COMPONENT=OFF \
          -DTARGET_BUILD_ARCH=x86_64 && \
    cmake --build build -j$(nproc)"

# ------------------------------------------------------------
# Stage 2: Runtime image
# ------------------------------------------------------------
FROM ubuntu:22.04 AS runtime

# Install any required runtime libs (OpenSSL, stdlibc++)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libssl3 \
        libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built artifacts from builder stage
COPY --from=builder /workspace/build/Output/Release/Server/ /app/

# Default ports (adjust if needed)
EXPOSE 7777/udp 7777/tcp

# Configure entrypoint
ENTRYPOINT ["/app/omp-server"]