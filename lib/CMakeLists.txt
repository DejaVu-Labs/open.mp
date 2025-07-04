# Remove old Conan 1.x integration - dependencies now handled by conanfile.py
# Dependencies are found in the root CMakeLists.txt

if(BUILD_SERVER)
	if(BUILD_PAWN_COMPONENT)
		# PAWN runtime
		# ------------
		set(PAWN_RUNTIME_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/pawn/source/amx")
		add_library(pawn-runtime STATIC
			${PAWN_RUNTIME_SRC_DIR}/amx.c
			${PAWN_RUNTIME_SRC_DIR}/amxargs.c
			${PAWN_RUNTIME_SRC_DIR}/amxaux.c
			${PAWN_RUNTIME_SRC_DIR}/amxcons.c
			${PAWN_RUNTIME_SRC_DIR}/amxcore.c
			${PAWN_RUNTIME_SRC_DIR}/amxfile.c
			${PAWN_RUNTIME_SRC_DIR}/amxstring.c
			${PAWN_RUNTIME_SRC_DIR}/amxtime.c
			${PAWN_RUNTIME_SRC_DIR}/amxfloat.c
		)
		target_compile_options(pawn-runtime
			PRIVATE "-Wno-unused-function"
		)
		target_include_directories(pawn-runtime 
			PRIVATE ${PAWN_RUNTIME_SRC_DIR}
			INTERFACE "${PAWN_RUNTIME_SRC_DIR}/.."
		)

		include(CheckIncludeFile)
		check_include_file("unistd.h" HAVE_UNISTD_H)
		if(HAVE_UNISTD_H)
			target_compile_definitions(pawn-runtime PUBLIC -DHAVE_UNISTD_H)
		endif()
		check_include_file("inttypes.h" HAVE_INTTYPES_H)
		if(HAVE_INTTYPES_H)
			target_compile_definitions(pawn-runtime PUBLIC -DHAVE_INTTYPES_H)
		endif()
		check_include_file("stdint.h" HAVE_STDINT_H)
		if(HAVE_STDINT_H)
			target_compile_definitions(pawn-runtime PUBLIC -DHAVE_STDINT_H)
		endif()
		check_include_file("alloca.h" HAVE_ALLOCA_H)
		if(HAVE_ALLOCA_H)
			target_compile_definitions(pawn-runtime PUBLIC -DHAVE_ALLOCA_H)
		endif()

		if (MSVC)
			target_compile_definitions(pawn-runtime
				PRIVATE
						-D_CRT_SECURE_NO_WARNINGS
			)
		endif()

		target_compile_definitions(pawn-runtime
			PRIVATE
				-DOVERWRITE_AMX_REGISTER
				-DFLOATPOINT
				-DAMX_STRING_LIB
				-DsNAMEMAX=63
				-DPAWN_CELL_SIZE=32
				-DAMX_FILENO_CHECKS
				-DAMX_NODYNALOAD

				# Disable default amx_FindPublic implementation because we want our own more performant one
				# Also disable amx_Allot because we want to check if we have enough memory when we are passing data
				# Which is more than available memory, so instead of a crash, we let user know about it.
				AMX_ALIGN AMX_CLEANUP AMX_CLONE AMX_DEFCALLBACK AMX_FLAGS AMX_GETADDR
				AMX_INIT AMX_MEMINFO AMX_NAMELENGTH AMX_NATIVEINFO AMX_PUSHXXX
				AMX_RAISEERROR AMX_REGISTER AMX_SETCALLBACK AMX_SETDEBUGHOOK
				AMX_XXXNATIVES AMX_XXXPUBVARS AMX_XXXSTRING AMX_XXXTAGS AMX_XXXUSERDATA AMX_UTF8XXX
		)

		if(UNIX)
			# TODO: set fvisibility for gcc/clang
			target_compile_definitions(pawn-runtime PUBLIC -DLINUX)
			check_include_file("ffi.h" HAVE_FFI_H)
			target_include_directories(pawn-runtime PUBLIC "${PAWN_RUNTIME_SRC_DIR}/../linux")
			target_sources(pawn-runtime PRIVATE "${PAWN_RUNTIME_SRC_DIR}/../linux/getch.c")
		endif()

		if(WIN32)
			target_compile_definitions(pawn-runtime
				PRIVATE
					-D_CRT_SECURE_NO_WARNINGS
					-D_CRT_NONSTDC_NO_DEPRECATE
			)
			target_link_libraries(pawn-runtime PRIVATE winmm)
		endif()

		set_property(TARGET pawn-runtime PROPERTY FOLDER "lib")
		set_property(TARGET pawn-runtime PROPERTY POSITION_INDEPENDENT_CODE ON)
	endif()

if(BUILD_LEGACY_COMPONENTS)
# RakNet
# ------
add_subdirectory(RakNet)
set_property(TARGET raknet PROPERTY FOLDER "lib")
target_compile_options(raknet
	PRIVATE
		"-Wno-logical-op-parentheses"
		"-Wno-bitwise-op-parentheses"
		"-Wno-#pragma-messages"
)
endif()

# ttmath
# ------
add_subdirectory(ttmath)
GroupSourcesByFolder(ttmath)
set_property(TARGET ttmath PROPERTY FOLDER "lib")

endif()
