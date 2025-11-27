import requests
from pprint import pprint
import pandas as pd
import re

class ERKSCRIPTS:
    # Configuration de l'URL de base
    BASE_URL = ""

    # Headers par défaut
    headers = {
        "Content-Type": "application/json",
    }

    # Variables globales pour stocker les tokens et IDs de test
    access_token = None
    refresh_token = None
    test_ids = {}

    def __init__(self, base_url: str = "Oh ! Change l'url ci dans le contructeur"):
        self.BASE_URL = base_url

    def authenticate(self, credentials: dict[str, str]) -> None:
        # Login
        response = requests.post(
            f"{self.BASE_URL}api/auth/jwt/create/", json=credentials, headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access")
            refresh_token = data.get("refresh")

            # Mettre à jour les headers avec le token
            self.headers["Authorization"] = f"Bearer {access_token}"

            print("✅ Authentification réussie!")
            print(f"Access Token: {access_token[:50]}")
        else:
            print(f"❌ Erreur d'authentification: {response.status_code}")
            print(response.json())

    def verify_connection(self) -> None:
        response = requests.get(f"{self.BASE_URL}api/auth/users/me/", headers=self.headers)

        if response.status_code == 200:
            user_data = response.json()
            print("✅ Utilisateur connecté:")
            pprint(user_data)
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(response.json())


    default_erk_account_columns = {
        'last_name': 'Nom Etudiant(e)',
        'first_name': 'Prénom Etudiant(e)',
        'room_id': 'Identifiant EurekaNet',
        'password': 'Mot de passe par défaut'
    }

    def get_users_from_xls_file(self, xls_file: str = 'COMPTES_EUREKANET.xlsx', cols: dict[str, str] = default_erk_account_columns) -> list:
        users = []
        try:
            df = pd.read_excel(xls_file)

            # Rename columns
            df_renamed = df.rename(columns={v: k for k, v in cols.items()})

            for _, row in df_renamed.iterrows():
                user = {
                    'last_name': row.get('last_name', ''),
                    'first_name': row.get('first_name', ''),
                    'room_id': row.get('room_id', ''),
                    'password': row.get('password', '')
                }
                users.append(user)

            return users
        except Exception as e:
            print(f"Erreur: {e}")
            return []

    def add_users_from_xls_file(self, xls_file: str, cols: dict[str, str] = default_erk_account_columns) -> bool:
        users = self.get_users_from_xls_file(xls_file, cols)
        total_users = len(users)
        success = 0

        for user in users:
            user_data = {
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'email': f'{user["room_id"]}@eurekanet.com',
                'password': user['password'],
                're_password': user['password'],
            }

            try:

                response = requests.post(f"{self.BASE_URL}api/auth/users/", json=user_data, headers=self.headers, timeout=30)

                if response.status_code in [200, 201]:
                    print(f"✅ Utilisateur {user_data['first_name']} {user_data['last_name']} créé avec succès")
                    success += 1
                else:
                    print(f"❌ Erreur pour {user_data['first_name']} {user_data['last_name']}: {response.status_code}")
                    print(f"Détails: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Erreur réseau pour {user_data['first_name']} {user_data['last_name']}: {e}")

        return success != 0

    def add_operation_type(self, operation_type_data: dict) -> bool:
        """
        Crée un nouveau type d'opération dans le système

        Args:
            operation_type_data (dict): Les données du type d'opération à créer
                Doit contenir au minimum:
                - name (str): Nom du type d'opération
                - code (str): Code unique du type d'opération
                - category (str): Catégorie métier (MAINTENANCE, SECURITY, etc.)
        """

        # Structure de base attendue par l'API
        payload = {
            "name": operation_type_data.get("name"),
            "code": operation_type_data.get("code"),
            "category": operation_type_data.get("category"),
            "description": operation_type_data.get("description", ""),
            "requires_approval": operation_type_data.get("requires_approval", False),
            "auto_assign_rules": operation_type_data.get("auto_assign_rules", {}),
            "default_priority": operation_type_data.get("default_priority", "NORMAL"),
            "sla_hours": operation_type_data.get("sla_hours"),
            "color_code": operation_type_data.get("color_code", "#808080"),
            "icon_name": operation_type_data.get("icon_name", "settings"),
            "is_active": operation_type_data.get("is_active", True)
        }

        # Validation des champs obligatoires
        if not payload["name"] or not payload["code"] or not payload["category"]:
            print("❌ Erreur: name, code et category sont obligatoires")
            return False

        try:
            response = requests.post(f"{self.BASE_URL}api/operations/types/", json=payload, headers=self.headers, timeout=30)

            if response.status_code in [200, 201]:
                data = response.json()
                operation_type_id = data.get("id")
                print(f"✅ Type d'opération '{payload['name']}' créé avec succès (ID: {operation_type_id})")

                # Stocker l'ID pour référence future
                self.test_ids[payload["code"]] = operation_type_id
                return True

            else:
                print(f"❌ Erreur lors de la création du type d'opération: {response.status_code}")
                print(f"Détails: {response.text}")

                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return True

    def add_operation_types(self, operation_types: list[dict]) -> bool:
        success = True
        failed_operation_types = []

        for operation_type in operation_types:
            is_current_operation_success = self.add_operation_type(operation_type)

            if not is_current_operation_success:
                failed_operation_types.append(operation_type)

            success = success and is_current_operation_success

        if success:
            print("Toutes les opérations ont bien été enregistrées !")
        else:
            more_than_one = len(failed_operation_types) > 1
            print(f"Erreur lors de l'enregistrement {"des" if more_than_one else "du"} operation{"s" if more_than_one else ""}.")

        return success

    def add_unit(self, unit_data: dict) -> bool:
        """
        Crée une nouvelle unitée gérée dans le système

        Args:
            unit_data (dict): Les données de l'unité gérée à créer
                Doit contenir au minimum:
                - floor (str): Etage de l'unité
                - unit_type (str): Code de l'unité
                - identifier (str): Le nom de l'unité gérée
        """

        # Structure de base attendue par l'API
        payload = {
            "floor": unit_data.get("floor"),
            "unit_type": unit_data.get("unit_type"),
            "parent": unit_data.get("parent"),
            "identifier": unit_data.get("identifier"),
            "name": unit_data.get("name"),
            "area_m2": unit_data.get("area_m2"),
            "current_status": unit_data.get("current_status", "AVAILABLE"),
            "monthly_rent": unit_data.get("monthly_rent", "65000"),
            "current_occupant": unit_data.get("current_occupant"),
            "occupation_start_date": unit_data.get("occupation_start_date"),
            "is_active": unit_data.get("is_active", True),
        }


        # Validation des champs obligatoires
        if not payload["floor"] or not payload["unit_type"] or not payload["identifier"]:
            print("❌ Erreur: floor, unit_type et identifier sont obligatoires")
            return False

        try:
            response = requests.post(f"{self.BASE_URL}api/patrimoine/units/", json=payload, headers=self.headers,
                                     timeout=30)

            if response.status_code in [200, 201]:
                data = response.json()
                unit_id = data.get("id")
                print(f"✅ Type d'unité gérée '{payload['identifier']}' créé avec succès (ID: {unit_id})")

                return True

            else:
                print(f"❌ Erreur lors de la création de l'unité : {response.status_code}")
                print(f"Détails: {response.text}")

                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return True

    def add_units(self, units: list[dict]) -> bool:
        success = True
        failed_units = []

        for unit in units:
            is_current_unit_success = self.add_unit(unit)

            if not is_current_unit_success:
                failed_units.append(unit)

            success = success and is_current_unit_success

        if success:
            print("Toutes les opérations ont bien été enregistrées !")
        else:
            more_than_one = len(failed_units) > 1
            print(f"Erreur lors de l'enregistrement {"des" if more_than_one else "du"} operation{"s" if more_than_one else ""}.")

        return success

    def get_unit_types(self, params: dict = None) -> list:
        """
        Récupère tous les types d'unités (étages) selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - is_composite (str): Filtre par type composite
                - is_rentable (str): Filtre par type louable
                - is_active (str): Filtre par statut actif
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des types d'unités
        """

        try:
            response = requests.get(
                f"{self.BASE_URL}api/patrimoine/unit-types/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                unit_types = data.get("results", [])
                print(f"✅ {len(unit_types)} type(s) d'unité(s) récupéré(s) avec succès")
                return unit_types
            else:
                print(f"❌ Erreur lors de la récupération des types d'unités: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def get_floors(self, params: dict = None) -> list:
        """
        Récupère tous les étages selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - building (str): Filtre par bâtiment
                - is_active (str): Filtre par statut actif
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des étages
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/patrimoine/floors/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                floors = data.get("results", [])
                print(f"✅ {len(floors)} étage(s) récupéré(s) avec succès")
                return floors
            else:
                print(f"❌ Erreur lors de la récupération des étages: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def add_tenant(self, tenant_data: dict) -> bool:
        """
        Crée un nouveau locataire dans le système

        Args:
            tenant_data (dict): Les données du locataire à créer
                Doit contenir au minimum:
                - user_id (str): UUID de l'utilisateur
                Peut contenir optionnellement:
                - current_unit_id (str): UUID de l'unité actuelle
                - move_in_date (str): Date d'entrée (format YYYY-MM-DD)
                - move_out_date (str): Date de sortie (format YYYY-MM-DD)
                - emergency_contact_name (str): Nom du contact d'urgence
                - emergency_contact_phone (str): Téléphone du contact d'urgence
                - notes (str): Notes internes

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "user_id": tenant_data.get("user_id"),
            "current_unit_id": tenant_data.get("current_unit_id"),
            "move_in_date": tenant_data.get("move_in_date"),
            "move_out_date": tenant_data.get("move_out_date"),
            "emergency_contact_name": tenant_data.get("emergency_contact_name"),
            "emergency_contact_phone": tenant_data.get("emergency_contact_phone"),
            "notes": tenant_data.get("notes", "")
        }

        # Validation du champ obligatoire
        if not payload["user_id"]:
            print("❌ Erreur: user_id est obligatoire")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/rental/tenants/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                tenant_id = data.get("user_id")
                print(f"✅ Locataire créé avec succès (User ID: {tenant_id})")
                return True
            else:
                print(f"❌ Erreur lors de la création du locataire: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_tenants(self, tenants: list[dict]) -> bool:
        """
        Crée plusieurs locataires

        Args:
            tenants (list[dict]): Liste des données des locataires à créer

        Returns:
            bool: True si tous les locataires ont été créés avec succès
        """
        success = True
        failed_tenants = []

        for tenant in tenants:
            is_current_tenant_success = self.add_tenant(tenant)

            if not is_current_tenant_success:
                failed_tenants.append(tenant)

            success = success and is_current_tenant_success

        if success:
            print("Tous les locataires ont bien été créés !")
        else:
            more_than_one = len(failed_tenants) > 1
            print(f"Erreur lors de la création de {'locataires' if more_than_one else 'locataire'}.")

        return success

    def get_users(self, params: dict = None) -> list:
        """
        Récupère tous les utilisateurs selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - page (int): Numéro de page

        Returns:
            list: Liste des utilisateurs
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/auth/users/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                users = data.get("results", [])
                print(f"✅ {len(users)} utilisateur(s) récupéré(s) avec succès")
                return users
            else:
                print(f"❌ Erreur lors de la récupération des utilisateurs: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def get_tenants_users(self, params: dict = None) -> list:
        """
        Récupère uniquement les utilisateurs qui sont des locataires

        Args:
            params (dict): Paramètres de filtrage optionnels
                - page (int): Numéro de page

        Returns:
            list: Liste des utilisateurs locataires
        """
        try:
            # Récupérer tous les utilisateurs
            all_users = self.get_users(params)

            # Filtrer pour garder seulement les locataires
            tenants = [user for user in all_users if user.get('is_tenant') and not user.get('is_staff') and '@eurekanet.com' in user.get('email')]

            print(f"✅ {len(tenants)} utilisateur(s) locataire(s) trouvé(s)")
            return tenants

        except Exception as e:
            print(f"❌ Erreur lors du filtrage des locataires: {e}")
            return []

    def add_operation_category(self, category_data: dict) -> bool:
        """
        Crée une nouvelle catégorie d'opérations dans le système

        Args:
            category_data (dict): Les données de la catégorie à créer
                Doit contenir au minimum:
                - code (str): Code unique de la catégorie
                - name (str): Nom de la catégorie
                Peut contenir optionnellement:
                - description (str): Description de la catégorie
                - color_code (str): Code couleur hexadécimal
                - icon_name (str): Nom de l'icône
                - sort_order (int): Ordre d'affichage
                - is_active (bool): Statut actif

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "code": category_data.get("code"),
            "name": category_data.get("name"),
            "description": category_data.get("description", ""),
            "color_code": category_data.get("color_code", "#808080"),
            "icon_name": category_data.get("icon_name", "settings"),
            "sort_order": category_data.get("sort_order", 0),
            "is_active": category_data.get("is_active", True)
        }

        # Validation des champs obligatoires
        if not payload["code"] or not payload["name"]:
            print("❌ Erreur: code et name sont obligatoires")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/operations/categories/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                category_id = data.get("id")
                print(f"✅ Catégorie d'opération '{payload['name']}' créée avec succès (ID: {category_id})")

                # Stocker l'ID pour référence future
                self.test_ids[payload["code"]] = category_id
                return True

            else:
                print(f"❌ Erreur lors de la création de la catégorie d'opération: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_operation_categories(self, categories: list[dict]) -> bool:
        """
        Crée plusieurs catégories d'opérations

        Args:
            categories (list[dict]): Liste des données des catégories à créer

        Returns:
            bool: True si toutes les catégories ont été créées avec succès
        """
        success = True
        failed_categories = []

        for category in categories:
            is_current_category_success = self.add_operation_category(category)

            if not is_current_category_success:
                failed_categories.append(category)

            success = success and is_current_category_success

        if success:
            print("Toutes les catégories d'opérations ont bien été créées !")
        else:
            more_than_one = len(failed_categories) > 1
            print(f"Erreur lors de la création de {'catégories' if more_than_one else 'catégorie'}.")

        return success

    def add_building(self, building_data: dict) -> bool:
        """
        Crée un nouveau bâtiment dans le système

        Args:
            building_data (dict): Les données du bâtiment à créer
                Doit contenir au minimum:
                - name (str): Nom du bâtiment
                Peut contenir optionnellement:
                - code (str): Code court du bâtiment
                - address (str): Adresse complète
                - main_image (str): UUID de l'image principale
                - total_area_m2 (str): Surface totale en m²
                - floors_count (int): Nombre d'étages
                - construction_year (int): Année de construction
                - manager (str): UUID du gestionnaire
                - is_active (bool): Statut actif

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "name": building_data.get("name"),
            "code": building_data.get("code", ""),
            "address": building_data.get("address", ""),
            "main_image": building_data.get("main_image"),
            "total_area_m2": building_data.get("total_area_m2"),
            "floors_count": building_data.get("floors_count", 0),
            "construction_year": building_data.get("construction_year"),
            "manager": building_data.get("manager"),
            "is_active": building_data.get("is_active", True)
        }

        # Validation du champ obligatoire
        if not payload["name"]:
            print("❌ Erreur: name est obligatoire")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/patrimoine/buildings/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                building_id = data.get("id")
                print(f"✅ Bâtiment '{payload['name']}' créé avec succès (ID: {building_id})")

                # Stocker l'ID pour référence future
                self.test_ids[payload["name"]] = building_id
                return True

            else:
                print(f"❌ Erreur lors de la création du bâtiment: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_buildings(self, buildings: list[dict]) -> bool:
        """
        Crée plusieurs bâtiments

        Args:
            buildings (list[dict]): Liste des données des bâtiments à créer

        Returns:
            bool: True si tous les bâtiments ont été créés avec succès
        """
        success = True
        failed_buildings = []

        for building in buildings:
            is_current_building_success = self.add_building(building)

            if not is_current_building_success:
                failed_buildings.append(building)

            success = success and is_current_building_success

        if success:
            print("Tous les bâtiments ont bien été créés !")
        else:
            more_than_one = len(failed_buildings) > 1
            print(f"Erreur lors de la création de {'bâtiments' if more_than_one else 'bâtiment'}.")

        return success

    def get_buildings(self, params: dict = None) -> list:
        """
        Récupère tous les bâtiments selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - manager (str): Filtre par gestionnaire
                - is_active (str): Filtre par statut actif
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des bâtiments
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/patrimoine/buildings/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                buildings = data.get("results", [])
                print(f"✅ {len(buildings)} bâtiment(s) récupéré(s) avec succès")
                return buildings
            else:
                print(f"❌ Erreur lors de la récupération des bâtiments: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def add_floor(self, floor_data: dict) -> bool:
        """
        Crée un nouvel étage dans un bâtiment

        Args:
            floor_data (dict): Les données de l'étage à créer
                Doit contenir au minimum:
                - building (str): UUID du bâtiment
                - number (int): Numéro de l'étage
                - chemical_code (str): Code chimique de l'étage
                Peut contenir optionnellement:
                - name (str): Nom descriptif de l'étage
                - area_m2 (str): Surface en m²
                - floor_plan (str): UUID du plan de l'étage
                - is_active (bool): Statut actif

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "building": floor_data.get("building"),
            "number": floor_data.get("number"),
            "chemical_code": floor_data.get("chemical_code"),
            "name": floor_data.get("name", ""),
            "area_m2": floor_data.get("area_m2"),
            "floor_plan": floor_data.get("floor_plan"),
            "is_active": floor_data.get("is_active", True)
        }

        # Validation des champs obligatoires
        if not payload["building"] or payload["number"] is None or not payload["chemical_code"]:
            print("❌ Erreur: building, number et chemical_code sont obligatoires")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/patrimoine/floors/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                floor_id = data.get("id")
                floor_name = payload.get("name") or f"Étage {payload['number']}"
                print(f"✅ Étage '{floor_name}' créé avec succès (ID: {floor_id})")

                # Stocker l'ID pour référence future
                self.test_ids[f"floor_{payload['building']}_{payload['number']}"] = floor_id
                return True

            else:
                print(f"❌ Erreur lors de la création de l'étage: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_floors(self, floors: list[dict]) -> bool:
        """
        Crée plusieurs étages

        Args:
            floors (list[dict]): Liste des données des étages à créer

        Returns:
            bool: True si tous les étages ont été créés avec succès
        """
        success = True
        failed_floors = []

        for floor in floors:
            is_current_floor_success = self.add_floor(floor)

            if not is_current_floor_success:
                failed_floors.append(floor)

            success = success and is_current_floor_success

        if success:
            print("Tous les étages ont bien été créés !")
        else:
            more_than_one = len(failed_floors) > 1
            print(f"Erreur lors de la création de {'étages' if more_than_one else 'étage'}.")

        return success

    def get_floors(self, params: dict = None) -> list:
        """
        Récupère tous les étages selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - building (str): Filtre par bâtiment (UUID)
                - is_active (str): Filtre par statut actif
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des étages
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/patrimoine/floors/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                floors = data.get("results", [])
                print(f"✅ {len(floors)} étage(s) récupéré(s) avec succès")
                return floors
            else:
                print(f"❌ Erreur lors de la récupération des étages: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def add_unit_type(self, unit_type_data: dict) -> bool:
        """
        Crée un nouveau type d'unité dans le système

        Args:
            unit_type_data (dict): Les données du type d'unité à créer
                Doit contenir au minimum:
                - name (str): Nom du type d'unité
                - code (str): Code unique du type
                Peut contenir optionnellement:
                - description (str): Description détaillée
                - default_image (str): UUID de l'image par défaut
                - is_composite (bool): Si le type peut contenir des sous-unités
                - is_rentable (bool): Si le type peut être loué
                - color_display (str): Code couleur hexadécimal
                - sort_order (int): Ordre d'affichage
                - is_active (bool): Statut actif

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "name": unit_type_data.get("name"),
            "code": unit_type_data.get("code"),
            "description": unit_type_data.get("description", ""),
            "default_image": unit_type_data.get("default_image"),
            "is_composite": unit_type_data.get("is_composite", False),
            "is_rentable": unit_type_data.get("is_rentable", True),
            "color_display": unit_type_data.get("color_display", "#808080"),
            "sort_order": unit_type_data.get("sort_order", 0),
            "is_active": unit_type_data.get("is_active", True)
        }

        # Validation des champs obligatoires
        if not payload["name"] or not payload["code"]:
            print("❌ Erreur: name et code sont obligatoires")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/patrimoine/unit-types/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                unit_type_id = data.get("id")
                print(f"✅ Type d'unité '{payload['name']}' créé avec succès (ID: {unit_type_id})")

                # Stocker l'ID pour référence future
                self.test_ids[payload["code"]] = unit_type_id
                return True

            else:
                print(f"❌ Erreur lors de la création du type d'unité: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_unit_types(self, unit_types: list[dict]) -> bool:
        """
        Crée plusieurs types d'unités

        Args:
            unit_types (list[dict]): Liste des données des types d'unités à créer

        Returns:
            bool: True si tous les types d'unités ont été créés avec succès
        """
        success = True
        failed_unit_types = []

        for unit_type in unit_types:
            is_current_unit_type_success = self.add_unit_type(unit_type)

            if not is_current_unit_type_success:
                failed_unit_types.append(unit_type)

            success = success and is_current_unit_type_success

        if success:
            print("Tous les types d'unités ont bien été créés !")
        else:
            more_than_one = len(failed_unit_types) > 1
            print(f"Erreur lors de la création de {'types d\'unités' if more_than_one else 'type d\'unité'}.")

        return success

    def get_unit_types(self, params: dict = None) -> list:
        """
        Récupère tous les types d'unités selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - is_composite (str): Filtre par type composite
                - is_rentable (str): Filtre par type louable
                - is_active (str): Filtre par statut actif
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des types d'unités
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/patrimoine/unit-types/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                unit_types = data.get("results", [])
                print(f"✅ {len(unit_types)} type(s) d'unité(s) récupéré(s) avec succès")
                return unit_types
            else:
                print(f"❌ Erreur lors de la récupération des types d'unités: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def get_operation_categories(self, params: dict = None) -> list:
        """
        Récupère toutes les catégories d'opérations selon les paramètres spécifiés

        Args:
            params (dict): Paramètres de filtrage optionnels
                - is_active (str): Filtre par statut actif
                - code (str): Filtre par code de catégorie
                - search (str): Terme de recherche
                - ordering (str): Champ de tri
                - page (int): Numéro de page

        Returns:
            list: Liste des catégories d'opérations
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}api/operations/categories/",
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                categories = data.get("results", [])
                print(f"✅ {len(categories)} catégorie(s) d'opération(s) récupérée(s) avec succès")
                return categories
            else:
                print(f"❌ Erreur lors de la récupération des catégories d'opérations: {response.status_code}")
                print(f"Détails: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return []

    def add_operation_type(self, operation_type_data: dict) -> bool:
        """
        Crée un nouveau type d'opération dans le système

        Args:
            operation_type_data (dict): Les données du type d'opération à créer
                Doit contenir au minimum:
                - name (str): Nom du type d'opération
                - code (str): Code unique du type
                - category_id (str): UUID de la catégorie
                Peut contenir optionnellement:
                - description (str): Description détaillée
                - requires_approval (bool): Si une approbation est nécessaire
                - auto_assign_rules (dict): Règles d'assignation automatique
                - default_priority (str): Priorité par défaut
                - sla_hours (int): Temps de résolution en heures
                - color_code (str): Code couleur hexadécimal
                - icon_name (str): Nom de l'icône
                - default_icon (str): UUID de l'icône par défaut
                - is_active (bool): Statut actif

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "name": operation_type_data.get("name"),
            "code": operation_type_data.get("code"),
            "category_id": operation_type_data.get("category_id"),
            "description": operation_type_data.get("description", ""),
            "requires_approval": operation_type_data.get("requires_approval", False),
            "auto_assign_rules": operation_type_data.get("auto_assign_rules", {}),
            "default_priority": operation_type_data.get("default_priority", "NORMAL"),
            "sla_hours": operation_type_data.get("sla_hours"),
            "color_code": operation_type_data.get("color_code", "#808080"),
            "icon_name": operation_type_data.get("icon_name", "settings"),
            "default_icon": operation_type_data.get("default_icon"),
            "is_active": operation_type_data.get("is_active", True)
        }

        # Validation des champs obligatoires
        if not payload["name"] or not payload["code"] or not payload["category_id"]:
            print("❌ Erreur: name, code et category_id sont obligatoires")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/operations/types/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                operation_type_id = data.get("id")
                print(f"✅ Type d'opération '{payload['name']}' créé avec succès (ID: {operation_type_id})")

                # Stocker l'ID pour référence future
                self.test_ids[payload["code"]] = operation_type_id
                return True

            else:
                print(f"❌ Erreur lors de la création du type d'opération: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_operation_types(self, operation_types: list[dict]) -> bool:
        """
        Crée plusieurs types d'opérations

        Args:
            operation_types (list[dict]): Liste des données des types d'opérations à créer

        Returns:
            bool: True si tous les types d'opérations ont été créés avec succès
        """
        success = True
        failed_operation_types = []

        for operation_type in operation_types:
            is_current_operation_type_success = self.add_operation_type(operation_type)

            if not is_current_operation_type_success:
                failed_operation_types.append(operation_type)

            success = success and is_current_operation_type_success

        if success:
            print("Tous les types d'opérations ont bien été créés !")
        else:
            more_than_one = len(failed_operation_types) > 1
            print(f"Erreur lors de la création de {'types d\'opérations' if more_than_one else 'type d\'opération'}.")

        return success

    def add_contact(self, contact_data: dict) -> bool:
        """
        Crée un nouveau contact dans le système

        Args:
            contact_data (dict): Les données du contact à créer
                Doit contenir au minimum:
                - first_name (str): Prénom du contact
                - last_name (str): Nom du contact
                - phone_number (str): Numéro de téléphone principal
                Peut contenir optionnellement:
                - type (str): Type de contact
                - organization (str): Organisation/entreprise
                - position (str): Fonction/Poste
                - department (str): Service/Département
                - phone_number_secondary (str): Téléphone secondaire
                - whatsapp_number (str): Numéro WhatsApp
                - email (str): Adresse email
                - address (str): Adresse physique
                - availability_info (str): Informations de disponibilité
                - priority (int): Priorité d'affichage
                - is_public (bool): Visible par tous les résidents
                - is_emergency_contact (bool): Contact d'urgence
                - is_active (bool): Statut actif
                - buildings (list): Liste d'UUID des bâtiments
                - notes (str): Notes internes
                - display_order (int): Ordre d'affichage

        Returns:
            bool: True si la création a réussi, False sinon
        """
        # Structure de base attendue par l'API
        payload = {
            "first_name": contact_data.get("first_name"),
            "last_name": contact_data.get("last_name"),
            "phone_number": contact_data.get("phone_number"),
            "type": contact_data.get("type", "OTHER"),
            "organization": contact_data.get("organization", ""),
            "position": contact_data.get("position", ""),
            "department": contact_data.get("department", ""),
            "phone_number_secondary": contact_data.get("phone_number_secondary"),
            "whatsapp_number": contact_data.get("whatsapp_number"),
            "email": contact_data.get("email"),
            "address": contact_data.get("address", ""),
            "availability_info": contact_data.get("availability_info", ""),
            "priority": contact_data.get("priority", 2),
            "is_public": contact_data.get("is_public", True),
            "is_emergency_contact": contact_data.get("is_emergency_contact", False),
            "is_active": contact_data.get("is_active", True),
            "buildings": contact_data.get("buildings", []),
            "notes": contact_data.get("notes", ""),
            "display_order": contact_data.get("display_order", 0)
        }

        # Validation des champs obligatoires
        if not payload["first_name"] or not payload["last_name"] or not payload["phone_number"]:
            print("❌ Erreur: first_name, last_name et phone_number sont obligatoires")
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}api/contacts/",
                json=payload,
                headers=self.headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                data = response.json()
                contact_id = data.get("id")
                print(f"✅ Contact '{payload['first_name']} {payload['last_name']}' créé avec succès (ID: {contact_id})")

                # Stocker l'ID pour référence future
                self.test_ids[f"contact_{payload['first_name']}_{payload['last_name']}"] = contact_id
                return True

            else:
                print(f"❌ Erreur lors de la création du contact: {response.status_code}")
                print(f"Détails: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return False

    def add_contacts(self, contacts: list[dict]) -> bool:
        """
        Crée plusieurs contacts

        Args:
            contacts (list[dict]): Liste des données des contacts à créer

        Returns:
            bool: True si tous les contacts ont été créés avec succès
        """
        success = True
        failed_contacts = []

        for contact in contacts:
            is_current_contact_success = self.add_contact(contact)

            if not is_current_contact_success:
                failed_contacts.append(contact)

            success = success and is_current_contact_success

        if success:
            print("Tous les contacts ont bien été créés !")
        else:
            more_than_one = len(failed_contacts) > 1
            print(f"Erreur lors de la création de {'contacts' if more_than_one else 'contact'}.")

        return success
