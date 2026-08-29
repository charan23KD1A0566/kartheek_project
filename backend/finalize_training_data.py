#!/usr/bin/env python3
import csv
from pathlib import Path
from random import shuffle

root = Path('d:\\sif sentimental\\data')
csv_path = root / 'training_reports.csv'

# Read existing data
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Additional 90+ scenarios to reach 700
additional = [
    ('Worker used an uncertified ladder borrowed from another department.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('A temporary cord was used to suspend a platform during maintenance.', 'YES', 'CRITICAL', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('Fall protection was not used due to employee discomfort with harnesses.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('A worker moved between two elevated surfaces without fall protection connection.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('The anchor point for fall protection was estimated without structural verification.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('Heights exceeding 10 feet were worked without a detailed fall protection plan.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('A used rescue harness with visible damage was repurposed for another worker.', 'YES', 'CRITICAL', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('Fall protection was not used because the work was expected to be brief.', 'YES', 'HIGH', 'WORKING_AT_HEIGHT', 'FALL_PROTECTION'),
    ('An overhead lifting operation used chain slings that showed rust and corrosion.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('Rigging hardware was mixed from different manufacturers without load rating verification.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('A crane lift proceeded without visual confirmation that all slings were engaged.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('The load rating was unknown for a pulley system used in a lift operation.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('Multiple loads were transported on a single lift despite separate rigging being required.', 'YES', 'HIGH', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('An improper knot was tied to secure a suspended load.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('Materials spilled from an overhead conveyor directly into a pedestrian walkway.', 'YES', 'HIGH', 'LINE_OF_FIRE', 'BARRIER_FAILURE'),
    ('An authorized operator was not present when lifting equipment was activated.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('Pedestrian access zones were not marked or barricaded during material hoisting.', 'YES', 'HIGH', 'LINE_OF_FIRE', 'BARRIER_FAILURE'),
    ('A load being transferred slipped because the suspension equipment was worn.', 'YES', 'CRITICAL', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('An untrained person was assigned to monitor a lifting operation.', 'YES', 'HIGH', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('Safe work method statements were not prepared for high-risk lifting operations.', 'YES', 'HIGH', 'LINE_OF_FIRE', 'LOAD_CONTROL'),
    ('An equipment operator was distracted by radio communication during a critical lift.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'TRAFFIC_CONTROL'),
    ('Mobile equipment was operated in an area with known underground electrical hazards.', 'YES', 'CRITICAL', 'VEHICLE_MOBILE_EQUIPMENT', 'TRAFFIC_CONTROL'),
    ('A vehicle was left running in a confined space without ventilation monitoring.', 'YES', 'CRITICAL', 'VEHICLE_MOBILE_EQUIPMENT', 'TRAFFIC_CONTROL'),
    ('Traffic control signal lights were blocked by stacked materials in the work zone.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'TRAFFIC_CONTROL'),
    ('A spotter was not assigned for equipment operations in areas with reduced visibility.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'PEDESTRIAN_SEGREGATION'),
    ('Equipment was operated in reverse without sounding the audible alarm.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'TRAFFIC_CONTROL'),
    ('A vehicle backed into a work area where personnel were present.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'PEDESTRIAN_SEGREGATION'),
    ('Mobile equipment inspection revealed hydraulic leaks that were not immediately addressed.', 'YES', 'MEDIUM', 'VEHICLE_MOBILE_EQUIPMENT', 'INSPECTION_FAILURE'),
    ('An operator continued work despite the vehicle emitting smoke from the engine.', 'YES', 'MEDIUM', 'VEHICLE_MOBILE_EQUIPMENT', 'INSPECTION_FAILURE'),
    ('Load placement on mobile equipment exceeded the side overhang limit.', 'YES', 'HIGH', 'VEHICLE_MOBILE_EQUIPMENT', 'LOAD_CONTROL'),
    ('A confined space was entered without confirming that hazardous gases were not present.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'ATMOSPHERIC_TESTING'),
    ('Rescue equipment was located far from the confined space entry point.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'PERMIT_FAILURE'),
    ('A sump pump was used to remove water from a confined space without atmospheric testing afterward.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'ATMOSPHERIC_TESTING'),
    ('An oxygen-depleted atmosphere was suspected but entry was allowed to continue.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'ATMOSPHERIC_TESTING'),
    ('A confined space entry permit was not posted at the access point.', 'YES', 'HIGH', 'CONFINED_SPACE', 'PERMIT_FAILURE'),
    ('A non-English-speaking worker was sent alone into a confined space.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'MONITORING_FAILURE'),
    ('Ventilation of a confined space was shut off before work was completed.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'ATMOSPHERIC_TESTING'),
    ('Multiple confined spaces were being worked simultaneously by the same team.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'MONITORING_FAILURE'),
    ('A potent chemical odor was detected in a confined space entry point but work continued.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'ATMOSPHERIC_TESTING'),
    ('Rescue training was not current for personnel assigned to confined-space rescues.', 'YES', 'CRITICAL', 'CONFINED_SPACE', 'PERMIT_FAILURE'),
    ('A chemical was disposed of without reviewing hazard classification for reactivity.', 'YES', 'MEDIUM', 'CHEMICAL_EXPOSURE', 'PROCESS_CONTROL'),
    ('Personal protective equipment was selected without checking chemical compatibility.', 'YES', 'HIGH', 'CHEMICAL_EXPOSURE', 'PPE_FAILURE'),
    ('Airborne dust concentration was not monitored in a chemical handling area.', 'YES', 'MEDIUM', 'CHEMICAL_EXPOSURE', 'PROCESS_CONTROL'),
    ('A chemical drum was transported without securing the lid.', 'YES', 'MEDIUM', 'CHEMICAL_EXPOSURE', 'PROCESS_CONTROL'),
    ('Chemical waste was mixed to reduce disposal volume without hazard assessment.', 'YES', 'HIGH', 'CHEMICAL_EXPOSURE', 'PROCESS_CONTROL'),
    ('An incompatible chemical was briefly stored next to existing inventory.', 'YES', 'HIGH', 'CHEMICAL_EXPOSURE', 'STORAGE_CONTROL'),
    ('A respirator filter was reused after showing signs of saturation.', 'YES', 'HIGH', 'CHEMICAL_EXPOSURE', 'PPE_FAILURE'),
    ('Hot work permit duration expired but welding continued on the same project.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PERMIT_FAILURE'),
    ('A fire watch was assigned but left the immediate area to attend other tasks.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PERMIT_FAILURE'),
    ('Propane heating equipment was used without ventilation in an enclosed space.', 'YES', 'CRITICAL', 'FIRE_EXPLOSION', 'PROCESS_CONTROL'),
    ('An electrically heated tool was plugged into a wet location without GFCI protection.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'LOTO_ISOLATION'),
    ('Combustible materials accumulated near a thermal cutting operation.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PROCESS_CONTROL'),
    ('A vehicle fueling operation was conducted near a hot work site.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PROCESS_CONTROL'),
    ('Insulation material was not removed from the work area before plasma cutting.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PROCESS_CONTROL'),
    ('Hot work continued after normal business hours with reduced supervision.', 'YES', 'HIGH', 'FIRE_EXPLOSION', 'PERMIT_FAILURE'),
    ('An excavation sidewall angle was steeper than recommended for the soil type.', 'YES', 'CRITICAL', 'EXCAVATION', 'GROUND_CONTROL'),
    ('Equipment continued to operate at the excavation edge during personnel work below.', 'YES', 'CRITICAL', 'EXCAVATION', 'GROUND_CONTROL'),
    ('Subsurface conditions changed but protective systems were not reevaluated.', 'YES', 'CRITICAL', 'EXCAVATION', 'GROUND_CONTROL'),
    ('A deep utility cut was made near an excavation without soil stabilization.', 'YES', 'CRITICAL', 'EXCAVATION', 'INSPECTION_FAILURE'),
    ('Vibration from nearby equipment destabilized the trench walls.', 'YES', 'HIGH', 'EXCAVATION', 'GROUND_CONTROL'),
    ('A competent person inspection was not performed after overnight rainfall.', 'YES', 'CRITICAL', 'EXCAVATION', 'GROUND_CONTROL'),
    ('Excavation proceeded into an area where gas line pressures were not verified.', 'YES', 'CRITICAL', 'EXCAVATION', 'INSPECTION_FAILURE'),
    ('Personnel removed breathing equipment while still inside the excavation.', 'YES', 'CRITICAL', 'EXCAVATION', 'PPE_FAILURE'),
    ('A machine guard removal was documented but reinstallation was not verified.', 'YES', 'HIGH', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('Equipment was returned to service before all LOTO devices were removed.', 'YES', 'CRITICAL', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('Production quotas overrode safety procedures for critical control verification.', 'YES', 'HIGH', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('A safety test was not performed after equipment modifications were completed.', 'YES', 'HIGH', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('An emergency stop function was disabled to allow continuous machine operation.', 'YES', 'CRITICAL', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('Critical safety documentation was stored off-site during maintenance.', 'YES', 'MEDIUM', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('A temporary repair was applied to critical equipment and not followed up.', 'YES', 'HIGH', 'CRITICAL_CONTROL_FAILURE', 'BARRIER_BYPASS'),
    ('Hearing damage resulted from noise exposure in areas without protection requirements.', 'YES', 'MEDIUM', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('Skin sensitization occurred from repeated chemical contact during unprotected work.', 'YES', 'MEDIUM', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('An employee continued work with improperly fitted respiratory protection.', 'YES', 'HIGH', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('Protective eyewear was left fogged during grinding due to improper ventilation.', 'YES', 'MEDIUM', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('A used harness passed visual inspection but failed proof load testing.', 'YES', 'CRITICAL', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('Protective gloves became contaminated and were used without replacement.', 'YES', 'MEDIUM', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('An employee reported a skin rash from wearing incompatible protective gear.', 'YES', 'MEDIUM', 'PPE_FAILURE', 'PPE_FAILURE'),
    ('Safe chemical storage practices were followed with clear labeling and segregation.', 'NO', 'LOW', 'CHEMICAL_EXPOSURE', 'NONE'),
    ('Personal protective equipment was inspected before each use and properly maintained.', 'NO', 'LOW', 'PPE_FAILURE', 'NONE'),
    ('Rescue procedures were tested quarterly and documented with successful outcomes.', 'NO', 'LOW', 'CONFINED_SPACE', 'NONE'),
    ('Fall protection training was current for all workers assigned to elevated work.', 'NO', 'LOW', 'WORKING_AT_HEIGHT', 'NONE'),
    ('Equipment operators held valid certifications and passed annual competency assessments.', 'NO', 'LOW', 'VEHICLE_MOBILE_EQUIPMENT', 'NONE'),
    ('Excavation work met all regulatory standards with proper permitting and inspections.', 'NO', 'LOW', 'EXCAVATION', 'NONE'),
]

# Add new rows
for text, sif, risk, hazard, control in additional:
    rows.append({
        'report_text': text,
        'sif_status': sif,
        'risk_level': risk,
        'hazard_category': hazard,
        'control_failure': control,
    })

# Shuffle
shuffle(rows)

# Write updated CSV
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['report_text', 'sif_status', 'risk_level', 'hazard_category', 'control_failure'])
    writer.writeheader()
    writer.writerows(rows)

yes_count = sum(1 for r in rows if r['sif_status'] == 'YES')
no_count = sum(1 for r in rows if r['sif_status'] == 'NO')
uncertain_count = sum(1 for r in rows if r['sif_status'] == 'UNCERTAIN')

print(f'✓ Final dataset: {len(rows)} training records')
print(f'  - YES (dangerous):    {yes_count} ({100*yes_count/len(rows):.1f}%)')
print(f'  - NO (safe):          {no_count} ({100*no_count/len(rows):.1f}%)')
print(f'  - UNCERTAIN:          {uncertain_count} ({100*uncertain_count/len(rows):.1f}%)')
print(f'\nDataset saved to: {csv_path}')
