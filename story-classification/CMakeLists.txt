CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

PROJECT( STORY_ANALYSIS )
set(TARGET TextAnalysis)

LINK_DIRECTORIES(${STORY_ANALYSIS_SOURCE_DIR}/lib)
INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR})

set(PROJECT_VERSION "0.1")
#set(ARCHIVE_NAME ${CMAKE_PROJECT_NAME}-${PROJECT_VERSION})
#add_custom_target(upload
#    COMMAND rsync *.cpp csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/
#    COMMAND rsync *.h csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/
#    COMMAND rsync CMakeList.txt csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/
#    COMMAND rsync wnb/ csa@ca:/home/csa/CAS2/hangqi/StoryTextInfo/wnb/
#    )
#add_custom_target(dist
#    COMMAND git archive --prefix=${ARCHIVE_NAME}/ HEAD
#        | bzip2 > ${CMAKE_BINARY_DIR}/${ARCHIVE_NAME}.tar.bz2
#    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

## Compiler flags
IF (CMAKE_COMPILER_IS_GNUCXX)
  list(APPEND CMAKE_CXX_FLAGS " -O3 -std=c++0x")
ENDIF()


set(SEG_SCR TextAnalysis.cpp classifier.cpp utility.cpp segmenter.cpp topic_model.h comatrix.cpp)

# executable
#--------------------------------------------------
add_executable (${TARGET} main.cpp ${SEG_SCR})
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR})
SET(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

ADD_SUBDIRECTORY(wnb)

target_link_libraries (${TARGET} wnb) 