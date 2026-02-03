#ifndef UNICORE_UM982_DRIVER__PVTSLN_DATA_HPP_
#define UNICORE_UM982_DRIVER__PVTSLN_DATA_HPP_

#include <string>

namespace unicore_um982_driver
{

struct PVTSLNData
{
    // Header information
    std::string message_id;           // "PVTSLNA"
    int sequence_num;                 // 84 (sequence number)
    std::string gnss_mode;           // "GPS" 
    std::string time_status;         // "FINE"
    int week;                        // GPS week number
    double time_of_week;             // Time of week in milliseconds
    
    // Solution status and position
    std::string position_status;     // "SINGLE", "RTK_FIXED", "RTK_FLOAT", etc.
    double heading;                  // Heading in degrees
    double latitude;                 // Latitude in degrees
    double longitude;                // Longitude in degrees  
    double altitude;                 // Altitude in meters
    double undulation;               // Height of geoid above ellipsoid
    double velocity_north;           // North velocity in m/s
    double velocity_east;            // East velocity in m/s
    double velocity_up;              // Up velocity in m/s
    
    // Dual antenna position
    std::string dual_antenna_status; // Status of dual antenna solution
    double dual_antenna_heading;     // Dual antenna heading
    double dual_antenna_latitude;    // Dual antenna latitude
    double dual_antenna_longitude;   // Dual antenna longitude
    double dual_antenna_altitude;    // Dual antenna altitude
    
    // Satellite information
    int num_satellites_tracked;     // Number of satellites being tracked
    int num_satellites_used_l1;     // Number of L1 satellites used in solution
    int num_satellites_used_l2;     // Number of L2 satellites used in solution
    
    // Position accuracy
    double sigma_latitude;           // Standard deviation of latitude (m)
    double sigma_longitude;          // Standard deviation of longitude (m)
    double sigma_altitude;           // Standard deviation of altitude (m)
    
    // Velocity accuracy
    double sigma_velocity_north;     // Standard deviation of north velocity (m/s)
    double sigma_velocity_east;      // Standard deviation of east velocity (m/s)
    double sigma_velocity_up;        // Standard deviation of up velocity (m/s)
    
    // Additional fields
    double pdop;                     // Position dilution of precision
    double age_of_corrections;       // Age of differential corrections (seconds)
    
    // Timestamp when message was parsed
    double timestamp;
    
    // Message validity
    bool is_valid;
    
    // Constructor
    PVTSLNData() 
        : sequence_num(0)
        , week(0)
        , time_of_week(0.0)
        , heading(0.0)
        , latitude(0.0)
        , longitude(0.0)
        , altitude(0.0)
        , undulation(0.0)
        , velocity_north(0.0)
        , velocity_east(0.0)
        , velocity_up(0.0)
        , dual_antenna_heading(0.0)
        , dual_antenna_latitude(0.0)
        , dual_antenna_longitude(0.0)
        , dual_antenna_altitude(0.0)
        , num_satellites_tracked(0)
        , num_satellites_used_l1(0)
        , num_satellites_used_l2(0)
        , sigma_latitude(0.0)
        , sigma_longitude(0.0)
        , sigma_altitude(0.0)
        , sigma_velocity_north(0.0)
        , sigma_velocity_east(0.0)
        , sigma_velocity_up(0.0)
        , pdop(0.0)
        , age_of_corrections(0.0)
        , timestamp(0.0)
        , is_valid(false)
    {
    }
};

// Function to parse PVTSLN message
bool parsePVTSLN(const std::string& line, PVTSLNData& data);

} // namespace unicore_um982_driver

#endif // UNICORE_UM982_DRIVER__PVTSLN_DATA_HPP_
