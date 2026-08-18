cmake_minimum_required(VERSION 3.22)

project(iCloudLinuxPlasma LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Qt6 REQUIRED COMPONENTS Core DBus Qml)

add_library(icloudlinuxplugin SHARED
    plasma_plugin/backend_bridge.cpp
    plasma_plugin/backend_bridge.h
    plasma_plugin/icloudlinux_plugin.cpp
    plasma_plugin/icloudlinux_plugin.h
)

target_link_libraries(icloudlinuxplugin PRIVATE Qt6::Core Qt6::DBus Qt6::Qml)

install(TARGETS icloudlinuxplugin DESTINATION lib/qt6/qml/org/icloudlinux/backend)

install(FILES plasma_plugin/qmldir DESTINATION lib/qt6/qml/org/icloudlinux/backend)