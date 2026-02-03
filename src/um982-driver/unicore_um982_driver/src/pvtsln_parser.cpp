#include "unicore_um982_driver/pvtsln_data.hpp"
#include <sstream>
#include <vector>
#include <algorithm>
#include <iostream>

namespace unicore_um982_driver
{

// 辅助函数：安全地将字符串转为 double，如果是空串或者非法则返回 0.0
double safeStod(const std::string& str) {
    if (str.empty()) return 0.0;
    try {
        return std::stod(str);
    } catch (...) {
        return 0.0;
    }
}

// 辅助函数：安全地将字符串转为 int
int safeStoi(const std::string& str) {
    if (str.empty()) return 0;
    try {
        return std::stoi(str);
    } catch (...) {
        return 0;
    }
}

std::vector<std::string> splitString(const std::string& str, char delimiter)
{
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;
    
    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    // 处理末尾如果是分隔符的情况（虽然后面的逻辑不太依赖这个）
    if (!str.empty() && str.back() == delimiter) {
        tokens.push_back("");
    }
    
    return tokens;
}

bool parsePVTSLN(const std::string& line, PVTSLNData& data)
{
    // Reset data validity
    data.is_valid = false;
    
    // 1. 更加宽松的过滤：只要包含 PVTSLN 就算通过初筛
    if (line.find("PVTSLN") == std::string::npos) {
        return false;
    }
    
    try {
        std::string msg = line;

        size_t start_pos = msg.find('#');
        if (start_pos == std::string::npos) {
            std::cerr << "[Driver Error] No '#' found in message: " << msg << std::endl;
            return false; 
        }
        // 截取从 # 开始的有效数据，并去掉 '#' 本身
        msg = msg.substr(start_pos + 1);

        // 3. 去掉校验和 (*CRC)
        size_t checksum_pos = msg.find('*');
        if (checksum_pos != std::string::npos) {
            msg = msg.substr(0, checksum_pos);
        }
        
        // 4. 寻找分号 ';' 分割 Header 和 Body
        size_t semicolon_pos = msg.find(';');
        if (semicolon_pos == std::string::npos) {
            std::cerr << "[Driver Error] No semicolon ';' found in message: " << msg << std::endl;
            return false;
        }
        
        std::string header_part = msg.substr(0, semicolon_pos);
        std::string body_part = msg.substr(semicolon_pos + 1);
        
        // --- 解析 Header ---
        std::vector<std::string> header_fields = splitString(header_part, ',');
        
        // 这里的 9 是基于标准 PVTSLN 定义，但为了防止越界，我们做个检查
        if (header_fields.size() < 6) { 
            std::cerr << "[Driver Error] Header too short: " << header_part << std::endl;
            return false;
        }
        
        data.message_id = header_fields[0]; // 应该是 PVTSLN 或 PVTSLNA
        data.sequence_num = safeStoi(header_fields[1]);
        data.gnss_mode = header_fields[2];
        data.time_status = header_fields[3];
        data.week = safeStoi(header_fields[4]);
        data.time_of_week = safeStod(header_fields[5]);
        
        // --- 解析 Body ---
        std::vector<std::string> body_fields = splitString(body_part, ',');
        
        // 确保字段足够多。你之前的日志显示数据很长，所以这里降低一点门槛以防万一
        if (body_fields.size() < 12) {
            std::cerr << "[Driver Error] Body too short (" << body_fields.size() << "): " << body_part << std::endl;
            return false;
        }
        
        size_t field_idx = 0;  // size_t 是无符号类型，专门用来匹配 .size()
        
        // 使用 safeStod 防止因为空字段(,,)导致程序抛出异常而中断解析
        data.position_status = body_fields[field_idx++];
        data.heading = safeStod(body_fields[field_idx++]);
        data.latitude = safeStod(body_fields[field_idx++]);
        data.longitude = safeStod(body_fields[field_idx++]);
        data.altitude = safeStod(body_fields[field_idx++]);
        data.undulation = safeStod(body_fields[field_idx++]);
        data.velocity_north = safeStod(body_fields[field_idx++]);
        data.velocity_east = safeStod(body_fields[field_idx++]);
        
        // 跳过 Dual Antenna Status
        if (field_idx < body_fields.size()) {
             data.dual_antenna_status = body_fields[field_idx++];
        }
        
        // 双天线数据 (如果后面还有数据的话)
        if (field_idx + 4 < body_fields.size()) {
            data.dual_antenna_heading = safeStod(body_fields[field_idx++]);
            data.dual_antenna_latitude = safeStod(body_fields[field_idx++]);
            data.dual_antenna_longitude = safeStod(body_fields[field_idx++]);
            data.dual_antenna_altitude = safeStod(body_fields[field_idx++]);
        }
        
        // 卫星数量等信息 (按需解析，防止越界)
        if (field_idx < body_fields.size()) data.num_satellites_tracked = safeStoi(body_fields[field_idx++]);
        if (field_idx < body_fields.size()) data.num_satellites_used_l1 = safeStoi(body_fields[field_idx++]);
        if (field_idx < body_fields.size()) data.num_satellites_used_l2 = safeStoi(body_fields[field_idx++]);
        
        // Skip reserved field
        if (field_idx < body_fields.size()) field_idx++;

        // 标准差信息 (Sigma)
        if (field_idx < body_fields.size()) data.sigma_latitude = safeStod(body_fields[field_idx++]);
        if (field_idx < body_fields.size()) data.sigma_longitude = safeStod(body_fields[field_idx++]);
        if (field_idx < body_fields.size()) data.sigma_altitude = safeStod(body_fields[field_idx++]);
        
        data.timestamp = data.time_of_week;
        data.is_valid = true;
        
        // 调试打印：如果解析成功了，打印一条信息（只在调试时看，平时可以注释掉）
        std::cout << "Parsed OK: Lat=" << data.latitude << " Lon=" << data.longitude << std::endl;
        
        return true;
    }
    catch (const std::exception& e) {
        std::cerr << "[Driver Exception] Parsing error: " << e.what() << " | Raw: " << line << std::endl;
        data.is_valid = false;
        return false;
    }
}

} // namespace unicore_um982_driver