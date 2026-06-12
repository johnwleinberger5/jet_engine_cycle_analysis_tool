#include "engine_cycle.h"
#include "constants.h"

#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>

#include <fstream>
#include <iostream>
#include <string>
#include <filesystem>

using json = nlohmann::json;

// ---------------------------------------------------------------------------
// Logging setup
// ---------------------------------------------------------------------------

struct LogConfig {
    std::string level    = "DEBUG";
    std::string log_file = "";      // empty = stdout only
};

LogConfig load_log_config(const std::string& config_path) {
    LogConfig cfg;
    if (config_path.empty() || !std::filesystem::exists(config_path))
        return cfg;

    std::ifstream f(config_path);
    json j = json::parse(f);

    if (j.contains("log_level") && j["log_level"].is_string())
        cfg.level = j["log_level"].get<std::string>();
    if (j.contains("log_file") && j["log_file"].is_string())
        cfg.log_file = j["log_file"].get<std::string>();

    return cfg;
}

void init_logger(const LogConfig& cfg) {
    std::vector<spdlog::sink_ptr> sinks;
    sinks.push_back(std::make_shared<spdlog::sinks::stderr_color_sink_mt>());

    if (!cfg.log_file.empty())
        sinks.push_back(std::make_shared<spdlog::sinks::basic_file_sink_mt>(cfg.log_file, true));

    auto logger = std::make_shared<spdlog::logger>("engine", sinks.begin(), sinks.end());

    // Pattern: [date time] [level] [file:line] [function] message
    logger->set_pattern("[%Y-%m-%d %H:%M:%S] [%l] [%s:%#] [%!] %v");

    spdlog::level::level_enum lvl = spdlog::level::debug;
    if      (cfg.level == "INFO")     lvl = spdlog::level::info;
    else if (cfg.level == "WARNING")  lvl = spdlog::level::warn;
    else if (cfg.level == "ERROR")    lvl = spdlog::level::err;
    else if (cfg.level == "CRITICAL") lvl = spdlog::level::critical;

    logger->set_level(lvl);
    spdlog::set_default_logger(logger);

    spdlog::info("Logger initialised — level={}, file={}",
                 cfg.level, cfg.log_file.empty() ? "stderr" : cfg.log_file);
}

// ---------------------------------------------------------------------------
// CLI argument parsing — minimal, no third-party library needed
// ---------------------------------------------------------------------------

struct CliArgs {
    std::string config_path = "";
    std::string input_path  = "";   // empty = read from stdin
};

CliArgs parse_args(int argc, char* argv[]) {
    CliArgs args;
    for (int i = 1; i < argc; ++i) {
        std::string flag = argv[i];
        if ((flag == "--config" || flag == "-c") && i + 1 < argc)
            args.config_path = argv[++i];
        else if ((flag == "--input" || flag == "-i") && i + 1 < argc)
            args.input_path = argv[++i];
        else {
            std::cerr << "Unknown flag: " << flag << "\n";
            std::exit(1);
        }
    }
    return args;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main(int argc, char* argv[]) {
    CliArgs args = parse_args(argc, argv);

    // Config file: --config flag, then ./config.json, then hardcoded defaults
    std::string config_path = args.config_path;
    if (config_path.empty() && std::filesystem::exists("config.json"))
        config_path = "config.json";

    LogConfig log_cfg = load_log_config(config_path);
    init_logger(log_cfg);

    // Read input JSON from file or stdin
    std::string input_str;
    if (!args.input_path.empty()) {
        spdlog::debug("Reading input from file: {}", args.input_path);
        std::ifstream f(args.input_path);
        if (!f) {
            spdlog::critical("Cannot open input file: {}", args.input_path);
            return 1;
        }
        input_str.assign(std::istreambuf_iterator<char>(f), {});
    } else {
        spdlog::debug("Reading input from stdin");
        input_str.assign(std::istreambuf_iterator<char>(std::cin), {});
    }

    // Parse input JSON
    json input_json;
    try {
        input_json = json::parse(input_str);
    } catch (const json::parse_error& e) {
        spdlog::critical("Failed to parse input JSON: {}", e.what());
        return 1;
    }

    SolverInput solver_input;
    try {
        solver_input.mach        = input_json.at("mach").get<double>();
        solver_input.opr         = input_json.at("opr").get<double>();
        solver_input.tit_k       = input_json.at("tit_k").get<double>();
        solver_input.altitude_ft = input_json.at("altitude_ft").get<double>();
    } catch (const json::exception& e) {
        spdlog::critical("Missing required input field: {}", e.what());
        return 1;
    }

    // Run solver
    SolverOutput output;
    try {
        EngineCycle cycle(solver_input);
        output = cycle.run();
    } catch (const std::exception& e) {
        spdlog::critical("Solver failed: {}", e.what());
        return 1;
    }

    // Write output JSON to stdout
    json output_json;
    output_json["specific_thrust_n_per_kgs"] = output.specific_thrust_n_per_kgs;
    output_json["sfc_kg_per_s_per_n"]        = output.sfc_kg_per_s_per_n;
    output_json["t0_stations_k"]             = output.t0_stations_k;
    output_json["p0_stations_pa"]            = output.p0_stations_pa;

    std::cout << output_json.dump(2) << "\n";
    return 0;
}
