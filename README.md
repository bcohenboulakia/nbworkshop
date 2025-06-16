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
<img width=400 alt="nbworkshop logo" src="https://github.com/user-attachments/assets/f951e693-326a-493d-912e-17696b5c9690">
</p>

[🇫🇷 Aller à la version française 🇫🇷](#-version-française-)

## Content:
- [Presentation](#presentation)
- [Installation and Prerequisites](#installation-and-prerequisites)
- [Quick start](#quick-start)
- [Solution formatting](#solution-formatting)
   * [solution in Code cells](#solution-in-code-cells)
   * [Solution in Markdown cells](#solution-in-markdown-cells)
   * [Note addressed to the tutor](#note-addressed-to-the-tutor)
   * [Cell entirely addressed to the tutor](#cell-entirely-addressed-to-the-tutor)
- [Configuration file](#configuration-file)
- [Conversion process](#conversion-process)
   * [Conversion script](#conversion-script)
   * [Notebooks filename](#notebooks-filename)
   * [Zip archive and attached files](#zip-archive-and-attached-files)
- [GitHub workflow](#github-workflow)
   * [Conversion triggering and branches](#conversion-triggering-and-branches)
   * [Pre and post-processing command](#pre-and-post-processing-command)



## Presentation

_nbworkshop_ is a streamlined tool designed for educators who use Jupyter Notebooks to tech Python and need to efficiently prepare and distribute exercise Notebooks with hidden solutions or instructor-only comments:
![Simple nbworkshop example](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

Unlike more comprehensive systems such as _nbgrader_, _nbworkshop_ prioritizes simplicity and flexibility, allowing teachers to mark specific parts of any cell-whether code or markdown-for removal in student versions, without imposing a rigid file structure or complex workflow. An archive (ZIP) containing these student versions, along with any necessary attachments, can also be created. This makes it easy to distribute up-to-date materials to students while keeping instructor content private and organized.

For users working with GitHub, _nbworkshop_ also provides a workflow that monitors specific directories and, whenever a Notebook within these monitored directories is updated on the main branch, automatically generates Student versions of those Notebooks that is stored on a specific branch. If ZIP archives are to be created, they are stored in the same branch. Note that this workflow can be easily adapted to GitLab or BitBucket using their respective CD/CI tools.

**Key features:**
- **Targeted Solution and instructions Hiding**: Teachers can precisely mark individual lines or blocks in both code and markdown cells as solutions. They are removed and replaced with placeholders, clearly indicating where students need to provide their answers. Instructor notes can also be provided, they are removed in the student version. All other content remains unchanged.
- **Automatic Batch Processing**: The conversion tool can process multiple Notebooks at once, generating student versions and optional ZIP archives containing all referenced attachments. 
- **GitHub Integration**: A pre-configured GitHub Actions workflow automatically regenerates the student versions and archives whenever Notebooks are updated on the main branch ([manual trigger](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow) is also possible). All the generated material is stored in a specific branch.
- **Automation-ready and extensible**: Offers complete adaptability, allowing to either extend the existing workflow with custom processing steps or integrate the conversion script to an entirely new workflow tailored to specific environment and requirements (using other CI/CD chains if needed).
- **Flexible Configuration**: All markers, placeholders, and naming conventions are controlled via a simple JSON configuration file, making adaptation to different teaching styles and environments straightforward. One can for example use a code placeholder that raises a `NotImplementedError`.

## Installation and Prerequisites

_nbworkshop_ can be used in two different ways:
 * Using the GitHub workflow (no prerequisites)<br>
 The project is entirely self-contained when used with the integrated GitHub workflow. In this case, no prerequisites or additional installation steps are required. Simply clone the repository to get started (see [Quick start](#quick-start)).
 * Direct use of the conversion script<br>
   If you want to run the conversion script directly on your machine, you will need:
	* Python (version 3.12 or later)
	*  BeautifulSoup to process Markdown cells (the script has been tested against BeautifulSoup 4.9.0).
	
   In this case, the script can be moved anywhere, provided that it can access the configuration file. Have a look at [Conversion script](#conversion-script) below for more details.

All _nbworkshop_ code is in the `.github` directory. It contains:
 * `.github/scripts/student_version.py`: the Python script that converts Tutor Notebooks to Students Notebooks, and creates ZIP archives with all the attached files. If used alone, this script can be moved anywhere, provided it still has access to the configuration file
 * `.github/workflows/generate_student_version.yml`: The GitHub workflow that calls the aforementioned Python script every time a Notebook is pushed on the repository's `main` branch.
 * `.github/conversion.json`: The configuration file. This is where parameters such as Notebook directories, text replacement, placeholders etc. are defined.


## Quick start
In workflow mode, _nbworkshop_ is entirely hosted on GutHub and requires no prerequisites (aside a GitHub account). To get started using this workflow:
1. Clone this repository
2. Add Notebooks to the clone repository
3. Edit `.github/conversion.json` to insert in `"notebooks_dir"` the directory containing the Notebooks you created (see [Configuration file](#configuration-file) for a detailed explanation)
4. Edit the Notebooks (see [Solution formatting](#solution-formatting) for more detailed explanation on formatting solutions):
	- In code cells, add `#SOLUTION` to each line of code cells that the students have to figure out by themselves.
	- In Markdown cells, add answers to the questions inside `<blockquote>`tags. Be sure to leave the HTML tags alone on their lines.  
5. Commit the  Notebooks on the main branch, and push them to the GitHub repository

The newly created `Students` branch contains the Students versions of the Notebooks (and ZIP archives), with solutions replaced by placeholders and all execution traces (including calculation results and cell execution counters) removed. Those converted Notebooks are updated on every push on the main branch.

## Solution formatting

Note that _nbworkshop_ can use any replacement text/tags and placeholder the user defines (see [Configuration file](#configuration-file)). In the following explanations, default versions are used.

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

A note only addressed to the tutor can be added in the Notebook. This note is completely removed from the student Notebook. It must be placed in markdown cells, inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>  block with the class <code>"comment"</code>. Example:
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
This is a markdown cell that does not appear at all in the Students version. It's a cell containing only a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> block. The cell is then entirely removed when generating the student version.

## Configuration file

The configuration file includes options for both conversion and GitHub workflow. Each one only takes into account the relevant options:
```json
{
    "notebooks_dir": ["notebooks", "ASSIGNMENTS"],
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
    "pre_processing": "echo 'Pre-processing completed' || true"
    "post_processing": "echo 'Post-processing completed' || true"
}
```

* Conversion options (all mandatory for the conversion script, ignored by the workflow):
	* `solution_marker`: Dictionary of markers identifying solution content, containing only the core text, which is either wrapped as an HTML tag for Markdown or prefixed with a comment character for Python.
	* `placeholder`: Dictionary of replacement text for removed solutions
	* `generate_zip`: Boolean enabling ZIP archives to be generated
	* `tutor_postfix`: String replaced by the value of `student_postfix` for the Notebook filename.
	* "student_postfix": String replacing the value of `tutor_postfix` for the Notebook filename.
* Workflow options (ignored by the conversion script):
	* `notebooks_dir` (mandatory): List of directories to process
	* `pre_processing` and `post_processing` (optional): Pre and Post-processing shell commands to be executed by the workflow, allowing for example to modify the notebooks before conversion, and send the generated ZIP archives to a LMS.
	
The configuration file is located in different places depending on the mode of use:
- **Using GitHub workflow**: `.github/conversion.json`
- **Manual script use**: `./conversion.json` (in current directory), but can be changed through commandlin option (see [Conversion script](#conversion-script))

## Conversion process

### Conversion script

The Python script that generates student Notebooks can be found in `.github/scripts/student_version.py`. If it's run through the GitHub workflow, there's no need to know anything about it. Everything (including paths of the generated files, and error management) is handled by the workflow, and through the configuration file.

If manually run (that is, not through the GitHub workflow), the student version is created in the same directory as the original Notebook. Here's the command-line interface:
```bash
python student_version.py NOTEBOOK_PATHS [--config PATH] [--hide-header]
```

 * `NOTEBOOK_PATHS`: Process specific Notebooks (supports glob patterns: `*.ipynb`, `**/exercises/*.ipynb`)
 * `--config` (optional): Specify alternative config path (default: `./conversion.json`)
 * `--hide-header` (optional): Suppress Markdown table headers for embedding in reports
 
The summary of the conversion process is sent to the standard output. In this summary, Notebooks are refered by absolute path if not in the hierarchy of the current working directry. Depending on whether batch processing is performed internally by the script or not, the `--hide-header` option can be used to generate a summary table without a header, in order to concatenate the report sheet lines successively generated by the script. This can be useful when integrating the script in an external batch processing (such as a CI/CD pipeline).

**Important note on configuration**: When the script is used manually, it defaults to the `./conversion.json` file in the current directory, unlike the GitHub workflow which uses `.github/conversion.json`.

### Notebooks filename

Every solution marker in processed Notebooks is replaced by the corresponding placeholder (both can be set in the [Configuration file](#configuration-file)). If an original Notebook's filename ends with the configured `tutor_postfix` parameter (see [Configuration](#configuration)), this postfix is replaced by the `student_postfix` parameter in the converted Notebook's filename. If the original name does not end with `tutor_postfix`, the `student_postfix` value is simply appended to the base name. No additional characters (such as underscores or spaces) are inserted automatically; the exact format is entirely determined by the postfix values set in the configuration.

## GitHub workflow

The conversion can be automated by a GitHub Actions workflow called `Generate Students Notebooks branch` which calls the conversion script on every update of a Notebook in a monitored directory. Note that the GitHub workflow uses `.github/conversion.json` as configuration file (including for calling the conversion script), and provides detailed error log in case this file is invalid (or missing).

The result of the workflow execution can be reviewed on the `README.md` of the Students branch which contains a short overview of the conversion process:
![Student branch README](https://github.com/user-attachments/assets/bc132feb-5f43-40e7-aa64-962154bc15b1)

A copy of this review appears on the workflow page in the `Action` tab on the GitHub repository web page:
![GitHub Actions summary](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)


The workflow can also be run manually from the same tab. For more information on how to manage and monitor GitHub workflow, see the [official GitHub Actions documentation](https://docs.github.com/en/actions/writing-workflows/quickstart).

### Zip archive and attached files

For each processed Notebook, if ZIP archives are to be generated (see the _Configuration_ section below), they are added in the `ZIP` subdirectory of each directory containing converted Notebooks. Each archive contains one Notebook and all embedded files. These files must be referenced directly in the global metadata of the Notebook, as a list associated with the key `"attached_files"`. Example:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Relative paths can be used, they are replicated in the ZIP archive. Absolute paths are forbidden and generate an error preventing the conversion to complete. If there is an error (embedded file missing or defined by an absolute path), the conversion is aborted. When used through the GitHub workflow (see below), subsequent Notebooks are generated, but the workflow execution status is set to failed, and the summary displays the faulty Notebook (see [GitHub workflow](#github-workflow)).

Note: In Jupyter-based environnements, editing the metadata of a Notebook is done in the _ADVANCED TOOLS_ area, under _Notebook metadata_. In Jupyter, it can be accessed by enabling _View_ > _Right Sidebar_ > _Show Notebook tools_. In JupyterLab, it's located in the _Property Inspector_ (gear icon) in the right sidebar.

### Conversion triggering and branches

This workflow uses two branches to generate student Notebooks (but as many branches as needed can be created, they will just be ignored):
 * The `main` branch contains the solution versions and the necessary resources (it can also contain other materials, which are ignored). Pushing a Notebook on this branch triggers its conversion, provided the pushed Notebook is in a monitored directory (as defined in the `notebooks_dir` section of the configuration file).
 * The `Students` branch is generated automatically. Its content must not be modified, as it is fully rewritten each time a conversion occurs. It contains the same content (including subdirectories structure) as the directories monitored in `main` branch, except that solutions and instructor notes are removed from the Notebooks, whether for code or for questions in the text.

Please note that conversion may take several dozens of seconds. This total delay includes both the time spent waiting for a GitHub Actions runner to become available (which can be long if no runners are free) and the time required to actually process the job. The execution time depends on how many Notebooks need to be converted and their length. Running other workflows in the repository at the same time may also increase the overall completion time. Moreover, in order to avoid useless conversions, `.ipynb_checkpoints` directories should be added to `.gitignore`.

### Pre and post-processing command

The `pre_processing` and `post_processing` options in `conversion.json` allow executing a command before or after all Notebook conversions are completed:
 - The pre-processing command is run just after setting up the workflow and validating the configuration file
 - The post-processing command is run the Students branch has been commited and pushed

By default (but it can be changed, see below), these command are executed on the Students branch with mainly two consequences:
* The pre-processing command can modify any file without the changes impacting the main branch. This allows for example to modify notebooks before conversion (removing changelogs or adding dates)
* The post-processing has access to the files generated by the workflow. This allows for example to send all the generated ZIP archives to a LMS using its API (which could be considered as _TeachOps_...).

The standard outputs of the commands execution are added to the process summary. Markdown can be used to format those output. If the execution failed, the execution error output is also displayed.

The pre and post-processing commands can execute any shell command that is available in the GitHub Actions runner environment (see [Adding scripts to your workflow](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow) and [Workflow commands for GitHub Actions](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions)). Notably, It is possible to switch branches within the post-processing command using the standard Git checkout command:
```bash
git checkout main
```
This branch-switching capability can be included at the beginning of your post-command string:
```yaml
"post_processing": "git checkout main && ./your-program"
```
It can also be done from the called program itself through external command execution.

Also note that the `actions: write` permission has been enabled, allowing commands to trigger other workflows using GitHub CLI (`gh workflow run`) without requiring additional personal access tokens. This requires target workflows to declare a `workflow_dispatch` trigger. Just be careful with trigger rules, as overlapping triggers can cause multiple executions.

## 🇫🇷 Version française 🇫🇷

<details>
  <summary>Montrer/Cacher</summary>
  

## Contenu&nbsp;:
- [Présentation](#présentation)
- [Installation et Prérequis](#installation-et-prérequis)
- [Démarrage rapide](#démarrage-rapide)
- [Formatage des solutions](#formatage-des-solutions)
   * [Solution dans les cellules de code](#solution-dans-les-cellules-de-code)
   * [Solution dans les cellules Markdown](#solution-dans-les-cellules-markdown)
   * [Note destinée au tuteur](#note-destinée-au-tuteur)
   * [Cellule entièrement destinée au tuteur](#cellule-entièrement-destinée-au-tuteur)
- [Fichier de configuration](#fichier-de-configuration)
- [Processus de conversion](#processus-de-conversion)
   * [Script de conversion](#script-de-conversion)
   * [Nom des fichiers des Notebooks](#nom-des-fichiers-des-notebooks)
   * [Archive Zip et fichiers joints](#archive-zip-et-fichiers-joints)
- [Workflow GitHub](#workflow-github)
   * [Déclenchement de la conversion et branches](#déclenchement-de-la-conversion-et-branches)
   * [Commandes de pré et post-traitement](#commandes-de-pré-et-post-traitement)

## Présentation

_nbworkshop_ est un outil simplifié conçu pour les enseignants utilisant des Notebooks Jupyter pour enseigner Python, qui ont besoin de préparer et distribuer efficacement des Notebooks d'exercices avec des solutions cachées ou des commentaires réservés aux instructeurs&nbsp;:
![Exemple simple nbworkshop](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

Contrairement à des systèmes plus complets comme _nbgrader_, _nbworkshop_ privilégie la simplicité et la flexibilité, permettant aux enseignants de marquer des parties spécifiques de n'importe quelle cellule - code ou markdown - pour suppression dans les versions étudiantes, sans imposer de structure de fichiers rigide ou de workflow complexe. Une archive (ZIP) contenant ces versions étudiantes, ainsi que toutes les pièces jointes nécessaires, peut également être créée. Cela facilite la distribution de matériel actualisé aux étudiants tout en gardant le contenu enseignant privé et organisé.

Pour les utilisateurs travaillant avec GitHub, _nbworkshop_ fournit également un workflow qui surveille des répertoires spécifiques et, à chaque mise à jour d'un Notebook dans ces répertoires surveillés sur la branche principale, génère automatiquement les versions étudiantes de ces Notebooks stockées sur une branche dédiée. Si des archives ZIP doivent être créées, elles sont stockées dans cette même branche. Notez que ce workflow peut être facilement adapté à GitLab ou BitBucket en utilisant leurs outils CD/CI respectifs.

**Fonctionnalités clés&nbsp;:**
- **Masquage ciblé des solutions et instructions**&nbsp;: Les enseignants peuvent marquer précisément des lignes ou blocs individuels dans les cellules de code et markdown comme solutions. Ils sont supprimés et remplacés par des espaces réservés, indiquant clairement où les étudiants doivent fournir leurs réponses. Des notes pour l'instructeur peuvent également être fournies, elles sont supprimées dans la version étudiante. Tout autre contenu reste inchangé.
- **Traitement par lots automatique**&nbsp;: L'outil de conversion peut traiter plusieurs Notebooks simultanément, générant des versions étudiantes et des archives ZIP optionnelles contenant toutes les pièces jointes référencées.
- **Intégration GitHub**&nbsp;: Un workflow GitHub Actions préconfiguré régénère automatiquement les versions étudiantes et archives à chaque mise à jour des Notebooks sur la branche principale ([déclenchement manuel](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow) également possible). Tout le matériel généré est stocké dans une branche spécifique.
- **Prêt pour l'automatisation et extensible**&nbsp;: Offre une adaptabilité complète, permettant soit d'étendre le workflow existant avec des étapes de traitement personnalisées, soit d'intégrer le script de conversion dans un workflow entièrement nouveau adapté à des environnements et besoins spécifiques (utilisation d'autres chaînes CI/CD si nécessaire).
- **Configuration flexible**&nbsp;: Tous les marqueurs, espaces réservés et conventions de nommage sont contrôlés via un simple fichier de configuration JSON, rendant l'adaptation à différents styles d'enseignement et environnements directe. On peut par exemple utiliser un espace réservé de code qui lève une `NotImplementedError`.

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
 * `.github/scripts/student_version.py`&nbsp;: le script Python qui convertit les Notebooks Tuteur en Notebooks Étudiants, et crée des archives ZIP avec tous les fichiers joints. S'il est utilisé seul, ce script peut être déplacé n'importe où, à condition d'avoir toujours accès au fichier de configuration
 * `.github/workflows/generate_student_version.yml`&nbsp;: Le workflow GitHub qui appelle le script Python susmentionné à chaque fois qu'un Notebook est poussé sur la branche `main` du dépôt.
 * `.github/conversion.json`&nbsp;: Le fichier de configuration. C'est ici que sont définis les paramètres tels que les répertoires des Notebooks, les remplacements de texte, les espaces réservés, etc.

## Démarrage rapide
En mode workflow, _nbworkshop_ est entièrement hébergé sur GitHub et ne nécessite aucun prérequis (à part un compte GitHub). Pour commencer à utiliser ce workflow&nbsp;:
1. Clonez ce dépôt
2. Ajoutez des Notebooks au dépôt cloné
3. Modifiez `.github/conversion.json` pour insérer dans `"notebooks_dir"` le répertoire contenant les Notebooks que vous avez créés (voir [Fichier de configuration](#fichier-de-configuration) pour une explication détaillée)
4. Modifiez les Notebooks (voir [Formatage des solutions](#formatage-des-solutions) pour des explications plus détaillées sur le formatage des solutions)&nbsp;:
	- Dans les cellules de code, ajoutez `#SOLUTION` à chaque ligne des cellules de code que les étudiants doivent trouver par eux-mêmes.
	- Dans les cellules Markdown, ajoutez les réponses aux questions entre des balises `<blockquote>`. Veillez à laisser les balises HTML seules sur leurs lignes.  
5. Committez les Notebooks sur la branche principale et poussez-les vers le dépôt GitHub

La nouvelle branche `Students` contient les versions étudiantes des Notebooks (et archives ZIP), avec les solutions remplacées par des espaces réservés et toutes les traces d'exécution (y compris les résultats de calcul et les compteurs d'exécution de cellules) supprimées. Ces Notebooks convertis sont mis à jour à chaque poussée sur la branche principale.

## Formatage des solutions

Notez que _nbworkshop_ peut utiliser n'importe quel texte de remplacement/balises et espace réservé défini par l'utilisateur (voir [Fichier de configuration](#fichier-de-configuration)). Dans les explications suivantes, les versions par défaut sont utilisées.

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

Une note uniquement destinée au tuteur peut être ajoutée dans le Notebook. Cette note est complètement supprimée du Notebook étudiant. Elle doit être placée dans des cellules markdown, à l'intérieur d'un bloc <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>avec la classe <code>"comment"</code>. Exemple&nbsp;:
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
Il s'agit d'une cellule markdown qui n'apparaît pas du tout dans la version Étudiante. C'est une cellule contenant uniquement un bloc <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. La cellule est alors entièrement supprimée lors de la génération de la version étudiante.

## Fichier de configuration

Le fichier de configuration inclut des options pour la conversion et le workflow GitHub. Chacun ne prend en compte que les options pertinentes&nbsp;:
```json
{
    "notebooks_dir": ["notebooks", "ASSIGNMENTS"],
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
    "pre_processing": "echo 'Pre-processing completed' || true"
    "post_processing": "echo 'Post-processing completed' || true"
}
```

* Options de conversion (toutes obligatoires pour le script de conversion, ignorées par le workflow)&nbsp;:
	* `solution_marker`&nbsp;: Dictionnaire des marqueurs identifiant le contenu solution, contenant uniquement le texte central, qui est soit encapsulé comme une balise HTML pour Markdown, soit préfixé par un caractère de commentaire pour Python.
	* `placeholder`&nbsp;:  Dictionnaire du texte de remplacement pour les solutions supprimées
	* `generate_zip`&nbsp;: Booléen activant la génération d'archives ZIP
	* `tutor_postfix`&nbsp;: Chaîne remplacée par la valeur de `student_postfix` pour le nom de fichier du Notebook.
	* `student_postfix`&nbsp;: Chaîne remplaçant la valeur de `tutor_postfix` pour le nom de fichier du Notebook.
* Options de workflow (ignorées par le script de conversion)&nbsp;:
	* `notebooks_dir` (obligatoire)&nbsp;: Liste des répertoires à traiter
	* `pre_processing` et `post_processing` (optionnel)&nbsp;: Commandes shell de pré et post-traitement à exécuter par le workflow, permettant par exemple de modifier les notebooks avant conversion et d'envoyer les archives ZIP générées à un LMS.
	
Le fichier de configuration se trouve à différents endroits selon le mode d'utilisation&nbsp;:
- **Utilisation du workflow GitHub**&nbsp;: `.github/conversion.json`
- **Utilisation manuelle du script**&nbsp;: `./conversion.json` (dans le répertoire courant), mais peut être changé via une option en ligne de commande (voir [Script de conversion](#script-de-conversion))

## Processus de conversion

### Script de conversion

Le script Python qui génère les Notebooks étudiants se trouve dans `.github/scripts/student_version.py` S'il est exécuté via le workflow GitHub, il n'est pas nécessaire de le connaître. Tout (y compris les chemins des fichiers générés et la gestion des erreurs) est géré par le workflow et via le fichier de configuration.

S'il est exécuté manuellement (c'est-à-dire pas via le workflow GitHub), la version étudiante est créée dans le même répertoire que le Notebook original. Voici l'interface en ligne de commande&nbsp;:
```bash
python version_etudiante.py CHEMINS_NOTEBOOK  [--config PATH] [--hide-header]
```

 * `CHEMINS_NOTEBOOK `: raite des Notebooks spécifiques (supporte les motifs globaux&nbsp;:`*.ipynb`, `**/exercices/*.ipynb`)
 * `--config` (optionnel): Spécifie un chemin de configuration alternatif (par défaut&nbsp;: `./conversion.json`)
 * `--hide-header` (optionnel): Supprime les en-têtes de tableau Markdown pour l'intégration dans des rapports
 
Le résumé du processus de conversion est envoyé sur la sortie standard. Dans ce résumé, les Notebooks sont référencés par chemin absolu s'ils ne sont pas dans la hiérarchie du répertoire de travail courant. Selon que le traitement par lots est effectué en interne par le script ou non, l'option `--hide-header` peut être utilisée pour générer un tableau récapitulatif sans en-tête, afin de concaténer les lignes de feuille de rapport générées successivement par le script. Cela peut être utile lors de l'intégration du script dans un traitement par lots externe (comme un pipeline CI/CD).

**Note importante sur la configuration**&nbsp;: Lorsque le script est utilisé manuellement, il utilise par défaut le fichier `./conversion.json` dans le répertoire courant, contrairement au workflow GitHub qui utilise `.github/conversion.json`.

### Nom des fichiers des Notebooks

Chaque marqueur de solution dans les Notebooks traités est remplacé par l'espace réservé correspondant (tous deux peuvent être définis dans le [Fichier de configuration file](#fichier-de-configuration)).Si un nom de fichier de Notebook original se termine par le paramètre `tutor_postfix` configuré (voir [Configuration](#configuration)), ce suffixe est remplacé par le paramètre `student_postfix` dans le nom de fichier du Notebook converti. Si le nom original ne se termine pas par `tutor_postfix`, la valeur de  `student_postfix` est simplement ajoutée au nom de base. Aucun caractère supplémentaire (tel que des tirets bas ou des espaces) n'est inséré automatiquement&nbsp;; le format exact est entièrement déterminé par les valeurs de suffixe définies dans la configuration.

## Workflow GitHub

La conversion peut être automatisée par un workflow GitHub Actions appelé `Generate Students Notebooks branch` qui appelle le script de conversion à chaque mise à jour d'un Notebook dans un répertoire surveillé. Notez que le workflow GitHub utilise `.github/conversion.json` comme fichier de configuration (y compris pour appeler le script de conversion) et fournit un journal d'erreurs détaillé en cas de fichier invalide (ou manquant).

Le résultat de l'exécution du workflow peut être consulté sur le `README.md` de la branche Students qui contient un bref aperçu du processus de conversion&nbsp;:
![README de la branche Students](https://github.com/user-attachments/assets/bc132feb-5f43-40e7-aa64-962154bc15b1)

Une copie de cette revue apparaît sur la page du workflow dans l'onglet Action de la page web du dépôt GitHub&nbsp;:
![Sommaire de la page GitHub Actions](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)


Le workflow peut également être exécuté manuellement depuis le même onglet. Pour plus d'informations sur la gestion et la surveillance des workflows GitHub, consultez la [documentation officielle GitHub Actions](https://docs.github.com/en/actions/writing-workflows/quickstart).

### Archive Zip et fichiers joints

Pour chaque Notebook traité, si des archives ZIP doivent être générées (voir la section Configuration ci-dessous), elles sont ajoutées dans le sous-répertoire ZIP de chaque répertoire contenant des Notebooks convertis. Chaque archive contient un Notebook et tous les fichiers intégrés. Ces fichiers doivent être référencés directement dans les métadonnées globales du Notebook, comme une liste associée à la clé `"attached_files"`. Exemple&nbsp;:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Les chemins relatifs peuvent être utilisés, ils sont répliqués dans l'archive ZIP. Les chemins absolus sont interdits et génèrent une erreur empêchant la conversion de se terminer. S'il y a une erreur (fichier intégré manquant ou défini par un chemin absolu), la conversion est abandonnée. Lorsqu'elle est utilisée via le workflow GitHub (voir ci-dessous), les Notebooks suivants sont générés, mais le statut d'exécution du workflow est défini sur échec, et le résumé affiche le Notebook défectueux (voir [Workflow GitHub](#workflow-gitHub)).

Remarque&nbsp;: Dans les environnements basés sur Jupyter, la modification des métadonnées d'un Notebook se fait dans la zone  _ADVANCED TOOLS_, sous  _Notebook metadata_. Dans Jupyter, on y accède en activant _View_ > _Right Sidebar_ > _Show Notebook tools_. Dans JupyterLab, il se trouve dans _Property Inspector_ (icône d'engrenage) dans la barre latérale droite.

### Déclenchement de la conversion et branches

Ce workflow utilise deux branches pour générer les Notebooks étudiants (mais autant de branches que nécessaire peuvent être créées, elles seront simplement ignorées)&nbsp;:
 * La branche  `main` contient les versions solutions et les ressources nécessaires (elle peut également contenir d'autres matériaux, qui sont ignorés). Pousser un Notebook sur cette branche déclenche sa conversion, à condition que le Notebook poussé soit dans un répertoire surveillé (tel que défini dans la section `notebooks_dir` du fichier de configuration).
 * La branche `Students` est générée automatiquement. Son contenu ne doit pas être modifié, car il est entièrement réécrit à chaque conversion. Elle contient le même contenu (y compris la structure des sous-répertoires) que les répertoires surveillés dans la branche `main`, sauf que les solutions et notes d'instructeur sont supprimées des Notebooks, que ce soit pour le code ou pour les questions dans le texte.

Veuillez noter que la conversion peut prendre plusieurs dizaines de secondes. Ce délai total comprend à la fois le temps d'attente pour qu'un runner GitHub Actions devienne disponible (ce qui peut être long si aucun runner n'est libre) et le temps nécessaire pour traiter réellement la tâche. Le temps d'exécution dépend du nombre de Notebooks à convertir et de leur longueur. L'exécution d'autres workflows dans le dépôt en même temps peut également augmenter le temps d'exécution global. De plus, pour éviter des conversions inutiles, les répertoires `.ipynb_checkpoints` peuvent être ajoutés à `.gitignore`.

### Commandes de pré et post-traitement

Les options  `pre_processing` et `post_processing` dans `conversion.json` permettent d'exécuter une commande avant ou après que toutes les conversions de Notebooks soient terminées&nbsp;:
 - La commande de pré-traitement est exécutée juste après la configuration du workflow et la validation du fichier de configuration
 - La commande de post-traitement est exécutée après que la branche Students a été commitée et poussée
 
Par défaut (mais cela peut être modifié, voir ci-dessous), ces commandes sont exécutées sur la branche Etudiants avec principalement deux conséquences&nbsp;:
* La commande de prétraitement peut modifier n'importe quel fichier sans que les changements impactent la branche principale. Cela permet, par exemple, de supprimer les changelogs ou d'ajouter des dates aux Notebooks avant la conversion.
* La commande de post-traitement a accès aux fichiers générés par le workflow. Cela permet par exemple d'envoyer toutes les archives ZIP générées à un LMS en utilisant son API (ce qui pourrait être considéré comme du _TeachOps_...).

Les sorties standard de l'exécution des commandes sont ajoutées au résumé du processus. Markdown peut être utilisé pour formater ces sorties. Si l'exécution a échoué, la sortie de l'erreur d'exécution est également affichée.

Les commandes de pré et post-traitement peuvent exécuter toute commande shell disponible dans l'environnement du runner GitHub Actions (voir [Adding scripts to your workflow](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow) et [Workflow commands for GitHub Actions](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions)).  Notamment, il est possible de changer de branche dans la commande de post-traitement en utilisant la commande Git standard&nbsp;:
```bash
git checkout main
```
Cette capacité de changement de branche peut être incluse au début de votre chaîne de commande post&nbsp;:
```yaml
"post_processing": "git checkout main && ./your-program"
```
Elle peut également être faite depuis le programme appelé lui-même via l'exécution de commande externe.

Notez également que la permission `actions: write` a été activée, permettant aux commandes de déclencher d'autres workflows en utilisant GitHub CLI (`gh workflow run`)  sans nécessiter de jetons d'accès personnels supplémentaires. Cela nécessite que les workflows cibles déclarent un déclencheur workflow_dispatch. Faites simplement attention aux règles de déclenchement, car des déclencheurs qui se chevauchent peuvent provoquer plusieurs exécutions.


</details>
