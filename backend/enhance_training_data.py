#!/usr/bin/env python3
"""
Add additional scenarios to reach 700+ training records.
This script appends more data generation to the existing expand_training_data.py
"""

import csv
from pathlib import Path
from random import shuffle

# Additional supplementary scenarios to reach 700+ records

SUPPLEMENTARY_SCENARIOS = [
    # More LOTO/Hazardous Energy variations
    ("Worker started equipment without checking for LOTO devices or tags first.", "YES", "CRITICAL", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    ("Electrical repair personnel entered a locked panel without verifying de-energization.", "YES", "CRITICAL", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    ("A mechanic began work on a pressurized system that had not been depressurized.", "YES", "HIGH", "HAZARDOUS_ENERGY", "PRESSURE_CONTROL"),
    ("Power was restored to a machine while a worker was still inside the enclosure.", "YES", "CRITICAL", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    ("An unauthorized person removed lockout devices from a machine.", "YES", "CRITICAL", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    ("Equipment operation resumed immediately after maintenance without LOTO removal protocol.", "YES", "HIGH", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    
    # Safe LOTO examples
    ("All energy isolation points were clearly marked and padlocked before maintenance.", "NO", "LOW", "HAZARDOUS_ENERGY", "NONE"),
    ("A qualified electrician performed three-point verification of de-energization.", "NO", "LOW", "HAZARDOUS_ENERGY", "NONE"),
    ("Lockout procedure was documented and reviewed by two independent safety personnel.", "NO", "LOW", "HAZARDOUS_ENERGY", "NONE"),
    ("Stored mechanical energy was discharged through established safe procedures.", "NO", "LOW", "HAZARDOUS_ENERGY", "NONE"),
    
    # Ambiguous LOTO examples
    ("Equipment maintenance occurred but energy state documentation was not included in the report.", "UNCERTAIN", "HIGH", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    ("LOTO procedures were mentioned in passing but verification steps were not detailed.", "UNCERTAIN", "MEDIUM", "HAZARDOUS_ENERGY", "LOTO_ISOLATION"),
    
    # More Confined Space variations
    ("Personnel access to a below-grade utility vault was initiated without gas detection equipment.", "YES", "CRITICAL", "CONFINED_SPACE", "ATMOSPHERIC_TESTING"),
    ("A worker remained in a confined space after the attendant left the station.", "YES", "CRITICAL", "CONFINED_SPACE", "MONITORING_FAILURE"),
    ("Entry into a storage tank occurred without completing the multi-level atmospheric survey.", "YES", "CRITICAL", "CONFINED_SPACE", "ATMOSPHERIC_TESTING"),
    ("Rescue retrieval equipment was brought to the site after entry had commenced.", "YES", "CRITICAL", "CONFINED_SPACE", "PERMIT_FAILURE"),
    ("Two workers simultaneously entered a confined space without an external attendant.", "YES", "CRITICAL", "CONFINED_SPACE", "MONITORING_FAILURE"),
    
    # Safe Confined Space examples
    ("Atmospheric monitoring was conducted continuously with readings logged every 15 minutes.", "NO", "LOW", "CONFINED_SPACE", "NONE"),
    ("Pre-entry rescue procedures were rehearsed and confirmed with rescue team personnel.", "NO", "LOW", "CONFINED_SPACE", "NONE"),
    ("A backup attendant was positioned to take over monitoring duties during shift changes.", "NO", "LOW", "CONFINED_SPACE", "NONE"),
    ("All entry permit conditions were verified and signed by the competent person.", "NO", "LOW", "CONFINED_SPACE", "NONE"),
    
    # Ambiguous Confined Space examples
    ("Work in a confined space was documented but the specific permit details were not attached.", "UNCERTAIN", "HIGH", "CONFINED_SPACE", "PERMIT_FAILURE"),
    ("A worker described entering a tank but the atmospheric condition measurements were not recorded.", "UNCERTAIN", "HIGH", "CONFINED_SPACE", "ATMOSPHERIC_TESTING"),
    
    # More Fall Protection variations
    ("A worker accessed a 30-foot rooftop using a portable ladder without fall restraint.", "YES", "CRITICAL", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    ("Extension work on a mezzanine occurred without verification of guardrail integrity.", "YES", "HIGH", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    ("Personnel removed personal protective equipment before completing elevated work.", "YES", "HIGH", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    ("A harness connection point was not verified before beginning work at height.", "YES", "HIGH", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    ("Window cleaning was performed at height without a certified fall arrest system.", "YES", "CRITICAL", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    
    # Safe Fall Protection examples
    ("All workers received annual fall protection training with current certification cards.", "NO", "LOW", "WORKING_AT_HEIGHT", "NONE"),
    ("Fall arrest systems were inspected before each use and any damage was immediately removed.", "NO", "LOW", "WORKING_AT_HEIGHT", "NONE"),
    ("Work at height was suspended when environmental conditions made safety procedures ineffective.", "NO", "LOW", "WORKING_AT_HEIGHT", "NONE"),
    ("An authorized rigger verified all anchor points and load ratings before work commenced.", "NO", "LOW", "WORKING_AT_HEIGHT", "NONE"),
    
    # Ambiguous Fall Protection examples
    ("Elevated work was performed but the specific fall protection method was not stated.", "UNCERTAIN", "HIGH", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    ("A worker was seen at height but whether a harness was worn could not be confirmed.", "UNCERTAIN", "HIGH", "WORKING_AT_HEIGHT", "FALL_PROTECTION"),
    
    # More Line of Fire variations
    ("A personnel was positioned directly beneath a crane's load path during a lift.", "YES", "CRITICAL", "LINE_OF_FIRE", "LOAD_CONTROL"),
    ("Materials were hoisted over an active work area with employees present.", "YES", "CRITICAL", "LINE_OF_FIRE", "BARRIER_FAILURE"),
    ("Barricade tape was the only protection around a lifting operation area.", "YES", "HIGH", "LINE_OF_FIRE", "BARRIER_FAILURE"),
    ("Load weight verification was not performed before hoisting commenced.", "YES", "HIGH", "LINE_OF_FIRE", "LOAD_CONTROL"),
    ("A spotter position was not established for the overhead lift operation.", "YES", "HIGH", "LINE_OF_FIRE", "LOAD_CONTROL"),
    
    # Safe Line of Fire examples
    ("Heavy equipment was lifted using certified rigging equipment with a qualified operator.", "NO", "LOW", "LINE_OF_FIRE", "NONE"),
    ("Radio communication between lift operator and spotters was verified and tested.", "NO", "LOW", "LINE_OF_FIRE", "NONE"),
    ("No personnel were allowed in the drop zone until the final all-clear was given.", "NO", "LOW", "LINE_OF_FIRE", "NONE"),
    ("Multiple hardened barricades were installed to protect the surrounding work area.", "NO", "LOW", "LINE_OF_FIRE", "NONE"),
    
    # Ambiguous Line of Fire examples
    ("Lifting occurred but confirmation of personnel clearance was not documented.", "UNCERTAIN", "HIGH", "LINE_OF_FIRE", "LOAD_CONTROL"),
    ("Materials were hoisted but the specific rigging method was not described.", "UNCERTAIN", "MEDIUM", "LINE_OF_FIRE", "LOAD_CONTROL"),
    
    # More Vehicle/Mobile Equipment variations
    ("A powered industrial truck operated in a congested area without backup alarm.", "YES", "HIGH", "VEHICLE_MOBILE_EQUIPMENT", "TRAFFIC_CONTROL"),
    ("Mobile crane operations continued during reduced visibility conditions.", "YES", "HIGH", "VEHICLE_MOBILE_EQUIPMENT", "TRAFFIC_CONTROL"),
    ("An equipment operator was using a radio instead of maintaining situational awareness.", "YES", "MEDIUM", "VEHICLE_MOBILE_EQUIPMENT", "PEDESTRIAN_SEGREGATION"),
    ("Vehicle inspection checklists were not completed before equipment was placed into service.", "YES", "MEDIUM", "VEHICLE_MOBILE_EQUIPMENT", "INSPECTION_FAILURE"),
    ("A forklift load was stacked higher than the maximum rated capacity of the vehicle.", "YES", "HIGH", "VEHICLE_MOBILE_EQUIPMENT", "LOAD_CONTROL"),
    
    # Safe Vehicle/Mobile Equipment examples
    ("The loading dock was segregated with dedicated pedestrian walkways marked in yellow.", "NO", "LOW", "VEHICLE_MOBILE_EQUIPMENT", "NONE"),
    ("All mobile equipment operators held valid certifications and completed annual refresher training.", "NO", "LOW", "VEHICLE_MOBILE_EQUIPMENT", "NONE"),
    ("Vehicle pre-shift inspections were logged daily with any defects immediately remedied.", "NO", "LOW", "VEHICLE_MOBILE_EQUIPMENT", "NONE"),
    ("Speed governors were installed and set on all equipment operating in pedestrian areas.", "NO", "LOW", "VEHICLE_MOBILE_EQUIPMENT", "NONE"),
    
    # Ambiguous Vehicle/Mobile Equipment examples
    ("Mobile equipment was operated but whether a pre-shift inspection was completed was unclear.", "UNCERTAIN", "MEDIUM", "VEHICLE_MOBILE_EQUIPMENT", "INSPECTION_FAILURE"),
    ("A load was transported but verification of load security was not documented.", "UNCERTAIN", "MEDIUM", "VEHICLE_MOBILE_EQUIPMENT", "LOAD_CONTROL"),
    
    # More Chemical Exposure variations
    ("A chemical reaction occurred in an unventilated area without spill containment.", "YES", "HIGH", "CHEMICAL_EXPOSURE", "PROCESS_CONTROL"),
    ("Unlabeled containers were handled without reference to original safety documentation.", "YES", "HIGH", "CHEMICAL_EXPOSURE", "PROCESS_CONTROL"),
    ("Incompatible chemicals were stored in adjacent locations separated only by a single shelf.", "YES", "MEDIUM", "CHEMICAL_EXPOSURE", "STORAGE_CONTROL"),
    ("A chemical spill was cleaned using only water without consulting the Safety Data Sheet.", "YES", "MEDIUM", "CHEMICAL_EXPOSURE", "PROCESS_CONTROL"),
    ("Maintenance work on chemical equipment was performed without isolation procedures.", "YES", "HIGH", "CHEMICAL_EXPOSURE", "PROCESS_CONTROL"),
    
    # Safe Chemical Exposure examples
    ("All chemical inventory was catalogued with Safety Data Sheets readily accessible.", "NO", "LOW", "CHEMICAL_EXPOSURE", "NONE"),
    ("Spill response kits were positioned throughout the work area with trained personnel assigned.", "NO", "LOW", "CHEMICAL_EXPOSURE", "NONE"),
    ("Chemical transfers used closed-system equipment to eliminate vapor exposure.", "NO", "LOW", "CHEMICAL_EXPOSURE", "NONE"),
    ("Personal protective equipment was selected based on SDS requirements and properly maintained.", "NO", "LOW", "CHEMICAL_EXPOSURE", "NONE"),
    
    # Ambiguous Chemical Exposure examples
    ("Chemical handling was mentioned but specific exposure controls were not described.", "UNCERTAIN", "MEDIUM", "CHEMICAL_EXPOSURE", "PROCESS_CONTROL"),
    ("PPE was used but the type of equipment and material compatibility was not stated.", "UNCERTAIN", "MEDIUM", "CHEMICAL_EXPOSURE", "PPE_FAILURE"),
    
    # More Hot Work variations
    ("Welding equipment was used in a location with residual flammable liquid odor.", "YES", "HIGH", "FIRE_EXPLOSION", "PERMIT_FAILURE"),
    ("Hot work was performed during end-of-shift when fire watch personnel availability was uncertain.", "YES", "HIGH", "FIRE_EXPLOSION", "PERMIT_FAILURE"),
    ("An acetylene bottle was transported in a vehicle with other pressurized cylinders unsecured.", "YES", "MEDIUM", "FIRE_EXPLOSION", "PROCESS_CONTROL"),
    ("Cutting operations produced sparks directed toward cable trays containing plastic insulation.", "YES", "MEDIUM", "FIRE_EXPLOSION", "PROCESS_CONTROL"),
    ("Hot work completed but post-operation fire watch was discontinued prematurely.", "YES", "HIGH", "FIRE_EXPLOSION", "PERMIT_FAILURE"),
    
    # Safe Hot Work examples
    ("Hot work site was cleaned of flammable materials and cleared by a competent person.", "NO", "LOW", "FIRE_EXPLOSION", "NONE"),
    ("Fire detection system activation was verified as part of the hot work permit protocol.", "NO", "LOW", "FIRE_EXPLOSION", "NONE"),
    ("Hot work was scheduled during daylight hours with full fire watch and rescue staffing.", "NO", "LOW", "FIRE_EXPLOSION", "NONE"),
    ("All hot work equipment was inspected and certified safe before bringing to the work site.", "NO", "LOW", "FIRE_EXPLOSION", "NONE"),
    
    # Ambiguous Hot Work examples
    ("Hot work occurred but whether a fire watch was present was not explicitly documented.", "UNCERTAIN", "HIGH", "FIRE_EXPLOSION", "PERMIT_FAILURE"),
    ("Welding operations were performed but flammable material clearance status was not confirmed.", "UNCERTAIN", "HIGH", "FIRE_EXPLOSION", "PROCESS_CONTROL"),
    
    # More Excavation variations
    ("Excavation continued below the maximum depth without soil testing or classification.", "YES", "CRITICAL", "EXCAVATION", "GROUND_CONTROL"),
    ("A trench deeper than 6 feet was opened without competent person supervision.", "YES", "CRITICAL", "EXCAVATION", "GROUND_CONTROL"),
    ("Underground utility line location was not verified before beginning excavation.", "YES", "CRITICAL", "EXCAVATION", "INSPECTION_FAILURE"),
    ("Excavation equipment was operated near the trench edge in violation of safe distance procedures.", "YES", "HIGH", "EXCAVATION", "GROUND_CONTROL"),
    ("Water infiltration from an adjacent source was ignored during excavation operations.", "YES", "HIGH", "EXCAVATION", "GROUND_CONTROL"),
    
    # Safe Excavation examples
    ("Soil strata was identified and appropriate shoring systems were selected and installed.", "NO", "LOW", "EXCAVATION", "NONE"),
    ("Competent person inspections were documented before work and after any changes in conditions.", "NO", "LOW", "EXCAVATION", "NONE"),
    ("All nearby utilities were located via one-call service and marked on the excavation plan.", "NO", "LOW", "EXCAVATION", "NONE"),
    ("Dewatering systems were operational and staffed during the entire excavation period.", "NO", "LOW", "EXCAVATION", "NONE"),
    
    # Ambiguous Excavation examples
    ("Excavation work was described but soil assessment and shoring selection were not detailed.", "UNCERTAIN", "CRITICAL", "EXCAVATION", "GROUND_CONTROL"),
    ("Trench work occurred but inspection records were not attached to the incident report.", "UNCERTAIN", "CRITICAL", "EXCAVATION", "GROUND_CONTROL"),
    
    # More Critical Control Failure variations
    ("A safety circuit interlock was overridden to resume operations without full reset.", "YES", "CRITICAL", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    ("Production pressure resulted in bypassing a required equipment safety verification.", "YES", "HIGH", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    ("A guarded operation continued while the enclosure door was held open to observe the process.", "YES", "HIGH", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    ("Maintenance personnel remained inside a machine enclosure during test operations.", "YES", "CRITICAL", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    ("An equipment reset was not performed after a critical component failure was detected.", "YES", "HIGH", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    
    # Safe Critical Control Failure examples
    ("All critical control verification procedures were conducted before and after maintenance.", "NO", "LOW", "CRITICAL_CONTROL_FAILURE", "NONE"),
    ("An equipment bypass or override was only permitted with written authorization by management.", "NO", "LOW", "CRITICAL_CONTROL_FAILURE", "NONE"),
    ("Safety interlocks were tested weekly and any discrepancies were immediately corrected.", "NO", "LOW", "CRITICAL_CONTROL_FAILURE", "NONE"),
    
    # Ambiguous Critical Control Failure examples
    ("Equipment operation resumed after maintenance but control verification was not documented.", "UNCERTAIN", "HIGH", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    ("A safety test was performed but confirmation of interlocks functionality was unclear.", "UNCERTAIN", "MEDIUM", "CRITICAL_CONTROL_FAILURE", "BARRIER_BYPASS"),
    
    # More PPE Failure variations
    ("Workers entered a high-noise area without hearing protection or noise dosimetry.", "YES", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    ("Chemical work was performed with gloves that were not rated for the specific chemicals used.", "YES", "HIGH", "PPE_FAILURE", "PPE_FAILURE"),
    ("A respirator was used beyond its manufacturer-specified service life.", "YES", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    ("Eye and face protection was removed during grinding operations for better visibility.", "YES", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    ("Foot protection was not enforced in an area where heavy objects were regularly handled.", "YES", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    
    # Safe PPE Failure examples
    ("Personal protective equipment was selected based on a job hazard analysis.", "NO", "LOW", "PPE_FAILURE", "NONE"),
    ("A workplace hearing conservation program was established with annual audiometric testing.", "NO", "LOW", "PPE_FAILURE", "NONE"),
    ("PPE fit testing was conducted for all respirator wearers with records maintained.", "NO", "LOW", "PPE_FAILURE", "NONE"),
    ("Damaged or contaminated protective equipment was immediately replaced and disposed of properly.", "NO", "LOW", "PPE_FAILURE", "NONE"),
    
    # Ambiguous PPE Failure examples
    ("A hazardous task was performed but whether protective equipment was used was unclear.", "UNCERTAIN", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    ("Personal protective equipment was available but usage compliance was not documented.", "UNCERTAIN", "MEDIUM", "PPE_FAILURE", "PPE_FAILURE"),
    
    # More Inspection Failure variations
    ("Equipment that failed recent inspection was temporarily repaired and returned to service.", "YES", "MEDIUM", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    ("A load test certificate was not provided for lifting equipment placed into operation.", "YES", "HIGH", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    ("A pressure vessel was used without a valid third-party inspection and certification.", "YES", "HIGH", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    ("Electrical cords showed visible wear and fraying but were still used for work equipment.", "YES", "MEDIUM", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    ("Annual maintenance was overdue for critical equipment that remained in active service.", "YES", "MEDIUM", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    
    # Safe Inspection Failure examples
    ("Equipment maintenance records were current and readily available for all operations.", "NO", "LOW", "INSPECTION_FAILURE", "NONE"),
    ("Independent third-party inspections were scheduled and completed on required timelines.", "NO", "LOW", "INSPECTION_FAILURE", "NONE"),
    ("Equipment was immediately removed from service when inspection defects were identified.", "NO", "LOW", "INSPECTION_FAILURE", "NONE"),
    ("A preventive maintenance program was established with scheduled tasks logged and verified.", "NO", "LOW", "INSPECTION_FAILURE", "NONE"),
    
    # Ambiguous Inspection Failure examples
    ("Equipment was in use but current inspection documentation was not attached to the report.", "UNCERTAIN", "MEDIUM", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
    ("Maintenance was performed but verification of certification or inspection was unclear.", "UNCERTAIN", "MEDIUM", "INSPECTION_FAILURE", "INSPECTION_FAILURE"),
]

def main():
    root = Path(__file__).resolve().parent.parent
    csv_path = root / "data" / "training_reports.csv"
    
    # Read existing data
    existing_rows = []
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
    
    # Add new rows
    new_rows = []
    for text, sif_status, risk_level, category, control_failure in SUPPLEMENTARY_SCENARIOS:
        new_rows.append({
            "report_text": text,
            "sif_status": sif_status,
            "risk_level": risk_level,
            "hazard_category": category,
            "control_failure": control_failure,
        })
    
    # Combine and shuffle
    all_rows = existing_rows + new_rows
    shuffle(all_rows)
    
    # Write combined data
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["report_text", "sif_status", "risk_level", "hazard_category", "control_failure"])
        writer.writeheader()
        writer.writerows(all_rows)
    
    # Print summary
    yes_count = sum(1 for r in all_rows if r["sif_status"] == "YES")
    no_count = sum(1 for r in all_rows if r["sif_status"] == "NO")
    uncertain_count = sum(1 for r in all_rows if r["sif_status"] == "UNCERTAIN")
    
    print(f"\n✓ Enhanced dataset now has {len(all_rows)} training records")
    print(f"  - YES (dangerous):    {yes_count} ({100*yes_count/len(all_rows):.1f}%)")
    print(f"  - NO (safe):          {no_count} ({100*no_count/len(all_rows):.1f}%)")
    print(f"  - UNCERTAIN:          {uncertain_count} ({100*uncertain_count/len(all_rows):.1f}%)")
    print(f"\nSaved to: {csv_path}")

if __name__ == "__main__":
    main()
