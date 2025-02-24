from cx_Freeze import setup, Executable

# Options pour inclure ModernGL et ses dépendances
options = {
    "build_exe": {
        "packages": ["glcontext"],
        "include_files": [],
        "include_msvcr": True,  # Inclure les DLL de Microsoft si nécessaire
    }
}

setup(
    name = "The lil prince",
    version = "1.0",
    author = "Aizeir",
    description = "",
    options=options,
    executables = [
        Executable("main.py", base="Win32GUI")
    ]
)