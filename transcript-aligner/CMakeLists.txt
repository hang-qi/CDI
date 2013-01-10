cmake_minimum_required (VERSION 2.6)

project (ALIGNER)

# Initialize CXXFLAGS.
set(CMAKE_CXX_FLAGS                "-Wall -std=c++0x")
set(CMAKE_CXX_FLAGS_DEBUG          "-O0 -g")
set(CMAKE_CXX_FLAGS_MINSIZEREL     "-Os -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELEASE        "-O4 -DNDEBUG")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g")

# Compiler-specific C++11 activation.
if ("${CMAKE_CXX_COMPILER_ID}" MATCHES "GNU")
    execute_process(
        COMMAND ${CMAKE_CXX_COMPILER} -dumpversion OUTPUT_VARIABLE GCC_VERSION)
    if (NOT (GCC_VERSION VERSION_GREATER 4.4 OR GCC_VERSION VERSION_EQUAL 4.4))
        message(FATAL_ERROR "${PROJECT_NAME} requires g++ 4.4 or greater.")
    endif ()
elseif ("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
else ()
    message(FATAL_ERROR "Your C++ compiler does not support C++11.")
endif ()

# Add include directories.
include_directories(src/utils)
include_directories(inc)

# utilities
set (UTILS_SOURCE_DIR src/utils)
set (UTILS_SOURCES
    ${UTILS_SOURCE_DIR}/string_utility.cpp
    ${UTILS_SOURCE_DIR}/datetime_utility.cpp)
add_library(utility ${UTILS_SOURCES})

# Source Directories.
set (SOURCE_DIR src)

# Source files.
set (ALIGNER_SOURCES
    ${SOURCE_DIR}/person_detector.cpp
	${SOURCE_DIR}/aligner.cpp)

set (TARGET aligner)

# Executables.
add_executable(${TARGET} ${ALIGNER_SOURCES})
target_link_libraries(${TARGET} utility)