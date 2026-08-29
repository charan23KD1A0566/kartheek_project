#!/usr/bin/env python3
"""
Expand training dataset from ~47 to 700+ high-quality labeled records.

This script generates realistic safety reports with:
- Diverse scenarios across all hazard categories
- Safe, dangerous, and ambiguous versions for each category
- Multiple writing styles and variations
- Proper balance of YES/NO/UNCERTAIN labels
"""

import csv
import json
from pathlib import Path
from random import choice, randint, shuffle

# Define comprehensive hazard scenarios with contrasting pairs

SCENARIOS = {
    # ===== HAZARDOUS ENERGY (LOTO/Electrical/Mechanical) =====
    "HAZARDOUS_ENERGY": {
        "category": "HAZARDOUS_ENERGY",
        "dangerous": [
            ("Worker entered an energized electrical area without completing lockout and isolation.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("Maintenance was performed on a live circuit without proper de-energization.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("The lockout tagout procedure was bypassed while equipment remained energized.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("A worker was exposed to an energized conductor while isolation procedures were not applied.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("Maintenance started while the pump remained energized and no LOTO was applied.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("LOTO was not applied prior to servicing the energized equipment.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("Worker touched an electrical panel without verifying it was de-energized first.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("An operator worked on a live motor without isolation or de-energization.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("The high-voltage area was entered without proper protective equipment and isolation.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("A technician bypassed the emergency stop and worked on energized equipment.", "YES", "HIGH", "LOTO_ISOLATION"),
            ("Hydraulic pressure was not relieved before maintenance on the pressurized line.", "YES", "HIGH", "PRESSURE_CONTROL"),
            ("A worker removed a spring from a compressed system without proper lockout.", "YES", "CRITICAL", "PRESSURE_CONTROL"),
            ("Pneumatic equipment was operated without pressure being vented to atmosphere.", "YES", "HIGH", "PRESSURE_CONTROL"),
            ("A flywheel remained rotating during maintenance work in the hazardous area.", "YES", "HIGH", "ROTATING_EQUIPMENT"),
            ("A conveyor belt continued moving during maintenance without proper isolation.", "YES", "HIGH", "ROTATING_EQUIPMENT"),
            ("Electrical repair continued while the system remained energized at full voltage.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("A worker handled a hot conductor without thermal protection or isolation.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("The panel door was opened and exposed live terminals without arc flash protection.", "YES", "CRITICAL", "PPE_FAILURE"),
            ("Stored spring energy was released when a worker opened the enclosure.", "YES", "HIGH", "PRESSURE_CONTROL"),
            ("A pressurized cylinder was struck by mobile equipment and ruptured.", "YES", "CRITICAL", "PRESSURE_CONTROL"),
            ("Electrical work was performed in wet conditions without de-energization or GFCI.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("An untrained person attempted repairs on energized machinery.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("Maintenance was started before the LOTO checklist was completed and verified.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("A circuit breaker was opened manually while load was still on the line.", "YES", "HIGH", "LOTO_ISOLATION"),
            ("Power tools were used in a wet environment without proper grounding.", "YES", "HIGH", "LOTO_ISOLATION"),
            ("A compressor was used without pressure relief and regulator inspection.", "YES", "HIGH", "PRESSURE_CONTROL"),
            ("The machine was restarted while lockout tags were still in place.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("Gas line work was performed without isolating the gas supply first.", "YES", "CRITICAL", "LOTO_ISOLATION"),
            ("A rotating blade continued spinning after emergency stop was pressed.", "YES", "HIGH", "ROTATING_EQUIPMENT"),
            ("Belt tension was adjusted on a running conveyor without guards in place.", "YES", "CRITICAL", "ROTATING_EQUIPMENT"),
        ],
        "safe": [
            ("The electrical panel was isolated, locked out and verified before maintenance began.", "NO", "LOW", "NONE"),
            ("All equipment was de-energized and verified safe before work commenced.", "NO", "LOW", "NONE"),
            ("The LOTO procedure was completed and a second worker verified the isolation.", "NO", "LOW", "NONE"),
            ("Electrical work followed lockout-tagout protocols with two-person verification.", "NO", "LOW", "NONE"),
            ("Maintenance was scheduled after the pump was de-energized and pressure was relieved.", "NO", "LOW", "NONE"),
            ("The technician confirmed de-energization using a multimeter before starting work.", "NO", "LOW", "NONE"),
            ("All high-voltage areas were properly isolated and grounded before access.", "NO", "LOW", "NONE"),
            ("The emergency stop was verified functional and the motor was isolated before service.", "NO", "LOW", "NONE"),
            ("Hydraulic pressure was fully relieved and the system vented to atmosphere.", "NO", "LOW", "NONE"),
            ("The pneumatic system was depressurized and bled down before maintenance.", "NO", "LOW", "NONE"),
            ("Spring tension was released through approved mechanical release before removal.", "NO", "LOW", "NONE"),
            ("The flywheel came to a complete stop and was mechanically locked before access.", "NO", "LOW", "NONE"),
            ("The conveyor belt was stopped, locked out and tagged before maintenance work.", "NO", "LOW", "NONE"),
            ("All rotating equipment was de-energized, blocked and verified stopped.", "NO", "LOW", "NONE"),
            ("Stored energy was completely dissipated and verified before opening the enclosure.", "NO", "LOW", "NONE"),
            ("A qualified electrician performed all high-voltage work with proper PPE and isolation.", "NO", "LOW", "NONE"),
            ("The lockout station was properly labeled and only authorized personnel had access.", "NO", "LOW", "NONE"),
            ("Pressure was verified zero before any work on the pressurized line commenced.", "NO", "LOW", "NONE"),
            ("All energy sources were identified, isolated and locked for the maintenance period.", "NO", "LOW", "NONE"),
            ("A LOTO inspection was completed to confirm all isolation points were addressed.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Electrical maintenance was planned but the report does not specify whether isolation was completed.", "UNCERTAIN", "MEDIUM", "LOTO_ISOLATION"),
            ("Work near energized equipment was mentioned but details about precautions were unclear.", "UNCERTAIN", "MEDIUM", "LOTO_ISOLATION"),
            ("LOTO procedures were discussed but confirmation of actual implementation was missing.", "UNCERTAIN", "HIGH", "LOTO_ISOLATION"),
            ("A worker accessed the electrical area but the report does not clearly describe the state of the system.", "UNCERTAIN", "MEDIUM", "LOTO_ISOLATION"),
            ("Maintenance on the pump occurred but pressure relief status was not documented.", "UNCERTAIN", "MEDIUM", "PRESSURE_CONTROL"),
            ("Work involving the hydraulic system was mentioned but isolation status was unclear.", "UNCERTAIN", "MEDIUM", "PRESSURE_CONTROL"),
            ("A technician was working near rotating equipment but the report does not confirm it was stopped.", "UNCERTAIN", "MEDIUM", "ROTATING_EQUIPMENT"),
            ("Energy work was described but the specific de-energization method was not stated.", "UNCERTAIN", "HIGH", "LOTO_ISOLATION"),
            ("Pressure equipment maintenance was discussed but relief valve operation was not confirmed.", "UNCERTAIN", "MEDIUM", "PRESSURE_CONTROL"),
        ],
    },

    # ===== CONFINED SPACE =====
    "CONFINED_SPACE": {
        "category": "CONFINED_SPACE",
        "dangerous": [
            ("Worker entered a confined space without atmospheric testing or gas monitoring.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("An employee entered a tank without an authorized permit and rescue plan.", "YES", "CRITICAL", "PERMIT_FAILURE"),
            ("Hazardous gas was detected in a confined space with no trained attendant present.", "YES", "CRITICAL", "MONITORING_FAILURE"),
            ("Confined-space entry started without ventilation, gas testing, or an emergency rescue procedure.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("A worker was sent into a manhole without proper atmospheric monitoring or rescue equipment.", "YES", "CRITICAL", "PERMIT_FAILURE"),
            ("An operator entered a vessel without verifying that hazardous chemicals were removed.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("A confined-space entry occurred without a designated safety watch.", "YES", "CRITICAL", "MONITORING_FAILURE"),
            ("Entry into an underground tank was attempted without atmospheric testing.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("A worker entered a closed vessel without checking the oxygen levels first.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("Confined-space rescue equipment was not available when entry occurred.", "YES", "CRITICAL", "PERMIT_FAILURE"),
            ("An employee went into a confined space to retrieve tools without proper precautions.", "YES", "CRITICAL", "PERMIT_FAILURE"),
            ("A sewer line entry was initiated without atmospheric testing or rescue standby.", "YES", "CRITICAL", "ATMOSPHERIC_TESTING"),
            ("A worker was sent alone into a confined space to complete repairs.", "YES", "CRITICAL", "MONITORING_FAILURE"),
            ("Confined-space work was performed without a hot work permit extension where welding was involved.", "YES", "CRITICAL", "PERMIT_FAILURE"),
            ("A paint booth was entered without verifying ventilation was operational.", "YES", "HIGH", "ATMOSPHERIC_TESTING"),
        ],
        "safe": [
            ("The confined-space permit was approved and atmospheric testing was completed before entry.", "NO", "LOW", "NONE"),
            ("Gas testing was performed and levels were within safe limits before personnel entered.", "NO", "LOW", "NONE"),
            ("A trained attendant was stationed outside with active communication and rescue equipment ready.", "NO", "LOW", "NONE"),
            ("The confined space was ventilated continuously during the entire entry period.", "NO", "LOW", "NONE"),
            ("The manhole was properly tested, vented and a rescue harness was used.", "NO", "LOW", "NONE"),
            ("All hazardous chemicals were removed and verified absent before any entry.", "NO", "LOW", "NONE"),
            ("Entry was conducted by authorized personnel following all permit-required procedures.", "NO", "LOW", "NONE"),
            ("Atmospheric conditions were monitored continuously and rescue personnel were on standby.", "NO", "LOW", "NONE"),
            ("A confined-space entry permit was completed with all required sign-offs before work.", "NO", "LOW", "NONE"),
            ("Two trained workers were present with full harness systems and emergency retrieval equipment.", "NO", "LOW", "NONE"),
            ("Atmospheric testing showed oxygen levels between 19.5% and 23.5% and no hazardous gases.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Entry into a confined space was mentioned but atmospheric testing status was unclear.", "UNCERTAIN", "HIGH", "ATMOSPHERIC_TESTING"),
            ("A worker was assigned to monitor a confined-space entry but details were incomplete.", "UNCERTAIN", "HIGH", "MONITORING_FAILURE"),
            ("Confined-space work was discussed but the permit documentation was not referenced.", "UNCERTAIN", "HIGH", "PERMIT_FAILURE"),
            ("Ventilation was provided but it was unclear if continuous monitoring occurred.", "UNCERTAIN", "MEDIUM", "ATMOSPHERIC_TESTING"),
            ("Entry was described but whether a trained attendant was present was not stated.", "UNCERTAIN", "HIGH", "MONITORING_FAILURE"),
        ],
    },

    # ===== WORKING AT HEIGHT / FALL PROTECTION =====
    "WORKING_AT_HEIGHT": {
        "category": "WORKING_AT_HEIGHT",
        "dangerous": [
            ("Worker performed work at height without fall protection near an unprotected edge.", "YES", "HIGH", "FALL_PROTECTION"),
            ("An operator climbed an unsafe scaffold without a harness or guardrail.", "YES", "HIGH", "FALL_PROTECTION"),
            ("Roof work continued with missing guardrails and no fall arrest system.", "YES", "HIGH", "FALL_PROTECTION"),
            ("A worker used an unsecured ladder at height without proper protection.", "YES", "HIGH", "FALL_PROTECTION"),
            ("An employee accessed the elevated platform without any fall protection equipment.", "YES", "HIGH", "FALL_PROTECTION"),
            ("Work at height was performed on an unstable surface with no safety measures.", "YES", "CRITICAL", "FALL_PROTECTION"),
            ("A worker hung tools from an overhead beam without safety securing.", "YES", "MEDIUM", "FALL_PROTECTION"),
            ("An operator leaned over the edge of an elevated platform without restraint.", "YES", "HIGH", "FALL_PROTECTION"),
            ("Ladder was placed on unstable ground and worker climbed without tying off.", "YES", "HIGH", "FALL_PROTECTION"),
            ("Access to the elevated area had missing guardrails and no certified fall protection.", "YES", "HIGH", "FALL_PROTECTION"),
        ],
        "safe": [
            ("Work at height used inspected scaffolding, guardrails, and an attached harness.", "NO", "LOW", "NONE"),
            ("The worker wore a properly fitted harness connected to a secure anchorage point.", "NO", "LOW", "NONE"),
            ("Fall protection was verified functional and edge protection was installed before work.", "NO", "LOW", "NONE"),
            ("The ladder was secured to stable ground and a spotter was present during use.", "NO", "LOW", "NONE"),
            ("All personnel at height wore approved personal fall arrest systems.", "NO", "LOW", "NONE"),
            ("Guardrails were installed at all unprotected edges with proper handrails.", "NO", "LOW", "NONE"),
            ("Safety net was properly installed and certified for the work height.", "NO", "LOW", "NONE"),
            ("The platform was inspected for structural integrity before access was granted.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Work at height was performed but fall protection equipment status was not documented.", "UNCERTAIN", "HIGH", "FALL_PROTECTION"),
            ("An elevated task occurred but harness usage was not clearly mentioned.", "UNCERTAIN", "HIGH", "FALL_PROTECTION"),
            ("Scaffolding was used for the work but structural integrity was not confirmed in the report.", "UNCERTAIN", "MEDIUM", "FALL_PROTECTION"),
            ("Access to height required but the specific protection measures were unclear.", "UNCERTAIN", "HIGH", "FALL_PROTECTION"),
        ],
    },

    # ===== LINE OF FIRE / SUSPENDED LOADS =====
    "LINE_OF_FIRE": {
        "category": "LINE_OF_FIRE",
        "dangerous": [
            ("A suspended load moved over a worker area without barriers or exclusion zones.", "YES", "CRITICAL", "BARRIER_FAILURE"),
            ("A worker stood in the line of fire below an unsecured overhead load.", "YES", "CRITICAL", "LOAD_CONTROL"),
            ("Material fell near an employee because the lifting area was not barricaded.", "YES", "HIGH", "BARRIER_FAILURE"),
            ("A heavy object was suspended over a work area with personnel present underneath.", "YES", "CRITICAL", "LOAD_CONTROL"),
            ("Lifting operations continued while workers were positioned in the drop zone.", "YES", "CRITICAL", "LOAD_CONTROL"),
            ("A load was hoisted over an occupied area without any warning or exclusion.", "YES", "CRITICAL", "BARRIER_FAILURE"),
            ("Rigging equipment was used but the load was not properly centered and controlled.", "YES", "HIGH", "LOAD_CONTROL"),
            ("An operator hoisted materials without confirming all personnel were clear of the area.", "YES", "HIGH", "LOAD_CONTROL"),
            ("Stacked items fell because they were not properly secured for lifting.", "YES", "HIGH", "LOAD_CONTROL"),
        ],
        "safe": [
            ("The lifting zone was barricaded and no worker was beneath the suspended load.", "NO", "LOW", "NONE"),
            ("All personnel were cleared from the drop zone before the load was hoisted.", "NO", "LOW", "NONE"),
            ("Warning signs and barriers were posted to exclude workers from the lifting area.", "NO", "LOW", "NONE"),
            ("The load was properly rigged, inspected and controlled during the lift.", "NO", "LOW", "NONE"),
            ("Spotter communication was established before lifting commenced.", "NO", "LOW", "NONE"),
            ("The suspended load was properly secured and load path was verified clear.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Lifting operations occurred but exclusion zone status was not clearly documented.", "UNCERTAIN", "HIGH", "BARRIER_FAILURE"),
            ("A suspended load was moved but worker positions relative to the load were unclear.", "UNCERTAIN", "HIGH", "LOAD_CONTROL"),
            ("Hoisting was performed but clearance confirmation was not mentioned in the report.", "UNCERTAIN", "HIGH", "LOAD_CONTROL"),
        ],
    },

    # ===== VEHICLE / MOBILE EQUIPMENT =====
    "VEHICLE_MOBILE_EQUIPMENT": {
        "category": "VEHICLE_MOBILE_EQUIPMENT",
        "dangerous": [
            ("A forklift reversed into a pedestrian area without a spotter or working alarm.", "YES", "HIGH", "PEDESTRIAN_SEGREGATION"),
            ("A truck and pedestrian nearly collided in a blind spot with no segregation.", "YES", "HIGH", "TRAFFIC_CONTROL"),
            ("Mobile equipment operated in a busy work area without reversing controls.", "YES", "HIGH", "TRAFFIC_CONTROL"),
            ("A crane operated without current inspection or certification during lifting.", "YES", "HIGH", "INSPECTION_FAILURE"),
            ("A vehicle moved through a pedestrian walkway at high speed without warning.", "YES", "HIGH", "TRAFFIC_CONTROL"),
            ("Mobile equipment was left running unattended in an active work area.", "YES", "MEDIUM", "TRAFFIC_CONTROL"),
            ("A loader operated in an area with pedestrians and no effective communication.", "YES", "HIGH", "PEDESTRIAN_SEGREGATION"),
            ("Vehicle backup occurred without audible alarm or visual indicators functioning.", "YES", "HIGH", "TRAFFIC_CONTROL"),
            ("A powered industrial truck transported a load that obstructed the operator's view.", "YES", "MEDIUM", "LOAD_CONTROL"),
        ],
        "safe": [
            ("The forklift route was segregated and a trained spotter controlled reversing.", "NO", "LOW", "NONE"),
            ("Mobile equipment operated in a designated zone with pedestrians excluded.", "NO", "LOW", "NONE"),
            ("All vehicles had functioning warning alarms and reverse lights operational.", "NO", "LOW", "NONE"),
            ("The crane operator held current certification and equipment was inspected before use.", "NO", "LOW", "NONE"),
            ("Pedestrian and vehicle traffic was segregated with clear markings and barriers.", "NO", "LOW", "NONE"),
            ("Spotters with clear communication channels managed all vehicle movements.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("A forklift was operating but spotter presence was not clearly documented.", "UNCERTAIN", "MEDIUM", "PEDESTRIAN_SEGREGATION"),
            ("Vehicle movement occurred but backup alarm functionality was not confirmed.", "UNCERTAIN", "MEDIUM", "TRAFFIC_CONTROL"),
            ("Mobile equipment was used but pedestrian segregation status was unclear.", "UNCERTAIN", "MEDIUM", "PEDESTRIAN_SEGREGATION"),
            ("A crane lift was performed but current certification was not mentioned.", "UNCERTAIN", "MEDIUM", "INSPECTION_FAILURE"),
        ],
    },

    # ===== CHEMICAL EXPOSURE =====
    "CHEMICAL_EXPOSURE": {
        "category": "CHEMICAL_EXPOSURE",
        "dangerous": [
            ("A worker handled chemicals without required protective equipment or exposure controls.", "YES", "HIGH", "PPE_FAILURE"),
            ("Chemical storage containers were left open in a warm area without ventilation.", "YES", "MEDIUM", "STORAGE_CONTROL"),
            ("An employee mixed incompatible chemicals without proper containment or ventilation.", "YES", "HIGH", "PROCESS_CONTROL"),
            ("A worker was exposed to chemical vapors without a respiratory protection program.", "YES", "HIGH", "PPE_FAILURE"),
            ("Hazardous chemicals were transferred without secondary containment or drip pans.", "YES", "MEDIUM", "PROCESS_CONTROL"),
            ("An operator worked with solvents without gloves or eye protection.", "YES", "HIGH", "PPE_FAILURE"),
            ("Chemical exposure occurred because Safety Data Sheets were not consulted.", "YES", "MEDIUM", "PROCESS_CONTROL"),
            ("A worker disposed of chemicals down the drain without proper procedures.", "YES", "MEDIUM", "PROCESS_CONTROL"),
        ],
        "safe": [
            ("Chemical handling followed the approved procedure with suitable PPE and ventilation.", "NO", "LOW", "NONE"),
            ("Workers wore appropriate personal protective equipment including gloves and eye protection.", "NO", "LOW", "NONE"),
            ("Chemical storage was properly ventilated and segregated from incompatible materials.", "NO", "LOW", "NONE"),
            ("All hazardous materials procedures were reviewed and Safety Data Sheets were available.", "NO", "LOW", "NONE"),
            ("Secondary containment and drip pans were in place during chemical transfers.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Chemical work was performed but PPE usage was not explicitly documented.", "UNCERTAIN", "MEDIUM", "PPE_FAILURE"),
            ("Hazardous material handling occurred but ventilation status was unclear.", "UNCERTAIN", "MEDIUM", "PROCESS_CONTROL"),
            ("Chemical storage was mentioned but containment measures were not detailed.", "UNCERTAIN", "MEDIUM", "STORAGE_CONTROL"),
        ],
    },

    # ===== HOT WORK / FIRE HAZARD =====
    "FIRE_EXPLOSION": {
        "category": "FIRE_EXPLOSION",
        "dangerous": [
            ("Hot work occurred near flammable materials without a fire watch or permit.", "YES", "HIGH", "PERMIT_FAILURE"),
            ("Welding was performed without verifying that flammable materials were removed.", "YES", "HIGH", "PROCESS_CONTROL"),
            ("An acetylene torch was used without proper testing or fire prevention measures.", "YES", "HIGH", "PERMIT_FAILURE"),
            ("Grinding sparks fell near oily rags and combustible debris without intervention.", "YES", "MEDIUM", "PROCESS_CONTROL"),
            ("Hot work continued after the fire watch duty ended without a relief.", "YES", "HIGH", "PERMIT_FAILURE"),
            ("A cutting torch was used on a pressurized line without depressurization.", "YES", "CRITICAL", "PROCESS_CONTROL"),
        ],
        "safe": [
            ("The hot work permit and fire watch were confirmed before welding started.", "NO", "LOW", "NONE"),
            ("All flammable materials were cleared from the work area before hot work began.", "NO", "LOW", "NONE"),
            ("A trained fire watch remained present during and after all hot work operations.", "NO", "LOW", "NONE"),
            ("Fire prevention equipment and extinguishers were verified functional and nearby.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Hot work was performed but fire watch status was not clearly documented.", "UNCERTAIN", "HIGH", "PERMIT_FAILURE"),
            ("Welding occurred but verification of flammable material clearance was unclear.", "UNCERTAIN", "HIGH", "PROCESS_CONTROL"),
            ("A permit was mentioned but whether all conditions were verified was not stated.", "UNCERTAIN", "MEDIUM", "PERMIT_FAILURE"),
        ],
    },

    # ===== EXCAVATION / TRENCH COLLAPSE =====
    "EXCAVATION": {
        "category": "EXCAVATION",
        "dangerous": [
            ("An excavation had no shoring and workers were exposed to a possible collapse.", "YES", "CRITICAL", "GROUND_CONTROL"),
            ("Workers entered a deep trench without protective systems or inspection.", "YES", "CRITICAL", "GROUND_CONTROL"),
            ("Trenching continued with loose soil and no protective systems installed.", "YES", "CRITICAL", "GROUND_CONTROL"),
            ("Underground utilities were damaged because a locate was not performed.", "YES", "HIGH", "INSPECTION_FAILURE"),
            ("Water accumulation in an excavation was ignored and work continued.", "YES", "HIGH", "GROUND_CONTROL"),
        ],
        "safe": [
            ("The excavation was properly shored using approved protective systems.", "NO", "LOW", "NONE"),
            ("Underground utilities were marked and the trench was inspected before work.", "NO", "LOW", "NONE"),
            ("Water was controlled and drainage systems were in place during excavation.", "NO", "LOW", "NONE"),
            ("Competent person inspections were completed before and during the work.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("An excavation was performed but shoring status was not documented.", "UNCERTAIN", "CRITICAL", "GROUND_CONTROL"),
            ("Trenching occurred but protective system verification was unclear.", "UNCERTAIN", "CRITICAL", "GROUND_CONTROL"),
            ("Underground work was mentioned but utility locate status was not confirmed.", "UNCERTAIN", "HIGH", "INSPECTION_FAILURE"),
        ],
    },

    # ===== MACHINE GUARDING =====
    "CRITICAL_CONTROL_FAILURE": {
        "category": "CRITICAL_CONTROL_FAILURE",
        "dangerous": [
            ("A machine guard was removed and rotating equipment was operated without the barrier.", "YES", "HIGH", "BARRIER_BYPASS"),
            ("A permit-required task began without authorization or verification of critical controls.", "YES", "HIGH", "PERMIT_FAILURE"),
            ("Safety interlocks were bypassed to continue production despite hazards.", "YES", "HIGH", "BARRIER_BYPASS"),
            ("An emergency stop was disabled so production would not be interrupted.", "YES", "CRITICAL", "BARRIER_BYPASS"),
            ("A machine was operated while maintenance personnel were still inside.", "YES", "CRITICAL", "BARRIER_BYPASS"),
        ],
        "safe": [
            ("The machine guard was installed and tested before the equipment was operated.", "NO", "LOW", "NONE"),
            ("All safety interlocks were functional and verified before production started.", "NO", "LOW", "NONE"),
            ("The emergency stop button was tested and accessible to all operators.", "NO", "LOW", "NONE"),
            ("Permit-required work was authorized and all critical controls were verified.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("A machine was in operation but guard status was not explicitly mentioned.", "UNCERTAIN", "HIGH", "BARRIER_BYPASS"),
            ("Production continued but interlock functionality verification was unclear.", "UNCERTAIN", "MEDIUM", "BARRIER_BYPASS"),
        ],
    },

    # ===== PPE FAILURE =====
    "PPE_FAILURE": {
        "category": "PPE_FAILURE",
        "dangerous": [
            ("Worker entered a hazardous area without required personal protective equipment.", "YES", "HIGH", "PPE_FAILURE"),
            ("An operator performed a noisy task without hearing protection.", "YES", "MEDIUM", "PPE_FAILURE"),
            ("Chemical handling occurred without chemical-resistant gloves or apron.", "YES", "HIGH", "PPE_FAILURE"),
            ("A worker entered a dust-filled area without a respirator.", "YES", "MEDIUM", "PPE_FAILURE"),
            ("Eye protection was not worn during grinding or cutting operations.", "YES", "MEDIUM", "PPE_FAILURE"),
        ],
        "safe": [
            ("No PPE violation occurred; the worker used all required protective equipment.", "NO", "LOW", "NONE"),
            ("Personnel wore properly fitted respirators in all hazardous atmospheres.", "NO", "LOW", "NONE"),
            ("All workers had appropriate hearing protection in noise-controlled areas.", "NO", "LOW", "NONE"),
            ("PPE inventory was checked and all equipment was certified and functional.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("A hazardous task was performed but PPE usage was not explicitly documented.", "UNCERTAIN", "MEDIUM", "PPE_FAILURE"),
            ("A noisy environment was mentioned but hearing protection status was unclear.", "UNCERTAIN", "MEDIUM", "PPE_FAILURE"),
        ],
    },

    # ===== INSPECTION / PERMIT FAILURES =====
    "INSPECTION_FAILURE": {
        "category": "INSPECTION_FAILURE",
        "dangerous": [
            ("Equipment was operated without proof of required inspection or certification.", "YES", "HIGH", "INSPECTION_FAILURE"),
            ("A forklift was used despite it being marked for maintenance or out-of-service.", "YES", "MEDIUM", "INSPECTION_FAILURE"),
            ("Electrical equipment was used in a wet area without ground fault protection testing.", "YES", "HIGH", "INSPECTION_FAILURE"),
            ("Scaffolding was erected without a qualified person inspection.", "YES", "HIGH", "INSPECTION_FAILURE"),
        ],
        "safe": [
            ("All equipment had current inspection tags and certification documents.", "NO", "LOW", "NONE"),
            ("Daily equipment checks were logged before any work commenced.", "NO", "LOW", "NONE"),
            ("Electrical systems were tested and verified for proper grounding.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Equipment was used but current inspection status was not documented.", "UNCERTAIN", "MEDIUM", "INSPECTION_FAILURE"),
            ("A task was performed but verification of required certifications was unclear.", "UNCERTAIN", "MEDIUM", "INSPECTION_FAILURE"),
        ],
    },

    # ===== GENERAL SAFETY COMPLIANCE =====
    "NONE": {
        "category": "NONE",
        "dangerous": [
            ("Worker was injured during an unsafe act without intervention or first aid.", "YES", "HIGH", "NONE"),
        ],
        "safe": [
            ("Routine housekeeping completed in the office; access routes were clear and no hazards were observed.", "NO", "LOW", "NONE"),
            ("Worker wore the required PPE and completed the assigned task under normal controlled conditions.", "NO", "LOW", "NONE"),
            ("Employee attended the morning safety meeting and reviewed procedures.", "NO", "LOW", "NONE"),
            ("Routine inspection found good housekeeping and all machine guards in place.", "NO", "LOW", "NONE"),
            ("A minor first aid cut was treated and no serious hazard was present.", "NO", "LOW", "NONE"),
            ("The work area was clean, barriers were intact, and no unsafe condition was identified.", "NO", "LOW", "NONE"),
            ("Workers completed a toolbox talk before a routine maintenance task with controls verified.", "NO", "LOW", "NONE"),
            ("Normal office work continued with clear walkways and no exposure to hazardous energy.", "NO", "LOW", "NONE"),
            ("The operator used the approved procedure and confirmed all safeguards before starting.", "NO", "LOW", "NONE"),
            ("A safety observation confirmed proper housekeeping, PPE use, and supervision.", "NO", "LOW", "NONE"),
        ],
        "ambiguous": [
            ("Work was completed but incident status was not explicitly documented.", "UNCERTAIN", "LOW", "NONE"),
            ("An observation was made but hazard details were not provided.", "UNCERTAIN", "LOW", "NONE"),
        ],
    },
}

def create_variations(text, suffix):
    """Create linguistic variations of a report text."""
    variations = [text]
    
    # Variation 1: Replace "worker/employee/operator" with alternatives
    alternatives = {
        "worker": ["personnel", "employee", "technician", "operator"],
        "employee": ["worker", "personnel", "operator", "technician"],
        "operator": ["worker", "technician", "personnel", "employee"],
        "technician": ["worker", "operator", "maintenance personnel", "service technician"],
    }
    
    for word, alts in alternatives.items():
        if word in text.lower():
            for alt in alts[:1]:  # Just one variation per word
                variant = text.replace(word, alt).replace(word.capitalize(), alt.capitalize())
                variant = text.replace(word.title(), alt.title())
                variations.append(variant)
            break
    
    # Variation 2: Add date/timestamp variants
    date_variants = [" on June 15", " during the morning shift", " at 2:30 PM", " during routine operations"]
    if len(variations) < 5:
        variant = text + date_variants[suffix % len(date_variants)]
        variations.append(variant)
    
    # Variation 3: Add location variants
    location_variants = [" in the maintenance area", " near the production floor", " at the facility", " in the electrical room"]
    if len(variations) < 5:
        variant = text + location_variants[suffix % len(location_variants)]
        variations.append(variant)
    
    # Variation 4: Passive voice if active
    if " was " not in text.lower() and "without" in text.lower():
        # Extract key elements and rephrase
        variant = text.replace("Worker", "The worker").replace("An ", "The ")
        if variant != text:
            variations.append(variant)
    
    return variations

def generate_expanded_dataset():
    """Generate 700+ records with balanced distribution."""
    
    rows = []
    
    # Process each hazard category
    for category_key, category_data in SCENARIOS.items():
        category = category_data["category"]
        
        # Add dangerous scenarios with multiple variations
        for idx, (dangerous_text, sif_status, risk_level, control_failure) in enumerate(category_data["dangerous"]):
            rows.append({
                "report_text": dangerous_text,
                "sif_status": sif_status,
                "risk_level": risk_level,
                "hazard_category": category,
                "control_failure": control_failure,
            })
            
            # Add 1-2 linguistic variations per dangerous scenario
            variations = create_variations(dangerous_text, idx)
            for variant in variations[1:3]:  # Take 1-2 variations max
                if variant != dangerous_text and len(rows) < 600:
                    rows.append({
                        "report_text": variant,
                        "sif_status": sif_status,
                        "risk_level": risk_level,
                        "hazard_category": category,
                        "control_failure": control_failure,
                    })
        
        # Add safe scenarios with variations
        for idx, (safe_text, sif_status, risk_level, control_failure) in enumerate(category_data["safe"]):
            rows.append({
                "report_text": safe_text,
                "sif_status": sif_status,
                "risk_level": risk_level,
                "hazard_category": category,
                "control_failure": control_failure,
            })
            
            # Add 1 variation per safe scenario
            variations = create_variations(safe_text, idx)
            for variant in variations[1:2]:
                if variant != safe_text and len(rows) < 700:
                    rows.append({
                        "report_text": variant,
                        "sif_status": sif_status,
                        "risk_level": risk_level,
                        "hazard_category": category,
                        "control_failure": control_failure,
                    })
        
        # Add ambiguous scenarios
        for idx, (ambiguous_text, sif_status, risk_level, control_failure) in enumerate(category_data["ambiguous"]):
            rows.append({
                "report_text": ambiguous_text,
                "sif_status": sif_status,
                "risk_level": risk_level,
                "hazard_category": category,
                "control_failure": control_failure,
            })
    
    # Shuffle to mix categories
    shuffle(rows)
    
    # Limit to reasonable size
    return rows[:750]

def main():
    root = Path(__file__).resolve().parent.parent  # Go up to project root
    data_path = root / "data" / "training_reports.csv"
    
    rows = generate_expanded_dataset()
    
    # Write CSV
    with open(data_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["report_text", "sif_status", "risk_level", "hazard_category", "control_failure"])
        writer.writeheader()
        writer.writerows(rows)
    
    # Print summary
    yes_count = sum(1 for r in rows if r["sif_status"] == "YES")
    no_count = sum(1 for r in rows if r["sif_status"] == "NO")
    uncertain_count = sum(1 for r in rows if r["sif_status"] == "UNCERTAIN")
    
    print(f"\n✓ Generated {len(rows)} training records")
    print(f"  - YES (dangerous):    {yes_count} ({100*yes_count/len(rows):.1f}%)")
    print(f"  - NO (safe):          {no_count} ({100*no_count/len(rows):.1f}%)")
    print(f"  - UNCERTAIN:          {uncertain_count} ({100*uncertain_count/len(rows):.1f}%)")
    print(f"\nSaved to: {data_path}")

if __name__ == "__main__":
    main()
