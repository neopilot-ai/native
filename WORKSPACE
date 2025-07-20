workspace(name = "ai_native_systems")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Rules Python setup
http_archive(
    name = "rules_python",
    url = "https://github.com/bazelbuild/rules_python/releases/download/0.30.0/rules_python-0.30.0.tar.gz",
    sha256 = "b13a4a3c0efbcd3567f34035e6a29b4c343fd3d43a9b9e3c3b34342984e26bbd",
)

load("@rules_python//python:repositories.bzl", "py_repositories")
py_repositories()

load("@rules_python//python:pip.bzl", "pip_parse")
pip_parse(
    name = "pip_deps",
    requirements_lock = "//:requirements.txt",
)

load("@pip_deps//:requirements.bzl", "install_deps")
install_deps()
