from erk_scripts import lib

def create_operation_categories(erkscript):
    categories = [
        {
            "code": "SECURITE",
            "name": "SECURITE",
            "description": "Opérations de sécurité",
            "color_code": "#4ECDC4",
            "icon_name": "security",
        },
        {
            "code": "HYDRIQUE",
            "name": "HYDRIQUE",
            "description": "Opérations à propos des eaux (fuite, inondation, infiltration...)",
            "color_code": "#4ECDC4",
            "icon_name": "security",
        },
        {
            "code": "ELECTRICITE",
            "name": "ELECTRICITE",
            "description": "Opérations de sécurité",
            "color_code": "#45B7D1",
            "icon_name": "light",
        },
        {
            "code": "WIFI",
            "name": "WIFI",
            "description": "Opérations sur le WIFI",
            "color_code": "#96CEB4",
            "icon_name": "wifi",
        },
        {
            "code": "EQUIPEMENT",
            "name": "EQUIPEMENT",
            "description": "Opérations sur un equipement quelconque",
            "color_code": "#96CEB4",
            "icon_name": "equipment",
        },
        {
            "code": "PROPRETE",
            "name": "PROPRETE",
            "description": "Opérations de nettoyage/propreté",
            "color_code": "#96CEB4",
            "icon_name": "cleaning",
        },
        {
            "code": "AUTRE",
            "name": "AUTRE",
            "description": "Opérations sans catégorie quelconque",
            "color_code": "#96CEB4",
            "icon_name": "other",
        },
    ]

    erkscript.add_operation_categories(categories)

def create_operation_types(erkscript):
    operation_categories = erkscript.get_operation_categories()

    operation_types = []

    for category in operation_categories:
        operation_types.append(
            {
                "name": "SIGNALEMENT",
                "code": f"SIG-{category.get("code")}",
                "category_id": category.get("id"),
                "sla_hours": 72,
                "color_code": "#2196F3",
                "is_active": True
            }
        )

    erkscript.add_operation_types(operation_types)

def create_tenants(erkscript):
    tenant_users = erkscript.get_tenants_users()

    tenants = []

    for tenant_user in tenant_users:
        tenants.append({
            "user_id": tenant_user.get("id"),
        })

    erkscript.add_tenants(tenants)

def create_buildings(erkscript):
    buildings = [
        {
            "name": "Eureka",
            "code": "ERK",
            "address": "Eyang",
            "floors_count": 1,
            "construction_year": 2025
        }
    ]

    erkscript.add_buildings(buildings)

def create_floors(erkscript):
    # Get one/many buildings
    res = erkscript.get_buildings({ "search": "Eureka" })
    eureka_buildings = res[0]

    eureka_floors = [
        {
            "building": eureka_buildings.get("id"),
            "number": 0,
            "chemical_code": "H",
            "name": "Hydrogène",
        },
        {
            "building": eureka_buildings.get("id"),
            "number": 1,
            "chemical_code": "N",
            "name": "Azote",
        }
    ]

    erkscript.add_floors(eureka_floors)

def create_unit_types(erkscript):
    unit_types = [
        {
            "name": "Cage d'escalier",
            "code": "CAGE_ESCALIER",
            "is_rentable": False,
            "color_display": "#2196F3",
        },
        {
            "name": "Chambre",
            "code": "CHAMBRE",
            "is_rentable": True,
            "color_display": "#2196F3",
        },
        {
            "name": "Couloir",
            "code": "COULOIR",
            "is_rentable": False,
            "color_display": "#2196F3",
        },
        {
            "name": "Local Technique",
            "code": "LOCAL_TECHNIQUE",
            "is_rentable": False,
            "color_display": "#2196F3",
        },
        {
            "name": "Point d'accès WIFI",
            "code": "POINT_ACCESS_WIFI",
            "is_rentable": False,
            "color_display": "#2196F3",
        },
        {
            "name": "Salle d'étude",
            "code": "SALLE_ETUDE",
            "is_rentable": False,
            "color_display": "#2196F3",
        },
    ]
    erkscript.add_unit_types(unit_types)

def create_units(erkscript):
    users = erkscript.get_tenants_users()
    res = erkscript.get_buildings({"search": "Eureka"})
    eureka_buildings = res[0]
    floors = erkscript.get_floors({ "building": eureka_buildings.get("id") })

    # Unit types
    ut_cage_escalier = erkscript.get_unit_types({ "search": "CAGE_ESCALIER" })[0]
    ut_couloir = erkscript.get_unit_types({ "search": "COULOIR" })[0]
    ut_chambre = erkscript.get_unit_types({ "search": "CHAMBRE" })[0]
    ut_local_technique = erkscript.get_unit_types({ "search": "LOCAL_TECHNIQUE" })[0]
    ut_point_access_wifi = erkscript.get_unit_types({ "search": "POINT_ACCESS_WIFI" })[0]

    """
    units = [
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_chambre.get("id"),
            "identifier": "ERK-H1",
            "name": f"Salle d'étude - Eureka RDC",
            "current_status": "OCCUPIED"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_point_access_wifi.get("id"),
            "identifier": f"ERK-H-1",
            "name": f"Point d'accès WIFI N°1 - EUREKA RDC",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_point_access_wifi.get("id"),
            "identifier": f"ERK-H-2",
            "name": f"Point d'accès WIFI N°2 - EUREKA RDC",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_local_technique.get("id"),
            "identifier": f"ERK-H10",
            "name": f"Local Technique - EUREKA RDC",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_couloir.get("id"),
            "identifier": f"ERK-H11",
            "name": f"Couloir - EUREKA RDC",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_cage_escalier.get("id"),
            "identifier": f"ERK-H12",
            "name": f"Cage d'escalier - EUREKA RDC",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[1].get("id"),
            "unit_type": ut_chambre.get("id"),
            "identifier": "ERK-N1",
            "name": f"Chambre N°1 - EUREKA Etage 1",
            "current_status": "OCCUPIED"
        },
        {
            "floor": floors[1].get("id"),
            "unit_type": ut_point_access_wifi.get("id"),
            "identifier": f"ERK-N-1",
            "name": f"Point d'accès WIFI N°1 - EUREKA Etage 1",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[0].get("id"),
            "unit_type": ut_point_access_wifi.get("id"),
            "identifier": f"ERK-N-2",
            "name": f"Point d'accès WIFI N°2 - EUREKA Etage 2",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[1].get("id"),
            "unit_type": ut_local_technique.get("id"),
            "identifier": f"ERK-N10",
            "name": f"Local Technique - EUREKA Etage 1",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[1].get("id"),
            "unit_type": ut_couloir.get("id"),
            "identifier": f"ERK-N11",
            "name": f"Couloir - EUREKA Etage 1",
            "current_status": "AVAILABLE"
        },
        {
            "floor": floors[1].get("id"),
            "unit_type": ut_cage_escalier.get("id"),
            "identifier": f"ERK-N12",
            "name": f"Cage d'escalier - EUREKA Etage 1",
            "current_status": "AVAILABLE"
        },
    ]
    
        for user in users:
        is_rdc = "eureka-h" in user.get("email")
        floor_id = floors[0].get("id") if is_rdc else floors[1].get("id")
        current_occupant_id = user.get("id")

        room_from_email = user.get("email").split('-')[1].split('@')[0]
        room_id = f"ERK-{room_from_email.upper()}"
        room_name = f"Chambre N°{room_from_email[1]} - EUREKA {"RDC" if is_rdc else "Etage 1"}"

        units.append({
            "floor": floor_id,
            "unit_type": ut_chambre.get("id"),
            "identifier": room_id,
            "name": room_name,
            "current_status": "OCCUPIED",
            "current_occupant": current_occupant_id,
            "area_m2": 15
        })

    """

    units = []

    for user in range(1, 10):
        is_rdc = "eureka-h" in user.get("email")
        floor_id = floors[0].get("id") if is_rdc else floors[1].get("id")
        current_occupant_id = user.get("id")

        room_from_email = user.get("email").split('-')[1].split('@')[0]
        room_id = f"ERK-{room_from_email.upper()}"
        room_name = f"Chambre N°{room_from_email[1]} - EUREKA {"RDC" if is_rdc else "Etage 1"}"

        units.append({
            "floor": floor_id,
            "unit_type": ut_chambre.get("id"),
            "identifier": room_id,
            "name": room_name,
            "current_status": "OCCUPIED",
            "current_occupant": current_occupant_id,
            "area_m2": 15
        })

    erkscript.add_units(units)

def create_users(erkscript):
    erkscript.add_users_from_xls_file('COMPTES_EUREKANET.xlsx')

def create_contacts(erkscript):
    contacts = [
        {
            "first_name": "N/A",
            "last_name": "N/A",
            "phone_number": "+237 6 90 19 14 04",
            "type": "STAFF",
            "organization": "Eureka Résidences",
            "position": "Gestionnaire Principal",
            "is_public": True,
            "is_emergency_contact": False,
        },
        {
            "first_name": "Jean",
            "last_name": "N/A",
            "phone_number": "+237 6 40 58 09 03",
            "type": "STAFF",
            "organization": "Eureka Résidences",
            "position": "Gardien",
            "is_public": True,
            "is_emergency_contact": False,
        },
        {
            "first_name": "N/A",
            "last_name": "N/A",
            "phone_number": "117",
            "type": "EMERGENCY",
            "organization": "Cameroun",
            "position": "Police",
            "is_public": True,
            "is_emergency_contact": True,
        },
        {
            "first_name": "N/A",
            "last_name": "N/A",
            "phone_number": "120",
            "type": "EMERGENCY",
            "organization": "Cameroun",
            "position": "Gendarmerie",
            "is_public": True,
            "is_emergency_contact": True,
        },
        {
            "first_name": "N/A",
            "last_name": "N/A",
            "phone_number": "118",
            "type": "EMERGENCY",
            "organization": "Cameroun",
            "position": "Pompiers",
            "is_public": True,
            "is_emergency_contact": True,
        },
    ]

    erkscript.add_contacts(contacts)

def main():
    erkscript = ERKSCRIPTS("https://prod-backend.eureka-residences.com/")

    # Credentials - À MODIFIER
    erkscript.authenticate({"email": "wilfried@eurekanet.com", "password": "mon_super_motdepasse"})

    # create_users(erkscript)
    # create_buildings(erkscript)
    # create_floors(erkscript)
    # create_unit_types(erkscript)
    # create_units(erkscript)
    # create_operation_categories(erkscript)
    # create_operation_types(erkscript)
    # create_contacts(erkscript)
    # create_tenants(erkscript)


if __name__ == "__main__":
    main()
