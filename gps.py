import pynmea2

attributes = {
    'BWC' : [
        'timestamp',
        'lat_next',
        'lat_next_direction',
        'lon_next',
        'lon_next_direction',
        'true_track',
        'true_track_sym',
        'mag_track',
        'mag_sym',
        'range_next',
        'range_unit',
        'waypoint_name'
    ],

    'GGA' : [
        'timestamp',
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'gps_qual',
        'num_sats',
        'horizontal_dil',
        'altitude',
        'altitude_units',
        'geo_sep',
        'geo_sep_units',
        'age_gps_data',
        'ref_station_id'
        ],


    'GLL' : [
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'timestamp',
        'status'
    ],

    'GSA' : [
        'mode',
        'mode_fix_type',
        'sv_id01',
        'sv_id02',
        'sv_id03',
        'sv_id04',
        'sv_id05',
        'sv_id06',
        'sv_id07',
        'sv_id08',
        'sv_id09',
        'sv_id10',
        'sv_id11',
        'sv_id12',
        'pdop',
        'hdop',
        'vdop'
    ],

    'GSV' : [
        'num_messages',
        'msg_num',
        'num_sv_in_view',
        'sv_prn_num_1',
        'elevation_deg_1',
        'azimuth_1',
        'snr_1',
        'sv_prn_num_2',
        'elevation_deg_2',
        'azimuth_2',
        'snr_2',
        'sv_prn_num_3',
        'elevation_deg_3',
        'azimuth_3',
        'snr_3',
        'sv_prn_num_4',
        'elevation_deg_4',
        'azimuth_4',
        'snr_4'
    ],

    'RMA' : [
        'data_status',
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'not_used_1',
        'not_used_2',
        'spd_over_grnd',
        'crse_over_grnd',
        'variation',
        'var_dir'
    ],

    'RMB' : [
        'status',
        'cross_track_error',
        'cte_correction_dir',
        'origin_waypoint_id',
        'dest_waypoint_id',
        'dest_lat',
        'dest_lat_dir',
        'dest_lon',
        'dest_lon_dir',
        'dest_range',
        'dest_true_bearing',
        'dest_velocity',
        'arrival_alarm'
    ],

    'RMC' : [
        'timestamp',
        'status',
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'spd_over_grnd',
        'true_course',
        'datestamp',
        'mag_variation',
        'mag_var_dir'
    ],

    'RTE': [
        'num_in_seq',
        'sen_num',
        'start_type',
        'active_route_id',
        'data'
    ],

    'TRF': [
        'timestamp',
        'date',
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'ele_angle',
        'num_iterations',
        'num_doppler_intervals',
        'update_dist',
        'sat_id',
        'data'
    ],

    'STN':['talker_id_num'],

    'VBW' :[
        'lon_water_spd',
        'trans_water_spd',
        'data_validity_water_spd',
        'lon_grnd_spd',
        'trans_grnd_spd',
        'data_validity_grnd_spd'
    ],

    'VTG' : [
        'true_track',
        'true_track_sym',
        'mag_track',
        'mag_track_sym',
        'spd_over_grnd_kts',
        'spd_over_grnd_kts_sym',
        'spd_over_grnd_kmph',
        'spd_over_grnd_kmph_sym'
    ],


    'WPL' : [
        'lat',
        'lat_dir',
        'lon',
        'lon_dir',
        'waypoint_id'
    ],

    'XTE' : [
        'warning_flag',
        'lock_flag',
        'cross_track_err_dist',
        'correction_dir',
        'dist_units'
    ],

    'ZDA' : [
        'timestamp',
        'day',
        'month',
        'year',
        'local_zone',
        'local_zone_minutes'
    ]

}


def nmea_to_dict(sentence):

    msg_type = sentence[3:6]

    attribute_lst = attributes[msg_type]
    msg = pynmea2.parse(sentence)

    msg_dict = {}
    for attr in attribute_lst:
        if hasattr(msg, attr):
            msg_dict[attr] = getattr(msg, attr)

    return msg_dict

