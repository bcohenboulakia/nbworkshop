<!--
This file is part of nbworkshop.

nbworkshop is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3 as published by
the Free Software Foundation.

nbworkshop is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nbworkshop. If not, see <https://www.gnu.org/licenses/>.
-->

<p align="center">
<img width=400 alt="nbworkshop logo" src="https://github.com/user-attachments/assets/9af0a222-afc6-4d5a-9529-a8d0daa29b18">
</p>


[🇫🇷 Aller à la version française 🇫🇷](#-version-française-)

_nbworkshop_ is a tool for preparing Python exercise Jupyter notebooks with hidden solutions or instructor-only comments:
![Simple nbworkshop example](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

Key strengths:
- No server required
- No rigid course file structure
- Preconfigured GitHub workflow with automatic regeneration on each push to main
- No local installation needed when using the GitHub workflow

<details>
  <summary><strong>Show full documentation</strong></summary>
  
## Content:
* [Presentation](#presentation)
* [Installation and Prerequisites](#installation-and-prerequisites)
* [Quick start](#quick-start)
* [Solution formatting](#solution-formatting)
   * [solution in Code cells](#solution-in-code-cells)
   * [Solution in Markdown cells](#solution-in-markdown-cells)
   * [Note addressed to the tutor](#note-addressed-to-the-tutor)
   * [Cell entirely addressed to the tutor](#cell-entirely-addressed-to-the-tutor)
* [Configuration file](#configuration-file)
* [Conversion process](#conversion-process)
   * [Conversion script](#conversion-script)
   * [Notebooks filename](#notebooks-filename)
   * [Zip archive and attached files](#zip-archive-and-attached-files)
* [GitHub workflow](#github-workflow)
   * [Conversion triggering and branches](#conversion-triggering-and-branches)
   * [Pre and post-processing command](#pre-and-post-processing-command)


## Presentation

Starting from one or several tutor notebooks, _nbworkshop_ generates synchronized student versions in which marked solutions and instructor-only comments are automatically removed or replaced by placeholders. This makes it possible to maintain one reference notebook while publishing student-ready material. _nbworkshop_ is compatible with standard Jupyter notebooks (`.ipynb` files), which you can create or edit with Jupyter or JupyterLab.

The tool deliberately does not include automated validation, grading, or advanced distribution features, offering a much simpler configuration than more comprehensive systems like _nbgrader_, with no complicated workflow or rigid directory structure: you only need to mark the parts to hide (in code or markdown cells) and generate student versions. This keeps tutor and students content perfectly synchronized, eliminating the risk of manual errors.

A GitHub Actions workflow automates generation and versioning: every time a notebook is updated on the main branch, synchronized student versions and optional ZIP archives are created and stored in a dedicated branch, ensuring a clear separation between instructor and student materials.

**Key features:**
* **Solution and instructions hiding**: Add special markers in code or markdown cells for lines or blocks to be hidden in the student version. Instructor notes are also removed during conversion.
* **Automatic batch processing**: Process multiple notebooks at once, generating student versions and, if enabled, ZIP files with all relevant attachments.
* **Integrated automation**: A pre-configured GitHub Actions workflow regenerates student versions and archives whenever notebooks are updated on the main branch; it is also possible to [trigger the workflow manually](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow), and all generated material is stored in a separate branch.
* **Extensibility and CI/CD compatibility**: Customize the workflow with your own pre or post-processing commands (for example, to send files to an LMS), or integrate the conversion script into alternative CI/CD pipelines like GitLab CI/CD, Bitbucket Pipelines, or other custom workflows.
* **Flexible configuration**: All markers, placeholders and naming conventions are set via a simple JSON configuration file, making adaptation to different teaching styles straightforward; you can, for example, use a code placeholder that raises a `NotImplementedError`.

## Installation and Prerequisites

_nbworkshop_ can be used in two different ways:
* Using the GitHub workflow (no prerequisites)<br>
 The project is entirely self-contained when used with the integrated GitHub workflow. In this case, no prerequisites or additional installation steps are required. Simply clone the repository to get started (see [Quick start](#quick-start)).
* Direct use of the conversion script<br>
   If you want to run the conversion script directly on your machine, you will need:
	* Python (version 3.12 or later, the script has not been tested against previous versions)
	*  BeautifulSoup to process Markdown cells (the script has been tested against BeautifulSoup 4.9.0).
	
   In this case, the script can be moved anywhere, provided that it can access the configuration file. Have a look at [Conversion script](#conversion-script) below for more details.

All _nbworkshop_ code is in the `.github` directory. It contains:
* `.github/scripts/nbworkshop_publish.py` and `.github/scripts/publish_outputs.py`: notebook selection and non-destructive publication helpers.
* `.github/scripts/nbworkshop_convert.py`: the Python script that converts Tutor notebooks to `Students` notebooks, and creates ZIP archives with all the attached files. If used alone, this script can be moved anywhere, provided it still has access to the configuration file
* `.github/workflows/nbworkshop_convert_students.yml`: The GitHub workflow that calls the aforementioned Python script every time a notebook is pushed on the repository's `main` branch.
* `.github/nbworkshop_convert.json`: The configuration file. This is where parameters such as notebook directories, text replacement, placeholders etc. are defined.


## Quick start
In workflow mode, _nbworkshop_ is entirely hosted on the GitHub repository hosting the notebooks, and requires no prerequisites (except for a GitHub account). To get started using this workflow:
1. Clone this repository
2. Add notebooks to the clone repository
3. Edit `.github/nbworkshop_convert.json` to insert in `"notebooks_dir"` the directory containing the notebooks you created (see [Configuration file](#configuration-file) for a detailed explanation)
4. Edit the notebooks (see [Solution formatting](#solution-formatting) for more detailed explanation on formatting solutions):
	* In code cells, add `#SOLUTION` to each line of code cells that the students have to figure out by themselves.
	* In Markdown cells, add answers to the questions inside `<blockquote>`tags. Be sure to leave the HTML tags alone on their lines.  
5. Commit the  notebooks on the `main` branch, and push them to the GitHub repository

The newly created `Students` branch contains the `Students` versions of the notebooks (and ZIP archives), with solutions replaced by placeholders and all execution traces (including calculation results and cell execution counters) removed. Those converted notebooks are updated on every push on the `main` branch.

Manual use is described in the [_Conversion script_ section](#conversion-script).

## How to add solutions and notes addressed to tutors

The script processes any standard Jupyter notebook and expects files in the `.ipynb` format. Note that _nbworkshop_ can use any replacement text/tags and placeholder the user defines (see [Configuration file](#configuration-file)). In the following explanations, default versions are used.

### solution in Code cells
To create a line or block of solution, the comment `#SOLUTION` must be added at the end of each line of the block. The block is replaced by a single placeholder `#TO COMPLETE`. Example:

```python
y = x #SOLUTION
```

is replaced by:
```python
#TO COMPLETE
```

To create the beginning of an instruction to be completed, the instruction must be multi-line using the `\` character, with the solution part on the second line and the comment `#SOLUTION` at the end. Example:
```python
y =\
    x #SOLUTION
```

is replaced by:
```python
y = #TO COMPLETE
```

Regular comments can be added, placed before `#SOLUTION` on the same line. Example:
```python
y = x #comment #SOLUTION
```

Comments specifically for tutors can also be added after `#SOLUTION` on the same line. Example:
```python
y = x #SOLUTION comment for the tutor
```

### Solution in Markdown cells

Solutions and comments are placed in a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> tag. They are replaced by a single placeholder <code>&lt;em&gt;TO COMPLETE&lt;/em&gt;</code>. Sometimes, Jupyter can't interpret Markdown code inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. In this case, reverting to HTML formatting is required.

The <code>&lt;blockquote&gt;</code> and <code>&lt;/blockquote&gt;</code> tags must be alone on their line, and the closing tag must not be forgotten (errors are not handled; the generated student version is then corrupted).

If there is no blank line between the question and the answer, the placeholder is placed on the same line as the question. Example:
```html
Question?
<blockquote>
    Expected answer.
</blockquote>
```
    
is replaced by:
```html
Question ? <em>TO COMPLETE</em>
```
    
If there is a blank line between the question and the answer, the placeholder is placed on the line below the question. Example:
```HTML
Question?

<blockquote>
    Expected answer.
</blockquote>
```
    
is replaced by:
```html
Question?
<em>TO COMPLETE</em>
```

### Note addressed to the tutor

A note only addressed to the tutor can be added in the notebook. This note is completely removed from the student notebook. It must be placed in markdown cells, inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>  block with the class <code>"comment"</code>. Example:
```html
WS text.

<blockquote class="comment">
    Note to the tutor
</blockquote>

Continuation of the WS.
```

is replaced by:
```html
WS text.
Continuation of the WS.

```

To place this note inside a single paragraph in the student version, chain the text and notes without a line break above or below the comment. Example:
```html
WS text.
<blockquote class="comment">
    Note to the tutor
</blockquote>
Continuation of the WS text.
```

is replaced by:

```html
WS text. Continuation of the WS text.
```

### Cell entirely addressed to the tutor
This is a markdown cell that does not appear at all in the `Students` version. It's a cell containing only a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> block. The cell is then entirely removed when generating the student version.

## Configuration file

The configuration file includes options for both conversion and GitHub workflow. Each one only takes into account the relevant options:
```json
{
    "notebooks_dir": ["Examples/notebooks/", "Examples/ASSIGNMENTS"],
    "solution_marker": {
        "code": "SOLUTION",
        "markdown": "blockquote"
    },
    "placeholder": {
        "code": "#TO COMPLETE",
        "markdown": "<em>TO COMPLETE</em>"
    },
    "tutor_postfix": "_Tutor",
    "student_postfix": "_Student",
    "generate_zip": true,
    "rebuild_all": false,
    "post_processing": "echo 'Post-processing complété' || true",
    "pre_processing": "echo 'Pré-processing complété' || true"
}
```

* Conversion options (all mandatory for the conversion script, ignored by the workflow):
	* `solution_marker`: Dictionary of markers identifying solution content, containing only the core text, which is either wrapped as an HTML tag for Markdown or prefixed with a comment character for Python.
	* `placeholder`: Dictionary of replacement text for removed solutions
	* `generate_zip`: Boolean enabling ZIP archives to be generated.
	* `tutor_postfix`: String replaced by the value of `student_postfix` for the notebook filename.
	* `student_postfix`: String replacing the value of `tutor_postfix` for the notebook filename.
* Workflow options (ignored by the conversion script):
	* `notebooks_dir` (mandatory): List of directories to process.
	* `rebuild_all` (optional): Boolean determining whether all notebooks are rebuilt every time, or only the ones that have changed since the last commit (and the corresponding ZIP if generated)
	* `pre_processing` and `post_processing` (optional): Pre and Post-processing shell commands to be executed by the workflow, allowing for example to modify the notebooks before conversion, and send the generated ZIP archives to a LMS.
	
The configuration file is located in different places depending on the mode of use:
* **Using GitHub workflow**: `.github/nbworkshop_convert.json`
* **Manual script use**: `./nbworkshop_convert.json` (in the script's directory), but can be changed through commandline option (see [Conversion script](#conversion-script))

## Conversion process

### Conversion script

The Python script that generates student notebooks is located at `.github/scripts/nbworkshop_convert.py`.  If it's run through the GitHub workflow, there's no need to know anything about it. Everything (including paths of the generated files, and error management) is handled by the workflow, and through the configuration file. If manually run (that is, not through the GitHub workflow), the student version is created in the same directory as the original notebook.

There are two ways to run the conversion script locally:
1. **With uv (recommended, zero setup)**: The script declares its required Python version and dependencies in its header, using the standard metadata format (PEP 723) supported by [uv](https://github.com/astral-sh/uv). If you have uv installed, simply run:
   
   ```bash
   uv run nbworkshop_convert.py NOTEBOOK_PATHS [--config PATH] [--hide-header]
   ```
   
   uv will automatically create an isolated environment, install Python (if needed) and all required packages (`beautifulsoup4` and `chardet`), then execute the script.
   
2. **With a manual Python setup**: Alternatively, you can run the script with any Python 3.12 or later. First, install the required dependencies:
   
   ```bash
   pip install beautifulsoup4>=4.9.0 chardet
   ```
   
   You may then run the script with:

   ```bash
   python nbworkshop_convert.py NOTEBOOK_PATHS [--config PATH] [--hide-header]
   ```
   
The script accepts the following arguments:
* `NOTEBOOK_PATHS`: Process specific notebooks (supports glob patterns: `*.ipynb`, `**/exercises/*.ipynb`)
* `--config` (optional): Specify alternative config path (default: `./nbworkshop_convert.json`)
* `--hide-header` (optional): Suppress Markdown table headers for embedding in reports

and then:
* creates the converted student notebooks in the same directory as the originals.
* prints a summary of the process (including the conversion report) to standard output. Notebooks are referenced with absolute paths if outside the current working directory.
* when using `--hide-header`, outputs the summary table without headers, which is suitable for concatenating reports in batch or CI/CD pipelines.
* **Configuration file note:** When run manually, the script expects `./nbworkshop_convert.json` by default (can be overridden with `--config`). The GitHub workflow, by contrast, uses `.github/nbworkshop_convert.json`.

### Notebooks filename

Every solution marker in processed notebooks is replaced by the corresponding placeholder (both can be set in the [Configuration file](#configuration-file)). If an original notebook's filename ends with the configured `tutor_postfix` parameter (see [Configuration](#configuration)), this postfix is replaced by the `student_postfix` parameter in the converted notebook's filename. If the original name does not end with `tutor_postfix`, the `student_postfix` value is simply appended to the base name. No additional characters (such as underscores or spaces) are inserted automatically; the exact format is entirely determined by the postfix values set in the configuration.

## GitHub workflow

The `Notebook conversion to Students branch` workflow uses `.github/nbworkshop_convert.json` and runs when notebooks are pushed to `main`, or manually from Actions. It converts sources in the configured directories, then publishes only generated notebooks, optional ZIPs, explicitly declared `metadata.attached_files`, and the conversion report in `Students/README.md`.

* `rebuild_all: true` regenerates all current notebooks; it never resets the branch.
* `rebuild_all: false` selects changed notebooks. A manual run always rebuilds all current notebooks.
* Deleting or renaming a source removes only its corresponding generated notebook and ZIP.

There is no merge of `main` into `Students` and no forced push. Files published by another tool, such as PPTAnim2PDF PDFs, are preserved. If another publication advances the branch during the push, nbworkshop retrieves the new state and retries without rerunning conversion or hooks. A concurrent change to the same destination path fails explicitly.

A newly created `Students` branch contains only published outputs. Instructor files already present on an older branch are retained; remove them separately before distributing the branch. Do not edit generated notebooks manually.

The conversion report is available in `Students/README.md` and the Actions summary:
![Student branch README](https://github.com/user-attachments/assets/bc132feb-5f43-40e7-aa64-962154bc15b1)

A copy of this review appears on the workflow page in the `Action` tab on the GitHub repository web page:
![GitHub Actions summary](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)

The workflow can also be run manually from the same tab. For more information on how to manage and monitor GitHub workflow, see the [official GitHub Actions documentation](https://docs.github.com/en/actions/writing-workflows/quickstart).


### Zip archive and attached files

For each processed notebook, if ZIP archives are to be generated (see the _Configuration_ section below), they are added in the `ZIP` subdirectory of each directory containing converted notebooks. Each archive contains one notebook and all embedded files. These files must be referenced directly in the global metadata of the notebook, as a list associated with the key `"attached_files"`. Example:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Relative paths can be used, they are replicated in the ZIP archive. Absolute paths are forbidden and generate an error preventing the conversion to complete. If there is an error (embedded file missing or defined by an absolute path), the conversion is aborted. When used through the GitHub workflow (see below), subsequent notebooks are generated, but the workflow execution status is set to failed, and the summary displays the faulty notebook (see [GitHub workflow](#github-workflow)).

Note: In Jupyter-based environnements, editing the metadata of a notebook is done in the _ADVANCED TOOLS_ area, under _Notebook metadata_. In Jupyter, it can be accessed by enabling _View_ > _Right Sidebar_ > _Show notebook tools_. In JupyterLab, it's located in the _Property Inspector_ (gear icon) in the right sidebar.

### Conversion triggering and branches

This workflow uses two branches to generate student notebooks (but as many branches as needed can be created, they will just be ignored):
* The `main` branch contains the solution versions and the necessary resources (it can also contain other materials, which are ignored). Pushing a notebook on this branch triggers its conversion, provided the pushed notebook is in a monitored directory (as defined in the `notebooks_dir` section of the configuration file).
* The `Students` branch receives only explicitly published outputs, at their original relative paths. Other files on that branch are preserved; unlisted source resources are not mirrored automatically.

Please note that conversion may take several dozens of seconds. This total delay includes both the time spent waiting for a GitHub Actions runner to become available (which can be long if no runners are free) and the time required to actually process the job. The execution time depends on how many notebooks need to be converted and their length. Running other workflows in the repository at the same time may also increase the overall completion time. Moreover, in order to avoid useless conversions, `.ipynb_checkpoints` directories should be added to `.gitignore`.

### Pre and post-processing command

The `pre_processing` and `post_processing` options in `nbworkshop_convert.json` allow executing a command before or after all notebook conversions are completed:
* The pre-processing command is run just after setting up the workflow and validating the configuration file
* The post-processing command is run after notebook conversion, before the generated files are committed and pushed to the `Students` branch.
 
Both hooks run in the temporary checkout of `main`: pre-processing before conversion, post-processing after conversion and before Git publication. They can call scripts from the source repository. Their temporary changes do not update `main`. They must not switch branches: publication uses a separate worktree. Hook failures stop publication, and output is included in the Actions summary.

Post-processing can use generated files, but it is not an after-successful-push hook. If an external deployment must wait for confirmed Git publication, keep it in a separate downstream step.

To install alongside PPTAnim2PDF, copy both workflows, their converter scripts and publication helpers under `.github/`, preserving paths. Both tools include the same neutral `.github/scripts/publish_outputs.py`. Keep `.github/nbworkshop_convert.json` unchanged; no shared JSON migration is required. Each workflow handles its own source types and output paths, so a mixed push can run both. PPTAnim2PDF must not overwrite the nbworkshop report in `Students/README.md`.

Publication tests: `python -m unittest discover -s tests -p 'test_nbworkshop_publish.py' -v`.

Also note that the `actions: write` permission has been enabled, allowing commands to trigger other workflows using GitHub CLI (`gh workflow run`) without requiring additional personal access tokens. This requires target workflows to declare a `workflow_dispatch` trigger. Just be careful with trigger rules, as overlapping triggers can cause multiple executions.

</details>
	
## 🇫🇷 Version française 🇫🇷

_nbworkshop_ est un outil spécialisé dans la préparation de notebooks Jupyter d'exercices Python avec des solutions cachées ou des commentaires réservés aux instructeurs&nbsp;:
![Exemple simple nbworkshop](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

Points forts&nbsp;:
- Ne nécessite pas de serveur
- Pas d’arborescence de fichiers rigide
- Workflow GitHub déjà prêt, avec régénération automatique à chaque push sur main
- Pas besoin d'installation locale quand le workflow GitHub est utilisé

<details>
  <summary><strong>Afficher la documentation</strong></summary>
  

## Contenu&nbsp;:
* [Présentation](#présentation)
* [Installation et Prérequis](#installation-et-prérequis)
* [Démarrage rapide](#démarrage-rapide)
* [Formatage des solutions](#formatage-des-solutions)
   * [Solution dans les cellules de code](#solution-dans-les-cellules-de-code)
   * [Solution dans les cellules Markdown](#solution-dans-les-cellules-markdown)
   * [Note destinée au tuteur](#note-destinée-au-tuteur)
   * [Cellule entièrement destinée au tuteur](#cellule-entièrement-destinée-au-tuteur)
* [Fichier de configuration](#fichier-de-configuration)
* [Processus de conversion](#processus-de-conversion)
   * [Script de conversion](#script-de-conversion)
   * [Nom des fichiers des notebooks](#nom-des-fichiers-des-notebooks)
   * [Archive Zip et fichiers joints](#archive-zip-et-fichiers-joints)
* [Workflow GitHub](#workflow-github)
   * [Déclenchement de la conversion et branches](#déclenchement-de-la-conversion-et-branches)
   * [Commandes de pré et post-traitement](#commandes-de-pré-et-post-traitement)

## Présentation

À partir d’un ou de plusieurs notebooks tuteur, nbworkshop génère des versions étudiantes synchronisées dans lesquelles les solutions marquées et les commentaires réservés à l’enseignant sont automatiquement supprimés ou remplacés par des espaces réservés. Cela permet de conserver un seul notebook de référence tout en publiant une version directement utilisable par les étudiants. _nbworkshop_ est compatible avec les notebooks Jupyter standards (fichiers `.ipynb`), que vous pouvez créer ou modifier avec Jupyter ou JupyterLab.

Cet outil ne propose volontairement aucune fonctionnalité de validation automatique, de correction ou de distribution avancée, ce qui permet une configuration bien plus simple que celle de systèmes plus complets comme _nbgrader_, sans workflow compliqué ni structure de fichiers rigide&nbsp;: il suffit de marquer les parties à masquer (dans les cellules code ou markdown) puis de générer les versions étudiantes. Cela garantit une parfaite synchronisation entre les contenus du tuteur et des étudiants, supprimant tout risque d’erreur manuelle.
Un workflow GitHub Actions automatise la génération et le versioning&nbsp;: à chaque modification d’un notebook sur la branche `main`, des versions étudiantes synchronisées, ainsi que des archives ZIP si besoin, sont créées et stockées sur une branche dédiée, assurant ainsi une séparation claire entre les contenus enseignant et étudiant.

**Fonctionnalités principales :**
* **Masquage des solutions et instructions :** Ajoutez des marqueurs spéciaux dans les cellules de code ou de texte pour masquer certaines lignes ou blocs dans la version étudiante ; les notes destinées à l’enseignant sont également supprimées lors de la conversion.
* **Traitement par lots automatique :** Traitez plusieurs notebooks en une seule fois, en générant les versions étudiantes et, si besoin, des archives ZIP contenant tous les fichiers associés.
* **Automatisation intégrée :** Un workflow GitHub Actions préconfiguré régénère les versions étudiantes et les archives à chaque mise à jour d’un notebook sur la branche `main`&nbsp;; il est aussi possible de [déclencher manuellement le workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow), et tous les fichiers générés sont stockés sur une branche séparée.
* **Extensibilité et compatibilité CI/CD :** Personnalisez le workflow en ajoutant vos propres commandes de pré ou post-traitement (par exemple, pour envoyer des fichiers à un LMS), ou intégrez le script de conversion dans d’autres pipelines CI/CD tels que GitLab CI/CD, Bitbucket Pipelines, ou tout workflow sur mesure.
* **Configuration flexible :** Tous les marqueurs, espaces réservés et conventions de nommage sont définis via un simple fichier de configuration JSON, ce qui facilite l’adaptation à différents styles d’enseignement ; vous pouvez par exemple utiliser un espace réservé de code qui lève une `NotImplementedError`.

## Installation et Prérequis

_nbworkshop_ peut être utilisé de deux manières différentes&nbsp;:
* Utilisation du workflow GitHub (aucun prérequis)<br>
 Le projet est entièrement autonome lorsqu'il est utilisé avec le workflow GitHub intégré. Dans ce cas, aucun prérequis ou étape d'installation supplémentaire n'est nécessaire. Clonez simplement le dépôt pour commencer (voir [Démarrage rapide](#démarrage-rapide)).
* Utilisation directe du script de conversion<br>
   Si vous souhaitez exécuter le script de conversion directement sur votre machine, vous aurez besoin de&nbsp;:
	* Python (version 3.12 ou ultérieure)
	*  BeautifulSoup pour traiter les cellules Markdown (le script a été testé avec BeautifulSoup 4.9.0).
	
   Dans ce cas, le script peut être déplacé n'importe où, à condition qu'il puisse accéder au fichier de configuration. Consultez [Script de conversion](#script-de-conversion) ci-dessous pour plus de détails.

Tout le code de _nbworkshop_ se trouve dans le répertoire `.github`. Il contient&nbsp;:
* `.github/scripts/nbworkshop_publish.py` et `.github/scripts/publish_outputs.py` : sélection des notebooks et publication sans réécriture de branche.
* `.github/scripts/nbworkshop_convert.py`&nbsp;: le script Python qui convertit les notebooks Tuteur en notebooks Étudiants, et crée des archives ZIP avec tous les fichiers joints. S'il est utilisé seul, ce script peut être déplacé n'importe où, à condition d'avoir toujours accès au fichier de configuration
* `.github/workflows/nbworkshop_convert_students.yml`&nbsp;: Le workflow GitHub qui appelle le script Python susmentionné à chaque fois qu'un notebook est poussé sur la branche `main` du dépôt.
* `.github/nbworkshop_convert.json`&nbsp;: Le fichier de configuration. C'est ici que sont définis les paramètres tels que les répertoires des notebooks, les remplacements de texte, les espaces réservés, etc.

Jupyter n’est pas obligatoire pour utiliser le script, du moment que les notebook Jupyter sont accessibles.

## Démarrage rapide
En mode workflow, _nbworkshop_ est entièrement hébergé sur le dépôt GitHub hébergeant les notebooks, et ne nécessite aucun prérequis (à part un compte GitHub). Pour commencer à utiliser ce workflow&nbsp;:
1. Clonez ce dépôt
2. Ajoutez des notebooks au dépôt cloné
3. Modifiez `.github/nbworkshop_convert.json` pour insérer dans `"notebooks_dir"` le répertoire contenant les notebooks que vous avez créés (voir [Fichier de configuration](#fichier-de-configuration) pour une explication détaillée)
4. Modifiez les notebooks (voir [Formatage des solutions](#formatage-des-solutions) pour des explications plus détaillées sur le formatage des solutions)&nbsp;:
	* Dans les cellules de code, ajoutez `#SOLUTION` à chaque ligne des cellules de code que les étudiants doivent trouver par eux-mêmes.
	* Dans les cellules Markdown, ajoutez les réponses aux questions entre des balises `<blockquote>`. Veillez à laisser les balises HTML seules sur leurs lignes.  
5. Committez les notebooks sur la branche `main` et poussez-les vers le dépôt GitHub

La nouvelle branche `Students` contient les versions étudiantes des notebooks (et archives ZIP), avec les solutions remplacées par des espaces réservés et toutes les traces d'exécution (y compris les résultats de calcul et les compteurs d'exécution de cellules) supprimées. Ces notebooks convertis sont mis à jour à chaque poussée sur la branche `main`.

L'utilisation manuelleest expliquée dans la [Section _Script de conversion_](#script-de-conversion).

## Comment ajouter des solutions et des notes adressées au tuteur

Le script traite tout notebook Jupyter standard et attend des fichiers au format `.ipynb`. Notez que _nbworkshop_ peut utiliser n'importe quel texte de remplacement/balises et espace réservé défini par l'utilisateur (voir [Fichier de configuration](#fichier-de-configuration)). Dans les explications suivantes, les versions par défaut sont utilisées.

### Solution dans les cellules de code
Pour créer une ligne ou un bloc de solution, le commentaire `#SOLUTION` doit être ajouté à la fin de chaque ligne du bloc. Le bloc est remplacé par un seul espace réservé `#TO COMPLETE`. Exemple&nbsp;:

```python
y = x #SOLUTION
```

est remplacé par&nbsp;:
```python
#TO COMPLETE
```


Pour créer le début d'une instruction à compléter, l'instruction doit être multi-ligne en utilisant le caractère `\`, avec la partie solution sur la deuxième ligne et le commentaire `#SOLUTION` à la fin. Exemple&nbsp;:
```python
y =\
    x #SOLUTION
```

est remplacé par&nbsp;:
```python
y = #TO COMPLETE
```

Des commentaires réguliers peuvent être ajoutés, placés avant `#SOLUTION` sur la même ligne. Exemple&nbsp;:
```python
y = x #commentaire #SOLUTION
```

Des commentaires spécifiquement pour les tuteurs peuvent également être ajoutés après `#SOLUTION` sur la même ligne. Exemple&nbsp;:
```python
y = x #SOLUTION commentaire pour le tuteur
```

### Solution dans les cellules Markdown

Les solutions et commentaires sont placés dans une balise <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. Ils sont remplacés par un seul espace réservé <code>&lt;em&gt;TO COMPLETE&lt;/em&gt;</code>. Parfois, Jupyter ne peut pas interpréter le code Markdown à l'intérieur d'un <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. Dans ce cas, il faut revenir au formatage HTML.

Les balises  <code>&lt;blockquote&gt;</code> et <code>&lt;/blockquote&gt;</code> doivent être seules sur leur ligne, et la balise de fermeture ne doit pas être oubliée (les erreurs ne sont pas gérées&nbsp;; la version étudiante générée est alors corrompue).

S'il n'y a pas de ligne vide entre la question et la réponse, l'espace réservé est placé sur la même ligne que la question. Exemple&nbsp;:
```html
Question?
<blockquote>
    Réponse attendue.
</blockquote>
```
    
est remplacé par&nbsp;:
```html
Question ? <em>TO COMPLETE</em>
```
    
S'il y a une ligne vide entre la question et la réponse, l'espace réservé est placé sur la ligne en dessous de la question. Exemple&nbsp;:
```HTML
Question?

<blockquote>
    Réponse attendue.
</blockquote>
```
    
est remplacé par&nbsp;:
```html
Question?
<em>TO COMPLETE</em>
```

### Note destinée au tuteur

Une note uniquement destinée au tuteur peut être ajoutée dans le notebook. Cette note est complètement supprimée du notebook étudiant. Elle doit être placée dans des cellules markdown, à l'intérieur d'un bloc <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>avec la classe <code>"comment"</code>. Exemple&nbsp;:
```html
Texte du WS.

<blockquote class="comment">
    Note pour le tuteur
</blockquote>

Suite du WS.
```

est remplacé par&nbsp;:
```html
Texte du WS.
Suite du WS.
```

Pour placer cette note à l'intérieur d'un seul paragraphe dans la version étudiante, enchaînez le texte et les notes sans saut de ligne au-dessus ou en dessous du commentaire. Exemple&nbsp;:
```html
Texte du WS.
<blockquote class="comment">
    Note pour le tuteur
</blockquote>
Suite du WS.
```

est remplacé par&nbsp;:

```html
Texte du WS. Suite du WS.
```

### Cellule entièrement destinée au tuteur
Il s'agit d'une cellule markdown qui n'apparaît pas du tout dans la version étudiante. C'est une cellule contenant uniquement un bloc <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. La cellule est alors entièrement supprimée lors de la génération de la version étudiante.

## Fichier de configuration

Le fichier de configuration inclut des options pour la conversion et le workflow GitHub. Chacun ne prend en compte que les options pertinentes&nbsp;:
```json
{
    "notebooks_dir": ["Examples/notebooks/", "Examples/ASSIGNMENTS"],
    "solution_marker": {
        "code": "SOLUTION",
        "markdown": "blockquote"
    },
    "placeholder": {
        "code": "#TO COMPLETE",
        "markdown": "<em>TO COMPLETE</em>"
    },
    "tutor_postfix": "_Tutor",
    "student_postfix": "_Student",
    "generate_zip": true,
    "rebuild_all": false,
    "post_processing": "echo 'Post-processing complété' || true",
    "pre_processing": "echo 'Pré-processing complété' || true"
}
```

* Options de conversion (toutes obligatoires pour le script de conversion, ignorées par le workflow)&nbsp;:
	* `solution_marker`&nbsp;: Dictionnaire des marqueurs identifiant le contenu solution, contenant uniquement le texte central, qui est soit encapsulé comme une balise HTML pour Markdown, soit préfixé par un caractère de commentaire pour Python.
	* `placeholder`&nbsp;:  Dictionnaire du texte de remplacement pour les solutions supprimées
	* `generate_zip`&nbsp;: Booléen activant la génération d'archives ZIP
	* `tutor_postfix`&nbsp;: Chaîne remplacée par la valeur de `student_postfix` pour le nom de fichier du notebook.
	* `student_postfix`&nbsp;: Chaîne remplaçant la valeur de `tutor_postfix` pour le nom de fichier du notebook.
* Options de workflow (ignorées par le script de conversion)&nbsp;:
	* `notebooks_dir` (obligatoire)&nbsp;: Liste des répertoires à traiter
	* `rebuild_all` (optional): Booléen indiquant si tous les notebooks doivent être reconstruits à chaque fois, ou seulement ceux qui ont été modifiés depuis le dernier commit (et le fichier ZIP correspondant s'il a été généré).
	* `pre_processing` et `post_processing` (optionnel)&nbsp;: Commandes shell de pré et post-traitement à exécuter par le workflow, permettant par exemple de modifier les notebooks avant conversion et d'envoyer les archives ZIP générées à un LMS.
	
Le fichier de configuration se trouve à différents endroits selon le mode d'utilisation&nbsp;:
* **Utilisation du workflow GitHub**&nbsp;: `.github/nbworkshop_convert.json`
* **Utilisation manuelle du script**&nbsp;: `./nbworkshop_convert.json` (dans le répertoire du script), mais peut être changé via une option en ligne de commande (voir [Script de conversion](#script-de-conversion))

## Processus de conversion
### Script de conversion

Le script Python qui génère les notebooks étudiants se trouve dans `.github/scripts/nbworkshop_convert.py`.  
S'il est utilisé via le workflow GitHub, il n'est pas nécessaire de s'en occuper directement : tous les chemins, la génération des fichiers et la gestion des erreurs sont assurés automatiquement par le workflow et le fichier de configuration.  
En exécution manuelle (c'est-à-dire en dehors du workflow GitHub), la version étudiante est créée dans le même répertoire que le notebook original.

Il existe deux façons d’exécuter le script localement :

1. **Avec uv (recommandé, aucune configuration)**  
   Le script déclare la version minimale de Python et les dépendances requises directement dans son en-tête, au format standard (PEP 723) pris en charge par [uv](https://github.com/astral-sh/uv).  
   Si uv est installé, il suffit de lancer :

   ```bash
   uv run nbworkshop_convert.py CHEMINS_NOTEBOOK [--config CHEMIN] [--hide-header]
   ```

   uv crée alors automatiquement un environnement isolé, installe Python (si besoin) et toutes les bibliothèques nécessaires (`beautifulsoup4` et `chardet`), puis exécute le script.

2. **Avec un environnement Python manuel**  
   Vous pouvez aussi exécuter le script avec n'importe quel Python 3.12 ou supérieur.  
   Installez d'abord les dépendances requises :

   ```bash
   pip install beautifulsoup4>=4.9.0 chardet
   ```
   
   Le script peut alors être lancé:
   
   ```bash
   python nbworkshop_convert.py NOTEBOOK_PATHS [--config PATH] [--hide-header]
   ```

Le script accepte les arguments suivants :
* `CHEMINS_NOTEBOOK` : traite un ou plusieurs notebooks spécifiques (motifs globaux acceptés : `*.ipynb`, `**/exercises/*.ipynb`)
* `--config` (optionnel) : spécifie un chemin alternatif pour la configuration (par défaut : `./nbworkshop_convert.json`)
* `--hide-header` (optionnel) : supprime les en-têtes de tableau Markdown (pour intégration dans des rapports)

Une fois lancé, le script :
* crée les versions étudiantes des notebooks dans le même répertoire que les originaux ;
* affiche un résumé du traitement (y compris le rapport de conversion) sur la sortie standard. Les notebooks sont référencés par leurs chemins absolus s’ils se trouvent hors du répertoire de travail courant ;
* si l’option `--hide-header` est utilisée, le tableau récapitulatif est généré sans en-tête, ce qui facilite la concaténation de rapports lors d'un traitement par lots ou dans un pipeline CI/CD ;
* **À noter concernant le fichier de configuration :** lors d’une exécution manuelle, le script utilise par défaut le fichier `./nbworkshop_convert.json` (modifiable via l’option `--config`). Le workflow GitHub, en revanche, utilise `.github/nbworkshop_convert.json`.


### Nom des fichiers des notebooks

Chaque marqueur de solution dans les notebooks traités est remplacé par l'espace réservé correspondant (tous deux peuvent être définis dans le [Fichier de configuration file](#fichier-de-configuration)).Si un nom de fichier de notebook original se termine par le paramètre `tutor_postfix` configuré (voir [Configuration](#configuration)), ce suffixe est remplacé par le paramètre `student_postfix` dans le nom de fichier du notebook converti. Si le nom original ne se termine pas par `tutor_postfix`, la valeur de  `student_postfix` est simplement ajoutée au nom de base. Aucun caractère supplémentaire (tel que des tirets bas ou des espaces) n'est inséré automatiquement&nbsp;; le format exact est entièrement déterminé par les valeurs de suffixe définies dans la configuration.

## Workflow GitHub

Le workflow `Notebook conversion to Students branch` utilise `.github/nbworkshop_convert.json`. Il s’exécute après un push de notebooks sur `main`, ou manuellement depuis Actions. Il convertit les sources des dossiers configurés, puis publie uniquement les notebooks générés, les ZIP optionnels, les ressources déclarées dans `metadata.attached_files` et le rapport `Students/README.md`.

* `rebuild_all: true` régénère tous les notebooks actuels ; il ne réinitialise jamais la branche.
* `rebuild_all: false` sélectionne les notebooks modifiés. Un lancement manuel reconstruit toujours tous les notebooks actuels.
* La suppression ou le renommage d’une source retire seulement son notebook généré et son ZIP.

Il n’y a ni fusion de `main` dans `Students`, ni push forcé. Les fichiers produits par un autre outil, notamment les PDF de PPTAnim2PDF, sont préservés. Si une publication concurrente fait avancer la branche pendant le push, nbworkshop récupère le nouvel état et réessaie sans refaire la conversion ni les hooks. Une modification concurrente du même chemin provoque un échec explicite.

Une nouvelle branche `Students` contient seulement les sorties publiées. Les fichiers enseignants déjà présents dans une ancienne branche sont conservés : retirez-les séparément avant de diffuser la branche. Ne modifiez pas manuellement les notebooks générés.

Le rapport est disponible dans `Students/README.md` et dans le résumé Actions :
![README de la branche `Students`](https://github.com/user-attachments/assets/bc132feb-5f43-40e7-aa64-962154bc15b1)

Une copie de cette revue apparaît sur la page du workflow dans l'onglet Action de la page web du dépôt GitHub&nbsp;:
![Sommaire de la page GitHub Actions](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)


Le workflow peut également être exécuté manuellement depuis le même onglet. Pour plus d'informations sur la gestion et la surveillance des workflows GitHub, consultez la [documentation officielle GitHub Actions](https://docs.github.com/en/actions/writing-workflows/quickstart).

### Archive Zip et fichiers joints

Pour chaque notebook traité, si des archives ZIP doivent être générées (voir la section Configuration ci-dessous), elles sont ajoutées dans le sous-répertoire ZIP de chaque répertoire contenant des notebooks convertis. Chaque archive contient un notebook et tous les fichiers intégrés. Ces fichiers doivent être référencés directement dans les métadonnées globales du notebook, comme une liste associée à la clé `"attached_files"`. Exemple&nbsp;:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Les chemins relatifs peuvent être utilisés, ils sont répliqués dans l'archive ZIP. Les chemins absolus sont interdits et génèrent une erreur empêchant la conversion de se terminer. S'il y a une erreur (fichier intégré manquant ou défini par un chemin absolu), la conversion est abandonnée. Lorsqu'elle est utilisée via le workflow GitHub (voir ci-dessous), les notebooks suivants sont générés, mais le statut d'exécution du workflow est défini sur échec, et le résumé affiche le notebook défectueux (voir [Workflow GitHub](#workflow-gitHub)).

Remarque&nbsp;: Dans les environnements basés sur Jupyter, la modification des métadonnées d'un notebook se fait dans la zone  _ADVANCED TOOLS_, sous  _Notebook metadata_. Dans Jupyter, on y accède en activant _View_ > _Right Sidebar_ > _Show notebook tools_. Dans JupyterLab, il se trouve dans _Property Inspector_ (icône d'engrenage) dans la barre latérale droite.

### Déclenchement de la conversion et branches

Ce workflow utilise deux branches pour générer les notebooks étudiants (mais autant de branches que nécessaire peuvent être créées, elles seront simplement ignorées)&nbsp;:
* La branche  `main` contient les versions solutions et les ressources nécessaires (elle peut également contenir d'autres matériaux, qui sont ignorés). Pousser un notebook sur cette branche déclenche sa conversion, à condition que le notebook poussé soit dans un répertoire surveillé (tel que défini dans la section `notebooks_dir` du fichier de configuration).
* La branche `Students` reçoit seulement les sorties explicitement publiées, à leur emplacement relatif d’origine. Ses autres fichiers sont préservés ; les ressources sources non déclarées ne sont pas recopiées automatiquement.

Veuillez noter que la conversion peut prendre plusieurs dizaines de secondes. Ce délai total comprend à la fois le temps d'attente pour qu'un runner GitHub Actions devienne disponible (ce qui peut être long si aucun runner n'est libre) et le temps nécessaire pour traiter réellement la tâche. Le temps d'exécution dépend du nombre de notebooks à convertir et de leur longueur. L'exécution d'autres workflows dans le dépôt en même temps peut également augmenter le temps d'exécution global. De plus, pour éviter des conversions inutiles, les répertoires `.ipynb_checkpoints` peuvent être ajoutés à `.gitignore`.

### Commandes de pré et post-traitement

Les options  `pre_processing` et `post_processing` dans `nbworkshop_convert.json` permettent d'exécuter une commande avant ou après que toutes les conversions de notebooks soient terminées&nbsp;:
* La commande de pré-traitement est exécutée juste après la configuration du workflow et la validation du fichier de configuration
* La commande de post-traitement est exécutée après la conversion des notebooks, avant que les fichiers générés soient commités et poussés sur la branche `Students`
 
Les deux hooks s’exécutent dans le checkout temporaire de `main` : le prétraitement avant conversion, le post-traitement après conversion et avant publication Git. Ils peuvent appeler les scripts du dépôt source. Leurs modifications temporaires ne mettent pas à jour `main`. Ils ne doivent pas changer de branche : la publication utilise un worktree distinct. Un échec de hook arrête la publication ; ses sorties figurent dans le résumé Actions.

Le post-traitement accède aux fichiers générés, mais ce n’est pas un hook après push confirmé. Un déploiement externe qui doit attendre cette confirmation doit rester dans une étape distincte en aval.

Pour installer aussi PPTAnim2PDF, copiez les deux workflows, leurs convertisseurs et leurs helpers de publication sous `.github/`, en conservant les chemins. Les deux outils fournissent le même fichier neutre `.github/scripts/publish_outputs.py`. Conservez `.github/nbworkshop_convert.json` : aucune migration vers un JSON commun n’est nécessaire. Chaque workflow traite ses types de sources et ses sorties ; un push mixte peut donc lancer les deux. PPTAnim2PDF ne doit pas écraser le rapport nbworkshop `Students/README.md`.

Tests de publication : `python -m unittest discover -s tests -p 'test_nbworkshop_publish.py' -v`.

Notez également que la permission `actions: write` a été activée, permettant aux commandes de déclencher d'autres workflows en utilisant GitHub CLI (`gh workflow run`)  sans nécessiter de jetons d'accès personnels supplémentaires. Cela nécessite que les workflows cibles déclarent un déclencheur workflow_dispatch. Faites simplement attention aux règles de déclenchement, car des déclencheurs qui se chevauchent peuvent provoquer plusieurs exécutions.


</details>
