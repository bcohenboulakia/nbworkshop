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
<img width=400 src="https://github.com/user-attachments/assets/db55c14a-c1f1-4731-a9cb-569d3129a371">
</p>

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
![example](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

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

To place this note inside a single paragraph in the student version, chain the text and notes without a line break above or below the comment.
Example:
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
	* "tutor_postfix": String replaced by the value of "student_postfix" for the Notebook filename.
	* "student_postfix": String replacing the value of "tutor_postfix" for the Notebook filename.
* Workflow options (ignored by the conversion script):
	* `notebooks_dir` (mandatory): List of directories to process
	* `pre_processing` and `post_processing` (optional): Pre and Post-processing shell commands to be executed by the workflow, allowing for example to modify the notebooks before conversion, and send the generated ZIP archives to a LMS.
	
The configuration file is located in different places depending on the mode of use:
- **Using GitHub workflow**: `.github/conversion.json` (in current directory)
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

The conversion can be automated by a GitHub Actions workflow called `Generate Students Notebooks branch` which calls the conversion script on every update of a Notebook in a monitored directory. Note that the GitHub workflow shares the `.github/conversion.json` as configuration file (including for calling the conversion script), and provides detailed error log in case this file is invalid (or missing).

The result of the workflow execution can be reviewed on the README.md of the Students branch which contains a short overview of the conversion process :

A copy of this review appears on the workflow page in the `Action` tab on the GitHub repository web page;
![summary](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)

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

These command are executed on the Students branch. It means they only have access to the processed/converted Notebooks, not the original versions from the main branch. This allows for example to modify notebooks before conversion (removing for example changelogs or adding dates), and send all the generated ZIP archives to a LMS using its API (which could be considered as _TeachOps_...). The standard output of the command execution is added to the process summary. Markdown can be used to format this output. If the execution failed, the execution error output is also displayed.

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
