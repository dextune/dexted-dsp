cmake_minimum_required(VERSION 3.20)
project(DextedDSP VERSION 0.1.0 LANGUAGES CXX)
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
find_package(Boost 1.74 REQUIRED)
add_library(dexted_dsp SHARED cpp/src/c_api.cpp)
add_library(DextedDSP::dexted_dsp ALIAS dexted_dsp)
target_compile_features(dexted_dsp PUBLIC cxx_std_20)
target_compile_definitions(dexted_dsp PRIVATE DEXTED_DSP_BUILD)
target_include_directories(dexted_dsp PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/cpp/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
target_link_libraries(dexted_dsp PUBLIC Boost::headers)
set_target_properties(dexted_dsp PROPERTIES CXX_VISIBILITY_PRESET hidden VERSION ${PROJECT_VERSION} SOVERSION 0)
include(CTest)
if(BUILD_TESTING)
    add_executable(dexted_dsp_native_tests cpp/tests/test_biquad.cpp)
    target_link_libraries(dexted_dsp_native_tests PRIVATE dexted_dsp)
    add_test(NAME native_predicate COMMAND dexted_dsp_native_tests)
endif()
install(TARGETS dexted_dsp EXPORT DextedDSPTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY cpp/include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT DextedDSPTargets NAMESPACE DextedDSP:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DextedDSP)
configure_package_config_file(cpp/cmake/DextedDSPConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/DextedDSPConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DextedDSP)
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/DextedDSPConfigVersion.cmake
    VERSION ${PROJECT_VERSION} COMPATIBILITY SameMajorVersion)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/DextedDSPConfig.cmake
              ${CMAKE_CURRENT_BINARY_DIR}/DextedDSPConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/DextedDSP)
