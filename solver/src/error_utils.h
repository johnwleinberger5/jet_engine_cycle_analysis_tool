#pragma once

#include <spdlog/spdlog.h>
#include <stdexcept>
#include <string>

// Log at CRITICAL then throw. Templated so callers can throw invalid_argument,
// runtime_error, or any other std::exception subclass.
template <typename ExceptionT = std::runtime_error>
[[noreturn]] void log_and_throw(const std::string& function, const std::string& msg) {
    spdlog::critical("[{}] {}", function, msg);
    throw ExceptionT(msg);
}
