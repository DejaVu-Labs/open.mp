from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Git
from conan.errors import ConanInvalidConfiguration
import os


class OpenMPConan(ConanFile):
    name = "openmp-server"
    version = "1.4.0"
    license = "Apache-2.0"
    url = "https://github.com/openmultiplayer/open.mp"
    description = "Open Multiplayer - An open source multiplayer modification for Grand Theft Auto: San Andreas"
    topics = ("gaming", "multiplayer", "sa-mp")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_server": [True, False],
        "build_pawn_component": [True, False],
        "build_unicode_component": [True, False],
        "build_legacy_components": [True, False],
        "build_test_components": [True, False],
        "build_sqlite_component": [True, False],
        "build_fixes_component": [True, False],
        "build_abi_check_tool": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_server": True,
        "build_pawn_component": True,
        "build_unicode_component": False,
        "build_legacy_components": True,
        "build_test_components": False,
        "build_sqlite_component": True,
        "build_fixes_component": True,
        "build_abi_check_tool": True,
    }

    # Binary configuration
    exports_sources = "CMakeLists.txt", "lib/*", "SDK/*", "Server/*", "Shared/*", "Tools/*", "cmake/*"
    
    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "apple-clang": "11",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            self.options.build_abi_check_tool = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and self.settings.compiler.version:
            if str(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        # Only Clang is officially supported
        if str(self.settings.compiler) not in ["clang", "apple-clang"]:
            if self.settings.os == "Windows" and "clang" not in str(self.settings.compiler):
                raise ConanInvalidConfiguration(
                    "Only Clang (or clang-cl on Windows) is officially supported for building."
                )

    def layout(self):
        cmake_layout(self, src_folder=".")

    def requirements(self):
        # Core dependencies
        self.requires("nlohmann_json/3.11.3")
        self.requires("openssl/1.1.1w")
        self.requires("cxxopts/3.2.0")
        
        if self.options.build_sqlite_component:
            self.requires("sqlite3/3.47.0")
            
        if self.options.build_unicode_component:
            self.requires("icu/75.1")
            
        if self.options.build_abi_check_tool:
            # libelfin is not available in conan-center, may need custom handling
            pass

    def build_requirements(self):
        # Build tools
        self.tool_requires("cmake/[>=3.19 <4]")
        if self.settings.os != "Windows":
            self.tool_requires("ninja/[>=1.10 <2]")

    def generate(self):
        # CMakeToolchain generates conan_toolchain.cmake
        tc = CMakeToolchain(self)
        
        # Map Conan options to CMake variables
        tc.variables["BUILD_SERVER"] = self.options.build_server
        tc.variables["BUILD_PAWN_COMPONENT"] = self.options.build_pawn_component
        tc.variables["BUILD_UNICODE_COMPONENT"] = self.options.build_unicode_component
        tc.variables["BUILD_LEGACY_COMPONENTS"] = self.options.build_legacy_components
        tc.variables["BUILD_TEST_COMPONENTS"] = self.options.build_test_components
        tc.variables["BUILD_SQLITE_COMPONENT"] = self.options.build_sqlite_component
        tc.variables["BUILD_FIXES_COMPONENT"] = self.options.build_fixes_component
        
        if self.settings.os == "Linux":
            tc.variables["BUILD_ABI_CHECK_TOOL"] = self.options.build_abi_check_tool
        
        # Set the C++ standard
        tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.variables["CMAKE_CXX_STANDARD_REQUIRED"] = True
        
        # Platform-specific settings
        if self.settings.os == "Windows":
            tc.variables["CMAKE_SYSTEM_VERSION"] = "10.0"
        
        tc.generate()
        
        # CMakeDeps generates Find<PackageName>.cmake files
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["open-mp-server"]
        
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "winmm", "shlwapi"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "dl", "rt"]
            
        self.cpp_info.set_property("cmake_file_name", "OpenMP")
        self.cpp_info.set_property("cmake_target_name", "OpenMP::Server")