#!/usr/bin/env python3
"""CLI for the DC FP calc kernel.

JSON batch (preferred; QA re-runs this):
    python3 _calc/run.py <inputs.json>

Ad-hoc:
    python3 _calc/run.py hydrant --ps 70 --ph 55 --qf 1600 --q 900 --derate 0.9
    python3 _calc/run.py density-area --density 0.20 --area 2500 --area-increase 0.30 --hose 250
    python3 _calc/run.py pump-envelope --qr 750 --pr 40 --churn-frac 1.20 --qd 900 --suction-static 70 --ceiling 175
    python3 _calc/run.py hw --q 900 --c 100 --id 6.065 --length 200
    python3 _calc/run.py louver --cfm 12000 --face-fpm 500 --free-area-pct 45

Stdout is a stable transcript. Ends with TRANSCRIPT_OK. Exit 2 on bad inputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from formulas import CalcError, dispatch  # noqa: E402

USAGE = """\
usage:
  python3 _calc/run.py <inputs.json>
  python3 _calc/run.py hydrant --ps 70 --ph 55 --qf 1600 --q 900 [--derate 0.9]
  python3 _calc/run.py density-area --density 0.20 --area 2500 --area-increase 0.30 --hose 250
  python3 _calc/run.py pump-envelope --qr 750 --pr 40 --qd 900 --suction-static 70 [--churn-frac 1.20] [--ceiling 175]
  python3 _calc/run.py hw --q 900 --c 100 --id 6.065 --length 200
  python3 _calc/run.py louver --cfm 12000 --face-fpm 500 --free-area-pct 45

JSON batch is preferred. QA re-runs the same file. Exit 2 on bad inputs.
"""

META_KEYS = {"id", "op", "formula", "notes", "comment", "label"}

# step-dict aliases → formula kwargs
ALIASES = {
    "hazen_williams": {
        "q": "q_gpm",
        "q_gpm": "q_gpm",
        "c": "c",
        "c_factor": "c",
        "id": "d_in",
        "d_in": "d_in",
        "d": "d_in",
        "length": "length_ft",
        "length_ft": "length_ft",
        "l_ft": "length_ft",
        "l": "length_ft",
    },
    "density_area": {
        "density": "density_gpm_ft2",
        "density_gpm_ft2": "density_gpm_ft2",
        "area": "base_area_ft2",
        "base_area": "base_area_ft2",
        "base_area_ft2": "base_area_ft2",
        "area_increase": "area_increase",
        "hose": "hose_gpm",
        "hose_gpm": "hose_gpm",
        "duration": "duration_min",
        "duration_min": "duration_min",
    },
    "hydrant_supply": {
        "ps": "ps_psi",
        "ps_psi": "ps_psi",
        "ph": "ph_psi",
        "ph_psi": "ph_psi",
        "qf": "qf_gpm",
        "qf_gpm": "qf_gpm",
        "q": "q_gpm",
        "q_gpm": "q_gpm",
        "derate": "derate",
    },
    "pump_envelope": {
        "qr": "qr_gpm",
        "qr_gpm": "qr_gpm",
        "pr": "pr_psi",
        "pr_psi": "pr_psi",
        "qd": "qd_gpm",
        "qd_gpm": "qd_gpm",
        "churn_frac": "churn_frac",
        "churn_frac_max": "churn_frac_max",
        "nfpa_flow_cap": "nfpa_flow_cap",
        "fm_flow_cap": "fm_flow_cap",
        "p150_frac": "p150_frac",
        "suction_static": "suction_static_psi",
        "suction_static_psi": "suction_static_psi",
        "ceiling": "ceiling_psi",
        "ceiling_psi": "ceiling_psi",
    },
    "pipe_volume": {"segments": "segments"},
    "k_factor": {"k": "k", "p_psi": "p_psi", "q_gpm": "q_gpm", "density": "density", "area_ft2": "area_ft2", "min_p_psi": "min_p_psi"},
    "tapered_branch": {"k": "k", "p_end_psi": "p_end_psi", "c": "c", "segments": "segments", "min_head_psi": "min_head_psi"},
    "di_trip_to_water": {"v_gal": "v_gal", "q_fill_gpm": "q_fill_gpm", "t_detect_s": "t_detect_s", "t_release_s": "t_release_s", "t_exhaust_s": "t_exhaust_s", "limit_s": "limit_s", "basis": "basis", "edition": "edition", "system_type": "system_type"},
    "seismic_fp": {"sds": "sds", "ip": "ip", "wp": "wp", "z_over_h": "z_over_h", "r_mu": "r_mu", "car": "car", "rpo": "rpo", "ta_s": "ta_s", "at_grade": "at_grade"},
    "electric_overpressure": {"net_shutoff_psi": "net_shutoff_psi", "max_static_suction_psi": "max_static_suction_psi", "component_rating_psi": "component_rating_psi", "elevation_ft": "elevation_ft", "vs_set_psi": "vs_set_psi", "vs_variance_psi": "vs_variance_psi", "relief_credited": "relief_credited"},
    "diesel_derate": {"pump_bhp": "pump_bhp", "altitude_ft": "altitude_ft", "ambient_f": "ambient_f", "nameplate_hp": "nameplate_hp", "stepwise": "stepwise", "gear_loss_hp": "gear_loss_hp"},
    "brace_load": {"cp": "cp", "segments": "segments", "pipe": "pipe", "spacing_ft": "spacing_ft", "listed_capacity_lb": "listed_capacity_lb", "angle_deg": "angle_deg", "capacity_is_horizontal": "capacity_is_horizontal"},
    "cp_from_sds": {"sds": "sds", "attach_height_ratio": "attach_height_ratio", "apply_height_factor": "apply_height_factor"},
    "hose_duration": {"hazard": "hazard", "supervised": "supervised"},
    "dry_delivery_screen": {"segments": "segments", "q_fill_gpm": "q_fill_gpm", "qod": "qod", "t_detect_s": "t_detect_s", "t_release_s": "t_release_s", "t_exhaust_s": "t_exhaust_s", "limit_s": "limit_s", "basis": "basis", "system_type": "system_type", "edition": "edition", "declared_interlock": "declared_interlock"},
    "relief_check": {"net_shutoff_psi": "net_shutoff_psi", "max_static_suction_psi": "max_static_suction_psi", "component_rating_psi": "component_rating_psi", "elevation_adj_psi": "elevation_adj_psi", "edition": "edition"},
    "junction_balance": {"q_low_gpm": "q_low_gpm", "p_low_psi": "p_low_psi", "p_high_psi": "p_high_psi", "q_high_gpm": "q_high_gpm", "tol_psi": "tol_psi"},
    "loop_two_path": {k: k for k in ["q_total_gpm","d1_in","l1_ft","d2_in","l2_ft","c","c2","split_frac"]},
    "compressor_n2_sizing": {"systems": "systems", "t_min": "t_min"},
    "battery_standby": {"loads": "loads", "standby_h": "standby_h", "alarm_min": "alarm_min", "aging_factor": "aging_factor", "vendor_derate": "vendor_derate", "battery_ah": "battery_ah"},
    "cross_main_walk": {"c": "c", "branches": "branches", "segments": "segments", "tol_psi": "tol_psi"},
    "bor_demand_pressure": {"q_gpm": "q_gpm", "p_bor_psi": "p_bor_psi", "c": "c", "segments": "segments", "dz_ft": "dz_ft", "friction_allow_psi": "friction_allow_psi", "system": "system", "suction_residual_psi": "suction_residual_psi", "qr_gpm": "qr_gpm", "churn_frac": "churn_frac", "p150_frac": "p150_frac"},
    "air_setpoint_stack": {"system_air_psig": "system_air_psig", "trip_psig": "trip_psig", "low_air_switch_psig": "low_air_switch_psig", "high_air_switch_psig": "high_air_switch_psig", "release_psig": "release_psig", "trip_tol_psi": "trip_tol_psi", "margin_low_psi": "margin_low_psi", "margin_high_psi": "margin_high_psi", "table_a_min_psig": "table_a_min_psig", "max_pneumatic_psig": "max_pneumatic_psig", "pmd_cut_in_psig": "pmd_cut_in_psig", "pmd_cut_out_psig": "pmd_cut_out_psig", "held": "held"},
    "rated_pressure_select": {"q_demand_gpm": "q_demand_gpm", "p_net_demand_psi": "p_net_demand_psi", "qr_gpm": "qr_gpm", "churn_frac": "churn_frac", "p150_frac": "p150_frac", "pr_candidates_psi": "pr_candidates_psi"},
    "fus_rff": {"a_m2": "a_m2", "a": "a_m2", "area_m2": "a_m2", "c_construction": "c_construction", "c": "c_construction", "occupancy_factor": "occupancy_factor", "occupancy": "occupancy_factor", "sprinkler_credit": "sprinkler_credit", "sprinkler": "sprinkler_credit", "exposure_factor": "exposure_factor", "exposure": "exposure_factor", "edition": "edition"},
    "sprinkler_grid_coverage": {"room_length_ft": "room_length_ft", "room_width_ft": "room_width_ft", "branch_spacing_ft": "branch_spacing_ft", "head_spacing_ft": "head_spacing_ft", "n_branches": "n_branches", "heads_per_branch": "heads_per_branch", "branch_offset_ft": "branch_offset_ft", "head_offset_ft": "head_offset_ft", "max_spacing_ft": "max_spacing_ft", "max_area_ft2": "max_area_ft2", "max_wall_distance_ft": "max_wall_distance_ft", "min_spacing_ft": "min_spacing_ft", "edge_area_rule": "edge_area_rule", "wall_compare": "wall_compare", "length_ft": "room_length_ft", "width_ft": "room_width_ft"},
    "pipe_velocity": {"q_gpm": "q_gpm", "q": "q_gpm", "id_in": "id_in", "d_in": "id_in", "d": "id_in", "nominal": "nominal", "schedule": "schedule", "sch": "schedule", "limit_fps": "limit_fps", "limit_source": "limit_source"},
    "remote_area_rectangle": {"area_ft2": "area_ft2", "head_spacing_ft": "head_spacing_ft", "branch_spacing_ft": "branch_spacing_ft", "room_length_parallel_ft": "room_length_parallel_ft", "room_width_perp_ft": "room_width_perp_ft", "wall_offset_ft": "wall_offset_ft", "a_ft2": "area_ft2", "s_ft": "head_spacing_ft", "l_ft": "branch_spacing_ft"},
    "obscuration_sc": {"sh": "sh", "sh_target": "sh", "n_ports": "n_ports", "n": "n_ports", "unit": "unit", "sc": "sc", "sc_min": "sc_min"},
    "pump_net_at_q": {"qr_gpm": "qr_gpm", "qr": "qr_gpm", "pr_psi": "pr_psi", "pr": "pr_psi", "q_gpm": "q_gpm", "q": "q_gpm", "churn_frac": "churn_frac", "p150_frac": "p150_frac"},
    "brace_spacing_max": {"cp": "cp", "pipe": "pipe", "main_lb_per_ft": "main_lb_per_ft", "branch_lb_per_main_ft": "branch_lb_per_main_ft", "listed_capacity_lb": "listed_capacity_lb", "angle_deg": "angle_deg", "capacity_is_horizontal": "capacity_is_horizontal"},
    "air_fill_scfm": {"v_gal": "v_gal", "v": "v_gal", "volume_gal": "v_gal", "p_psig": "p_psig", "p": "p_psig", "t_min": "t_min", "t": "t_min"},
    "louver_free_area": {
        "cfm": "cfm",
        "face": "face_fpm",
        "face_fpm": "face_fpm",
        "free_area_pct": "free_area_pct",
        "pct": "free_area_pct",
    },
}

OP_CANON = {
    "hw": "hazen_williams",
    "hazen_williams": "hazen_williams",
    "hazen-williams": "hazen_williams",
    "density_area": "density_area",
    "density-area": "density_area",
    "hydrant": "hydrant_supply",
    "pump_envelope": "pump_envelope",
    "pump-envelope": "pump_envelope",
    "louver": "louver_free_area",
    "pipe_volume": "pipe_volume",
    "air_fill_scfm": "air_fill_scfm",
    "compressor_n2_sizing": "compressor_n2_sizing",
    "compressor-n2-sizing": "compressor_n2_sizing",
    "brace_spacing_max": "brace_spacing_max",
    "brace-spacing-max": "brace_spacing_max",
    "air_fill": "air_fill_scfm",
    "k_factor": "k_factor",
    "tapered_branch": "tapered_branch",
    "di_trip_to_water": "di_trip_to_water",
    "seismic_fp": "seismic_fp",
    "diesel_derate": "diesel_derate",
    "electric_overpressure": "electric_overpressure",
    "electric-overpressure": "electric_overpressure",
    "diesel-derate": "diesel_derate",
    "brace_load": "brace_load",
    "junction_balance": "junction_balance",
    "loop_two_path": "loop_two_path", "loop-two-path": "loop_two_path", "looped_main": "loop_two_path",
    "relief_check": "relief_check",
    "hose_duration": "hose_duration",
    "hose-duration": "hose_duration",
    "dry_delivery_screen": "dry_delivery_screen",
    "dry-delivery-screen": "dry_delivery_screen",
    "cp_from_sds": "cp_from_sds",
    "pump_net_at_q": "pump_net_at_q",
    "pump-net-at-q": "pump_net_at_q",
    "cross_main_walk": "cross_main_walk",
    "cross-main-walk": "cross_main_walk",
    "bor_demand_pressure": "bor_demand_pressure",
    "bor-demand-pressure": "bor_demand_pressure",
    "rated_pressure_screen": "bor_demand_pressure",
    "rated_pressure_select": "rated_pressure_select",
    "rated-pressure-select": "rated_pressure_select",
    "pump_rated_pressure": "rated_pressure_select",
    "air_setpoint_stack": "air_setpoint_stack",
    "air-setpoint-stack": "air_setpoint_stack",
    "pmd_margin_stack": "air_setpoint_stack",
    "battery_standby": "battery_standby",
    "battery-standby": "battery_standby",
    "fus_rff": "fus_rff",
    "fus-rff": "fus_rff",
    "fus_required_fire_flow": "fus_rff",
    "obscuration_sc": "obscuration_sc",
    "obscuration-sc": "obscuration_sc",
    "sc_sh_n": "obscuration_sc",
    "chamber_sensitivity": "obscuration_sc",
    "sprinkler_grid_coverage": "sprinkler_grid_coverage",
    "sprinkler-grid-coverage": "sprinkler_grid_coverage",
    "grid_coverage": "sprinkler_grid_coverage",
    "pipe_velocity": "pipe_velocity",
    "pipe-velocity": "pipe_velocity",
    "velocity": "pipe_velocity",
    "remote_area_rectangle": "remote_area_rectangle",
    "remote-area-rectangle": "remote_area_rectangle",
    "remote_area": "remote_area_rectangle",
}

# Canonical input keys per op, in print order (only those present).
INPUT_ORDER = {
    "hazen_williams": ["q_gpm", "c", "d_in", "length_ft"],
    "density_area": [
        "density_gpm_ft2",
        "base_area_ft2",
        "area_increase",
        "hose_gpm",
        "duration_min",
    ],
    "hydrant_supply": ["ps_psi", "ph_psi", "qf_gpm", "q_gpm", "derate"],
    "pump_envelope": [
        "qr_gpm",
        "pr_psi",
        "qd_gpm",
        "churn_frac",
        "churn_frac_max",
        "nfpa_flow_cap",
        "fm_flow_cap",
        "p150_frac",
        "suction_static_psi",
        "ceiling_psi",
    ],
    "louver_free_area": ["cfm", "face_fpm", "free_area_pct"],
    "pipe_volume": [],
    "k_factor": ["k", "p_psi", "q_gpm", "density", "area_ft2", "min_p_psi"],
    "tapered_branch": ["k", "p_end_psi", "c", "segments", "min_head_psi"],
    "di_trip_to_water": ["v_gal", "q_fill_gpm", "t_detect_s", "t_release_s", "t_exhaust_s", "limit_s", "basis", "edition", "system_type"],
    "seismic_fp": ["sds", "ip", "wp", "z_over_h", "r_mu", "car", "rpo", "ta_s", "at_grade"],
    "electric_overpressure": ["net_shutoff_psi", "max_static_suction_psi", "component_rating_psi", "elevation_ft", "vs_set_psi", "vs_variance_psi", "relief_credited"],
    "diesel_derate": ["pump_bhp", "altitude_ft", "ambient_f", "nameplate_hp", "stepwise", "gear_loss_hp"],
    "brace_load": ["cp", "segments", "pipe", "spacing_ft", "listed_capacity_lb", "angle_deg", "capacity_is_horizontal"],
    "cp_from_sds": ["sds", "attach_height_ratio", "apply_height_factor"],
    "hose_duration": ["hazard", "supervised"],
    "dry_delivery_screen": ["q_fill_gpm", "qod", "t_detect_s", "t_release_s", "t_exhaust_s", "limit_s", "basis", "system_type", "edition", "declared_interlock"],
    "relief_check": ["net_shutoff_psi", "max_static_suction_psi", "component_rating_psi", "elevation_adj_psi"],
    "junction_balance": ["q_low_gpm", "p_low_psi", "p_high_psi", "q_high_gpm", "tol_psi"],
    "loop_two_path": ["q_total_gpm","d1_in","l1_ft","d2_in","l2_ft","c","c2","split_frac"],
    "air_fill_scfm": ["v_gal", "p_psig", "t_min"],
    "compressor_n2_sizing": ["systems", "t_min"],
    "brace_spacing_max": ["cp", "pipe", "main_lb_per_ft"],
    "cross_main_walk": ["c", "branches", "segments", "tol_psi"],
    "battery_standby": ["standby_h", "alarm_min", "aging_factor", "vendor_derate", "battery_ah"],
    "bor_demand_pressure": ["q_gpm", "p_bor_psi", "c", "segments", "dz_ft", "friction_allow_psi", "system", "suction_residual_psi", "qr_gpm", "churn_frac", "p150_frac"],
    "rated_pressure_select": ["q_demand_gpm", "p_net_demand_psi", "qr_gpm", "churn_frac", "p150_frac", "pr_candidates_psi"],
    "air_setpoint_stack": ["system_air_psig", "trip_psig", "low_air_switch_psig", "high_air_switch_psig", "release_psig", "trip_tol_psi", "margin_low_psi", "margin_high_psi", "table_a_min_psig", "max_pneumatic_psig", "pmd_cut_in_psig", "pmd_cut_out_psig", "held"],
    "pump_net_at_q": ["qr_gpm", "pr_psi", "q_gpm", "churn_frac", "p150_frac"],
    "fus_rff": ["a_m2", "c_construction", "occupancy_factor", "sprinkler_credit", "exposure_factor", "edition"],
    "obscuration_sc": ["sh", "n_ports", "unit", "sc", "sc_min"],
    "sprinkler_grid_coverage": ["room_length_ft", "room_width_ft", "branch_spacing_ft", "head_spacing_ft", "n_branches", "heads_per_branch", "branch_offset_ft", "head_offset_ft", "max_spacing_ft", "max_area_ft2", "max_wall_distance_ft", "min_spacing_ft", "edge_area_rule", "wall_compare"],
    "pipe_velocity": ["q_gpm", "id_in", "nominal", "schedule", "limit_fps", "limit_source"],
    "remote_area_rectangle": ["area_ft2", "head_spacing_ft", "branch_spacing_ft", "room_length_parallel_ft", "room_width_perp_ft", "wall_offset_ft"],
}

OUTPUT_ORDER = {
    "hazen_williams": ["p_psi", "hf_ft", "psi_per_ft_water"],
    "density_area": [
        "design_area_ft2",
        "q_spr_gpm",
        "hose_gpm",
        "qd_gpm",
        "duration_min",
        "gallons",
        "gallons_note",
    ],
    "hydrant_supply": ["p_raw_psi", "p_derated_psi"],
    "pump_envelope": [
        "min_qr_fm_gpm",
        "min_qr_nfpa_gpm",
        "qd_over_qr",
        "churn_net_pref_psi",
        "churn_net_max_psi",
        "p150_min_psi",
        "q150_gpm",
        "churn_system_pref_psi",
        "churn_system_max_psi",
        "ceiling_psi",
        "p_net_qd_psi",
        "qd_le_fm_cap",
        "qd_le_nfpa_cap",
        "churn_system_pref_le_ceiling",
        "churn_system_max_le_ceiling",
        "interpolation_applied",
        "interpolation",
    ],
    "louver_free_area": ["free_area_ft2", "gross_area_ft2"],
    "pipe_volume": ["segments_detail", "volume_gal", "volume_ft3"],
    "k_factor": ["q_gpm", "p_psi", "q_req_gpm", "k_si", "min_p_psi", "floor_governs"],
    "tapered_branch": ["nodes_detail", "q_inlet_gpm", "p_inlet_psi", "k_equiv_inlet", "end_head_ok"],
    "di_trip_to_water": ["t_fill_s", "t_total_s", "limit_s", "limit_basis", "margin_s", "passes_screen", "v_max_gal_at_limit", "edition", "nfpa_table_cite", "note_60s_option", "system_type_default_warning"],
    "seismic_fp": ["hf", "r_mu_used", "fp_raw", "fp_min", "fp_max", "fp", "fp_over_wp"],
    "electric_overpressure": ["elevation_adj_psi", "churn_max_psi", "component_rating_psi", "churn_ok_4771", "churn_margin_psi", "vs_max_psi", "vs_ok_47732", "vs_margin_psi", "relief_credited", "compliant", "compliance_path", "basis"],
    "diesel_derate": ["alt_deduction_pct", "temp_deduction_pct", "total_deduction_pct", "derate_factor", "required_engine_hp", "nameplate_hp", "derated_hp", "engine_ok", "deficit_hp", "basis"],
    "brace_load": ["segments_detail", "w_pipe_lb", "wp_lb", "fpw_lb", "pipe_fpw_max_lb", "pipe_ok", "capacity_is_horizontal", "angle_divisor", "brace_cap_lb", "brace_ok"],
    "cp_from_sds": ["cp_base", "height_factor", "cp"],
    "hose_duration": ["hose_total_gpm", "duration_min", "duration_range_min", "supervised"],
    "dry_delivery_screen": ["volume_gal", "system_type", "qod", "nfpa_size_cap_gal", "nfpa_size_threshold_gal", "nfpa_delivery_time_exempt", "nfpa_basis", "edition", "note_60s_option", "nfpa_table_cite", "t_fill_s", "t_total_s", "limit_s", "limit_basis", "margin_s", "passes_screen", "v_max_gal_at_limit", "declared_interlock", "qod_750_cap_basis", "warning"],
    "relief_check": ["relief_check_psi", "component_rating_psi", "relief_valve_required", "margin_psi"],
    "junction_balance": ["k_equiv", "q_low_adjusted_gpm", "q_total_gpm", "p_carried_psi", "delta_p_psi", "within_tolerance"],
    "loop_two_path": ["mode","q1_gpm","q2_gpm","p1_psi","p2_psi","p_governing_psi","equal_split_p1_psi","equal_split_p2_psi","equal_split_governing_psi","basis"],
    "compressor_n2_sizing": ["largest_system_id", "compressor_scfm_gauge", "compressor_scfm_abs", "n2_campus_scfm_gauge", "n2_campus_scfm_abs", "connected_v_gal"],
    "brace_spacing_max": ["max_spacing_ft", "any_pass", "brace_cap_lb", "rows"],
    "air_fill_scfm": ["scfm_gauge_basis", "scfm_abs_basis", "free_air_scf_gauge"],
    "battery_standby": ["rows", "standby_ma_total", "alarm_ma_total", "standby_ah", "alarm_ah", "aging_factor", "ah_required", "ah_required_vendor_derated", "battery_ah", "battery_ok", "margin_ah", "basis"],
    "cross_main_walk": ["rows", "tees", "q_total_gpm", "p_inlet_psi", "all_tees_within_tolerance", "basis"],
    "bor_demand_pressure": ["rows", "friction_psi", "elevation_psi", "allowance_psi", "p_discharge_required_psi", "p_net_required_psi", "envelope_segment", "envelope_factor", "rated_pressure_floor_psi", "lump_allowance_flag", "basis"],
    "air_setpoint_stack": ["t_worst_psi", "bands", "code_pass", "maker_pass", "all_pass", "needs_pe", "tags", "notes", "basis"],
    "rated_pressure_select": ["rows", "rated_pressure_floor_psi", "selected_pr_psi", "envelope_factor", "feasible", "meets_demand", "any_feasible", "basis"],
    "pump_net_at_q": ["churn_net_psi", "p150_net_psi", "q150_gpm", "rows", "p_net_psi", "all_within_150", "basis"],
    "fus_rff": ["edition", "a_m2", "c_construction", "construction_type_2020", "occupancy_factor", "sprinkler_credit", "exposure_factor", "f0_raw_lpm", "f0_rounded_lpm", "e_occupancy_lpm", "e_floor_applied", "sprinkler_reduction_lpm", "exposure_addition_lpm", "h_raw_lpm", "h_clamped_lpm", "rff_lpm", "rff_gpm_us", "duration_h", "duration_note", "volume_m3", "clamp_status", "basis"],
    "obscuration_sc": ["sh", "n_ports", "unit", "sc_max", "sc_req_max", "sc", "sh_eff", "passes_sc", "sc_min", "n_max_at_sc_min", "passes_n", "gap_b33r8_1", "port_layout", "basis"],
    "sprinkler_grid_coverage": ["n_heads", "area_per_head_ft2", "edge_area_per_head_ft2_v", "edge_area_ok", "edge_area_rule", "wall_compare", "max_directional_spacing_ft", "x_last_branch_ft", "y_last_head_ft", "wall_x0_ft", "wall_x1_ft", "wall_y0_ft", "wall_y1_ft", "max_wall_dist_actual_ft", "covered_x_ft", "covered_y_ft", "uncovered_x_ft", "uncovered_y_ft", "coverage_x_pct", "coverage_y_pct", "spacing_ok", "area_ok", "coverage_ok", "wall_ok", "min_spacing_ok", "passes", "fail_reasons", "basis"],
    "pipe_velocity": ["v_fps", "q_gpm", "id_in", "nominal", "schedule", "id_source", "k_const", "k_const_derived", "flow_area_in2", "limit_fps", "limit_source", "v_minus_limit_fps", "v_over_limit", "nfpa13_cite", "friction_method_note", "basis"],
    "remote_area_rectangle": ["sqrt_a_ft", "required_length_parallel_ft", "heads_per_branch_raw", "heads_per_branch_v", "length_provided_parallel_ft_v", "area_per_head_ft2", "n_heads_raw", "n_heads_v", "n_branches_v", "heads_on_last_branch_v", "width_perp_ft_v", "heads_area_ft2_v", "rectangle_area_ft2_v", "room_length_parallel_ft", "heads_fit_parallel", "spacings_fit_parallel", "heads_fit_parallel_basis", "heads_fit_parallel_warning", "wall_offset_ft", "length_between_end_heads_ft", "shortfall_parallel_ft", "room_short_parallel", "room_width_perp_ft", "room_narrow_perp", "fits_room", "both_sides_of_cross_main", "warnings", "elects_remote_area", "basis"],
}

UNITS = {
    "q_gpm": "gpm",
    "c": "—",
    "d_in": "in",
    "length_ft": "ft",
    "p_psi": "psi",
    "hf_ft": "ft",
    "psi_per_ft_water": "psi/ft",
    "density_gpm_ft2": "gpm/ft2",
    "base_area_ft2": "ft2",
    "area_increase": "—",
    "hose_gpm": "gpm",
    "duration_min": "min",
    "design_area_ft2": "ft2",
    "q_spr_gpm": "gpm",
    "qd_gpm": "gpm",
    "gallons": "gal",
    "ps_psi": "psi",
    "ph_psi": "psi",
    "qf_gpm": "gpm",
    "derate": "—",
    "p_raw_psi": "psi",
    "p_derated_psi": "psi",
    "qr_gpm": "gpm",
    "pr_psi": "psi",
    "churn_frac": "—",
    "churn_frac_max": "—",
    "nfpa_flow_cap": "—",
    "fm_flow_cap": "—",
    "p150_frac": "—",
    "suction_static_psi": "psi",
    "ceiling_psi": "psi",
    "min_qr_fm_gpm": "gpm",
    "min_qr_nfpa_gpm": "gpm",
    "qd_over_qr": "—",
    "churn_net_pref_psi": "psi",
    "churn_net_max_psi": "psi",
    "p150_min_psi": "psi",
    "q150_gpm": "gpm",
    "churn_system_pref_psi": "psi",
    "churn_system_max_psi": "psi",
    "p_net_qd_psi": "psi",
    "cfm": "cfm",
    "face_fpm": "fpm",
    "free_area_pct": "%",
    "free_area_ft2": "ft2",
    "gross_area_ft2": "ft2",
    "volume_gal": "gal",
    "volume_ft3": "ft3",
    "v_gal": "gal",
    "p_psig": "psig",
    "t_min": "min",
    "scfm_gauge_basis": "scfm",
    "scfm_abs_basis": "scfm",
    "free_air_scf_gauge": "scf",
}


def fmt_num(value: Any) -> str:
    """Round to 4 decimal places unless the value is integer."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        r = round(value, 4)
        if abs(r - round(r)) < 1e-12:
            return str(int(round(r)))
        return f"{r:.4f}"
    if value is None:
        return "n/a"
    return str(value)


def _unit(key: str) -> str:
    u = UNITS.get(key)
    if not u or u == "—":
        return ""
    return f" {u}"


def _print_kv(key: str, value: Any, indent: str = "  ") -> None:
    if isinstance(value, (list, tuple)) and key == "q_gpm":
        inner = ", ".join(fmt_num(v) for v in value)
        print(f"{indent}{key}: [{inner}] gpm")
        return
    print(f"{indent}{key}: {fmt_num(value)}{_unit(key)}")


def emit_step(
    step_id: str,
    op_canon: str,
    inputs: dict[str, Any],
    result: dict[str, Any],
) -> None:
    formula = result.get("formula", op_canon)
    print(f"--- step {step_id}  op={op_canon}  formula={formula} ---")
    print("inputs")
    for key in INPUT_ORDER.get(op_canon, inputs.keys()):
        if key in inputs and inputs[key] is not None:
            _print_kv(key, inputs[key])
    print("outputs")
    if op_canon == "hydrant_supply" and result.get("table"):
        print("  table")
        print("    q_gpm  p_raw_psi  p_derated_psi")
        for row in result["rows"]:
            q = fmt_num(row["q_gpm"])
            raw = fmt_num(row["p_raw_psi"])
            if "p_derated_psi" in row:
                der = fmt_num(row["p_derated_psi"])
                print(f"    {q}  {raw} psi  {der} psi")
            else:
                print(f"    {q}  {raw} psi")
        if result.get("derate") is not None:
            print(f"  derate: {fmt_num(result['derate'])}")
        return
    for key in OUTPUT_ORDER.get(op_canon, []):
        if key in result:
            _print_kv(key, result[key])


def _canon_op(op: str) -> str:
    key = (op or "").strip().lower()
    if key not in OP_CANON:
        raise CalcError(
            f"unknown op {op!r}; want one of: hw, density-area, hydrant, "
            "pump-envelope, louver"
        )
    return OP_CANON[key]


def _alias_inputs(op_canon: str, raw: dict[str, Any]) -> dict[str, Any]:
    aliases = ALIASES[op_canon]
    out: dict[str, Any] = {}
    unknown = []
    for k, v in raw.items():
        if k in META_KEYS:
            continue
        lk = str(k).strip()
        if lk in aliases:
            out[aliases[lk]] = v
        elif lk in aliases.values():
            out[lk] = v
        else:
            unknown.append(k)
    if unknown:
        raise CalcError(
            f"unknown field(s) for {op_canon}: {', '.join(str(u) for u in unknown)}"
        )
    return out


def _resolve_refs(step: dict[str, Any], done: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Step references: a string value "@<step_id>.<key>[.<key>...]" is
    replaced by that earlier step's output. Only earlier steps can be referenced."""
    out: dict[str, Any] = {}
    for k, v in step.items():
        if k in ("id", "op") or not (isinstance(v, str) and v.startswith("@")):
            out[k] = v
            continue
        sid, _, path = v[1:].partition(".")
        if sid not in done:
            raise CalcError(f"step reference {v!r}: no earlier step {sid!r}")
        cur: Any = done[sid]
        for part in path.split(".") if path else []:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                raise CalcError(f"step reference {v!r}: key {part!r} not found")
        out[k] = cur
    return out


def run_steps(job: str, notes: Optional[str], steps: list[dict[str, Any]]) -> None:
    computed = []
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise CalcError(f"step {i} is not an object")
        step_id = str(step.get("id") or f"s{i+1}")
        op_canon = _canon_op(str(step.get("op") or ""))
        step = _resolve_refs(step, {sid: res for sid, _o, _i, res in computed})
        inputs = _alias_inputs(op_canon, step)
        result = dispatch(op_canon, inputs)
        computed.append((step_id, op_canon, inputs, result))

    print("CALC KERNEL TRANSCRIPT")
    print(f"job: {job}")
    if notes:
        print(f"notes: {notes}")
    print(f"steps: {len(computed)}")
    print()
    for step_id, op_canon, inputs, result in computed:
        emit_step(step_id, op_canon, inputs, result)
        print()
    print("TRANSCRIPT_OK")


def _parse_q_list(values: list[str]) -> Any:
    """Accept `--q 900` or `--q 0 750 900` or `--q 0,750,900`."""
    nums: list[float] = []
    for v in values:
        for part in str(v).split(","):
            part = part.strip()
            if not part:
                continue
            nums.append(float(part))
    if not nums:
        raise CalcError("q_gpm is required")
    if len(nums) == 1:
        return nums[0]
    return nums


def cmd_json(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR: JSON root must be an object", file=sys.stderr)
        return 2
    job = data.get("job") or path.stem
    notes = data.get("notes")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        print("ERROR: JSON must have a non-empty 'steps' array", file=sys.stderr)
        return 2
    try:
        run_steps(str(job), notes if notes else None, steps)
    except CalcError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except TypeError as exc:
        print(f"ERROR: missing or extra input: {exc}", file=sys.stderr)
        return 2
    return 0


def build_subparsers() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run.py", add_help=False)
    sub = p.add_subparsers(dest="cmd")

    h = sub.add_parser("hydrant", add_help=False)
    h.add_argument("--ps", type=float, required=True)
    h.add_argument("--ph", type=float, required=True)
    h.add_argument("--qf", type=float, required=True)
    h.add_argument("--q", nargs="+", required=True)
    h.add_argument("--derate", type=float, default=None)

    d = sub.add_parser("density-area", add_help=False)
    d.add_argument("--density", type=float, required=True)
    d.add_argument("--area", type=float, required=True)
    d.add_argument("--area-increase", type=float, default=0.0)
    d.add_argument("--hose", type=float, default=0.0)
    d.add_argument("--duration", type=float, default=None)

    e = sub.add_parser("pump-envelope", add_help=False)
    e.add_argument("--qr", type=float, required=True)
    e.add_argument("--pr", type=float, required=True)
    e.add_argument("--qd", type=float, required=True)
    e.add_argument("--churn-frac", type=float, default=1.20)
    e.add_argument("--churn-frac-max", type=float, default=1.40)
    e.add_argument("--qd-nfpa-cap", dest="nfpa_flow_cap", type=float, default=1.50)
    e.add_argument("--fm-flow-cap", type=float, default=1.40)
    e.add_argument("--p150-frac", type=float, default=0.65)
    e.add_argument("--suction-static", type=float, required=True)
    e.add_argument("--ceiling", type=float, default=175.0)

    w = sub.add_parser("hw", add_help=False)
    w.add_argument("--q", type=float, required=True)
    w.add_argument("--c", type=float, required=True)
    w.add_argument("--id", type=float, required=True)
    w.add_argument("--length", type=float, required=True)

    L = sub.add_parser("louver", add_help=False)
    L.add_argument("--cfm", type=float, required=True)
    L.add_argument("--face-fpm", type=float, required=True)
    L.add_argument("--free-area-pct", type=float, required=True)
    return p


def cmd_adhoc(argv: list[str]) -> int:
    parser = build_subparsers()
    try:
        args, extra = parser.parse_known_args(argv)
    except SystemExit:
        print(USAGE, file=sys.stderr)
        return 2
    if extra:
        print(f"ERROR: unrecognized arguments: {' '.join(extra)}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    cmd = args.cmd
    try:
        if cmd == "hydrant":
            q = _parse_q_list(args.q)
            step = {
                "id": "hydrant",
                "op": "hydrant",
                "ps_psi": args.ps,
                "ph_psi": args.ph,
                "qf_gpm": args.qf,
                "q_gpm": q,
                "derate": args.derate,
            }
        elif cmd == "density-area":
            step = {
                "id": "density_area",
                "op": "density_area",
                "density_gpm_ft2": args.density,
                "base_area_ft2": args.area,
                "area_increase": args.area_increase,
                "hose_gpm": args.hose,
            }
            if args.duration is not None:
                step["duration_min"] = args.duration
        elif cmd == "pump-envelope":
            step = {
                "id": "pump_envelope",
                "op": "pump_envelope",
                "qr_gpm": args.qr,
                "pr_psi": args.pr,
                "qd_gpm": args.qd,
                "churn_frac": args.churn_frac,
                "churn_frac_max": args.churn_frac_max,
                "nfpa_flow_cap": args.nfpa_flow_cap,
                "fm_flow_cap": args.fm_flow_cap,
                "p150_frac": args.p150_frac,
                "suction_static_psi": args.suction_static,
                "ceiling_psi": args.ceiling,
            }
        elif cmd == "hw":
            step = {
                "id": "hw",
                "op": "hw",
                "q_gpm": args.q,
                "c": args.c,
                "d_in": args.id,
                "length_ft": args.length,
            }
        elif cmd == "louver":
            step = {
                "id": "louver",
                "op": "louver",
                "cfm": args.cfm,
                "face_fpm": args.face_fpm,
                "free_area_pct": args.free_area_pct,
            }
        else:
            print(USAGE, file=sys.stderr)
            return 2
        run_steps("(adhoc)", None, [step])
    except CalcError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except TypeError as exc:
        print(f"ERROR: missing or extra input: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(USAGE, end="")
        return 0 if argv else 2
    if argv[0] in OP_CANON or argv[0] in {
        "hydrant",
        "density-area",
        "pump-envelope",
        "hw",
        "louver",
    }:
        return cmd_adhoc(argv)
    return cmd_json(Path(argv[0]))


if __name__ == "__main__":
    sys.exit(main())
