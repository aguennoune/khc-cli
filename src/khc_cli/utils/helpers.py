"""Utility functions for khc CLI."""

import re
import time
import base64
import logging
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
from rich.console import Console
from datetime import datetime
from khc_cli.awesomecure.awesome2py import AwesomeList
console = Console()
LOGGER = logging.getLogger(__name__)

def countdown(t):
    """Compte à rebours visuel dans la console."""
    while t:
        mins, secs = divmod(int(t), 60)
        timeformat = "{:02d}:{:02d}".format(mins, secs)
        console.print(timeformat, end="\r")
        time.sleep(1)
        t -= 1
    console.print("\n\n\n\n\n")

def crawl_github_dependents(repo, page_num):
    """Récupère les dépendants d'un repo GitHub."""
    url = 'https://github.com/{}/network/dependents'.format(repo)
    dependents_data = []
    list_end = False
    
    for i in range(page_num):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")

            page_data = []
            for t in soup.findAll("div", {"class": "Box-row"}):
                repo_owner_elem = t.find('a', {"data-repository-hovercards-enabled":""})
                repo_name_elem = t.find('a', {"data-hovercard-type":"repository"})
                
                # Vérifier que les deux éléments existent avant d'accéder à leur attribut text
                if repo_owner_elem and repo_name_elem:
                    dependent = "{}/{}".format(repo_owner_elem.text, repo_name_elem.text)
                    page_data.append(dependent)
            
            for dependent in page_data:
                if dependent in dependents_data:
                    list_end = True 
            
            if list_end:
                break
            else:    
                dependents_data.extend(page_data)
            
            # Traitement de la pagination
            paginationContainer = None
            try:
                pagination_div = soup.find("div", {"class":"paginate-container"})
                if pagination_div:
                    paginationContainer = pagination_div.find_all('a')
            except Exception as e:
                LOGGER.debug(f"Erreur lors de la récupération de la pagination: {e}")
                break
            
            if not paginationContainer:
                break
                
            try:
                if len(paginationContainer) > 1:
                    paginationContainer = paginationContainer[1]
                else:
                    paginationContainer = paginationContainer[0]
            except Exception as e:
                LOGGER.debug(f"Erreur lors du traitement de la pagination: {e}")
                break
            
            if paginationContainer and "href" in paginationContainer.attrs:
                url = paginationContainer["href"]
            else:
                break
                
        except Exception as e:
            LOGGER.warning(f"Erreur lors de la récupération des dépendants pour {repo}: {e}")
            break
        
    return dependents_data

def fetch_awesome_readme_content(github_client, awesome_repo_path, readme_filename, local_readme_path):
    """Récupère le contenu du README d'une liste Awesome."""
    
    awesome_repo = github_client.get_repo(awesome_repo_path)
    if not awesome_repo:
        raise ValueError(f"Repository {awesome_repo_path} not found")
    
    # Déterminer la branche par défaut
    default_branch = awesome_repo.default_branch
    LOGGER.info(f"Branche par défaut du dépôt: {default_branch}")
    
    # Liste des noms possibles pour le README
    readme_variants = [
        readme_filename,
        readme_filename.lower(),
        "README",
        "readme",
        "README.markdown",
        "readme.markdown",
        "README.rst",
        "readme.rst"
    ]
    
    awesome_content = None
    last_exception = None
    
    # Méthode 1: Essayer d'obtenir le contenu via l'API GitHub avec différentes variantes
    for variant in readme_variants:
        try:
            LOGGER.info(f"Tentative de récupération via l'API GitHub avec le nom: {variant}")
            content_file = awesome_repo.get_contents(urllib.parse.quote(variant))
            if isinstance(content_file, list):
                # Si c'est un dossier, chercher un fichier README dedans
                for file in content_file:
                    if re.match(r"readme.*", file.name, re.IGNORECASE):
                        content_file = file
                        break
                else:
                    continue  # Aucun README trouvé dans la liste
            
            awesome_content_encoded = content_file.content
            awesome_content = base64.b64decode(awesome_content_encoded)
            LOGGER.info(f"Contenu récupéré avec succès via l'API GitHub pour: {variant}")
            break
        except Exception as e:
            LOGGER.debug(f"Échec avec la variante {variant}: {e}")
            last_exception = e
    
    # Méthode 2: Si l'API GitHub échoue, essayer via l'URL raw
    if awesome_content is None:
        LOGGER.warning(f"Impossible d'obtenir le contenu via l'API GitHub: {last_exception}")
        
        for variant in readme_variants:
            try:
                LOGGER.info(f"Tentative de récupération via l'URL raw avec la branche {default_branch} et le nom: {variant}")
                raw_url = f"https://raw.githubusercontent.com/{awesome_repo_path}/{default_branch}/{variant}"
                response = requests.get(raw_url)
                
                if response.status_code == 200:
                    awesome_content = response.content
                    LOGGER.info(f"Contenu récupéré avec succès via l'URL raw pour: {variant}")
                    break
                else:
                    LOGGER.debug(f"Échec avec l'URL raw pour {variant}: {response.status_code}")
            except Exception as e:
                LOGGER.debug(f"Erreur lors de la récupération via l'URL raw pour {variant}: {e}")
                last_exception = e
    
    # Méthode 3: Essayer de récupérer directement la page HTML du dépôt et extraire le README rendu
    if awesome_content is None:
        try:
            LOGGER.info("Tentative de récupération via le HTML de la page GitHub...")
            html_url = f"https://github.com/{awesome_repo_path}"
            
            # Utiliser un User-Agent pour éviter les limitations d'API
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(html_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Différentes tentatives pour extraire le contenu du README
                readme_div = soup.find("div", {"id": "readme"})
                
                if readme_div:
                    # Tentative 1: Chercher l'article dans le div readme
                    readme_content = readme_div.find("article")
                    
                    if readme_content:
                        LOGGER.info("Contenu du README trouvé dans l'article")
                        # Extraire le contenu Markdown à partir du HTML
                        markdown_content = []
                        for elem in readme_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "li", "a", "code", "pre"]):
                            if elem.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                                level = int(elem.name[1])
                                markdown_content.append("#" * level + " " + elem.get_text().strip())
                            elif elem.name == "p":
                                markdown_content.append(elem.get_text().strip())
                            elif elem.name == "a":
                                href = elem.get("href", "")
                                markdown_content.append(f"[{elem.get_text().strip()}]({href})")
                            elif elem.name == "li":
                                markdown_content.append("- " + elem.get_text().strip())
                        
                        awesome_content = "\n\n".join(markdown_content).encode('utf-8')
                    else:
                        # Tentative 2: Prendre tout le contenu du div readme
                        LOGGER.info("Article non trouvé, utilisation du div readme complet")
                        awesome_content = str(readme_div).encode('utf-8')
                else:
                    # Tentative 3: Chercher le contenu du markdown principal
                    LOGGER.warning("Division du README non trouvée, recherche d'alternatives...")
                    
                    # Essayer de trouver le contenu Markdown dans un autre élément
                    markdown_container = soup.find("div", {"class": "markdown-body"})
                    if markdown_container:
                        LOGGER.info("Contenu Markdown trouvé dans un conteneur alternatif")
                        awesome_content = str(markdown_container).encode('utf-8')
                    else:
                        # Dernier recours: prendre le contenu du body principal
                        main_content = soup.find("main", {"id": "js-repo-pjax-container"})
                        if main_content:
                            LOGGER.info("Utilisation du contenu principal de la page")
                            awesome_content = str(main_content).encode('utf-8')
                        else:
                            LOGGER.warning("Aucun conteneur de contenu trouvé")
                
                if awesome_content:
                    LOGGER.info("Contenu récupéré avec succès via le HTML de la page GitHub")
                else:
                    LOGGER.warning("Échec de l'extraction du contenu à partir du HTML")
            else:
                LOGGER.warning(f"Échec de la récupération de la page HTML: {response.status_code}")
        except Exception as e:
            LOGGER.error(f"Erreur lors de la récupération via HTML: {e}")
            last_exception = e
    
    # Méthode 4 (cas spécifique): Téléchargement direct pour sindresorhus/awesome
    if awesome_content is None and awesome_repo_path.lower() == "sindresorhus/awesome":
        try:
            LOGGER.info("Tentative spécifique pour sindresorhus/awesome...")
            # URL direct vers le README de sindresorhus/awesome (peut nécessiter une mise à jour)
            special_url = "https://raw.githubusercontent.com/sindresorhus/awesome/main/readme.md"
            response = requests.get(special_url)
            
            if response.status_code == 200:
                awesome_content = response.content
                LOGGER.info("Contenu récupéré avec succès via l'URL spécifique pour sindresorhus/awesome")
            else:
                LOGGER.warning(f"Échec avec l'URL spécifique: {response.status_code}")
        except Exception as e:
            LOGGER.error(f"Erreur avec l'URL spécifique: {e}")
            last_exception = e
    
    if awesome_content is None:
        LOGGER.error("Toutes les méthodes de récupération ont échoué")
        raise ValueError(f"Impossible de récupérer le contenu du README après avoir essayé plusieurs méthodes: {last_exception}")
    
    # Crée le répertoire parent si nécessaire
    Path(local_readme_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(local_readme_path, "w", encoding="utf-8") as filehandle:
        filehandle.write(awesome_content.decode("utf-8", errors="replace"))
    LOGGER.info(f"Awesome README saved to {local_readme_path}")
    return AwesomeList(str(local_readme_path))

def initialize_csv_writers(projects_csv_path, orgs_csv_path):
    """Initialise les écrivains CSV pour les projets et les organisations."""
    import csv
    from pathlib import Path
    
    projects_csv_path = Path(projects_csv_path)
    orgs_csv_path = Path(orgs_csv_path)
    
    projects_csv_path.parent.mkdir(parents=True, exist_ok=True)
    orgs_csv_path.parent.mkdir(parents=True, exist_ok=True)

    csv_fieldnames = [
        "project_name", "oneliner", "git_namespace", "git_url", "platform",
        "topics", "rubric", "last_commit_date", "stargazers_count",
        "number_of_dependents", "stars_last_year", "project_active",
        "dominating_language", "organization", "organization_user_name",
        "languages", "homepage", "readme_content", "refs", "project_created",
        "project_age_in_days", "license", "total_commits_last_year",
        "total_number_of_commits", "last_issue_closed", "open_issues",
        "closed_pullrequests", "closed_issues", "issues_closed_last_year",
        "days_until_last_issue_closed", "open_pullrequests", "reviews_per_pr",
        "development_distribution_score", "last_released_date",
        "last_release_tag_name", "good_first_issue", "contributors",
        "accepts_donations", "donation_platforms", "code_of_conduct",
        "contribution_guide", "dependents_repos", "organization_name",
        "organization_github_url", "organization_website",
        "organization_location", "organization_country", "organization_form",
        "organization_avatar", "organization_public_repos",
        "organization_created", "organization_last_update",
    ]

    csv_github_organizations_fieldnames = [
        "organization_name", "organization_user_name", "organization_github_url",
        "organization_website", "organization_location", "organization_country",
        "organization_form", "organization_avatar", "organization_public_repos",
        "organization_created", "organization_last_update", "organization_rubric"
    ]

    csv_projects_file = open(projects_csv_path, "w", newline="", encoding="utf-8")
    writer_projects = csv.DictWriter(csv_projects_file, fieldnames=csv_fieldnames)
    writer_projects.writeheader()

    existing_orgs = set()
    if orgs_csv_path.exists():
        with open(orgs_csv_path, "r", newline="", encoding="utf-8") as f_org_read:
            reader_github_organizations = csv.DictReader(f_org_read)
            for entry in reader_github_organizations:
                if 'organization_user_name' in entry:
                    existing_orgs.add(entry['organization_user_name'])

    csv_orgs_file = open(orgs_csv_path, "a", newline="", encoding="utf-8")
    writer_github_organizations = csv.DictWriter(csv_orgs_file, fieldnames=csv_github_organizations_fieldnames)
    # Write header only if file is new/empty
    if orgs_csv_path.stat().st_size == 0:
        writer_github_organizations.writeheader()

    return writer_projects, writer_github_organizations, existing_orgs, csv_projects_file, csv_orgs_file