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
<img width=400 src="https://github.com/user-attachments/assets/10e381e7-4365-48f7-bcf7-6476cdd0a240">
</p>

## Content:
- [Presentation](#presentation)
- [Basic usage](#basic-usage)
  - [Conversion](#conversion)
  - [Zip archive and attached files](#zip-archive-and-attached-files)
  - [Configuration](#configuration)
- [GitHub workflow](#github-workflow)
  - [Conversion and branches](#conversion-and-branches)
  - [Post-processing command](#post-processing-command)
- [Solution formatting](#solution-formatting)
  - [Solution in Code cells](#solution-in-code-cells)
  - [Solution in Markdown cells](#solution-in-markdown-cells)
  - [Note addressed to the tutor](#note-addressed-to-the-tutor)
  - [Cell entirely addressed to the tutor](#cell-entirely-addressed-to-the-tutor)
</p>

## Presentation

_nbworkshop_ is a streamlined tool designed for educators who use Jupyter Notebooks and need to efficiently prepare and distribute exercise Notebooks with hidden solutions or instructor-only comments:
![example](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)

Unlike more comprehensive systems such as _nbgrader_, _nbworkshop_ prioritizes simplicity and flexibility, allowing teachers to mark specific parts of any cell-whether code or markdown-for removal in student versions, without imposing a rigid file structure or complex workflow. An archive (ZIP) containing these student versions, along with any necessary attachments, can also be created. This makes it easy to distribute up-to-date materials to students while keeping instructor content private and organized.

For users working with GitHub, _nbworkshop_ also provides a workflow that monitors specific directories and, whenever a Notebook within these monitored directories is updated on the main branch, automatically generates Student versions of those Notebooks that is stored on a specific branch. If ZIP archives are to be created, they are stored in the same branch. Note that this workflow can be easily adapted to GitLab or BitBucket using their respective CD/CI tools.

**Key features:**
- **Targeted Solution and instructions Hiding**: Teachers can precisely mark individual lines or blocks in both code and markdown cells as solutions. They are removed and replaced with placeholders, clearly indicating where students need to provide their answers. Instructor notes can also be provided, they are removed in the student version. All other content remains unchanged.
- **Automatic Batch Processing**: The conversion tool can process multiple Notebooks at once, generating student versions and optional ZIP archives containing all referenced attachments. 
- **GitHub Integration**: A pre-configured GitHub Actions workflow automatically regenerates the student versions and archives whenever Notebooks are updated on the main branch ([manual trigger](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow) is also possible). All the generated material is stored in a specific branch.
- **Automation-ready**: Can easily be integrated to other CD/CI chains
- **Flexible Configuration**: All markers, placeholders, and naming conventions are controlled via a simple JSON configuration file, making adaptation to different teaching styles and environments straightforward. One can for example use a code placeholder that raises a `NotImplementedError`.
- 
## Basic usage

All _nbworkshop_ code is in the `.github` directory. It contains:
 * `.github/scripts/student_version.py`: the Python script that converts Tutor Notebooks to Students Notebooks, and creates ZIP archives with all the attached files. If used alone, this script can be moved anywhere, provided it still has access to the configuration file
 * `.github/workflows/generate_student_version.yml`: The GitHub workflow that calls the aforementioned Python script every time a Notebook is pushed on the repository's `main` branch.
 * `.github/conversion.json`: The configuration file. This is where Notebook directories, text replacement, and placeholders must be defined.

### Conversion

The Python script that generates student Notebooks is in `.github/scripts/student_version.py` (but it can be moved anywhere, provided that it can access the configuration file). Here's the command-line interface:
```bash
python student_version.py NOTEBOOK_PATHS [--config PATH] [--hide-header]
```

 * `NOTEBOOK_PATHS`: Process specific Notebooks (supports glob patterns: `*.ipynb`, `**/exercises/*.ipynb`)
 * `--config` (optional): Specify alternative config path (default: `./conversion.json`)
 * `--hide-header` (optional): Suppress Markdown table headers for embedding in reports
 
The student version is created in the same directory as the original Notebook. The summary is sent to the standard output. Notebooks are refered by absolute path if not in the hierarchy of the current working directry.

Depending on whether batch processing is performed internally by the script or not, the `--hide-header` option can be used to generate a summary table without a header, in order to concatenate the report sheet lines successively generated by the script. This can be useful when integrating the script in an external batch processing (such as a CD/CI pipeline).

### Zip archive and attached files

For each processed Notebook, if ZIP archives are to be generated (see the _Configuration_ section below), they are added in the `ZIP` subdirectory of each directory containing converted Notebooks. Each archive contains one Notebook and all embedded files. These files must be referenced directly in the global metadata of the Notebook, as a list associated with the key `"attached_files"`. Example:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Relative paths can be used, they are replicated in the ZIP archive. Absolute paths are forbidden and generate an error preventing the conversion to complete. If there is an error (embedded file missing or defined by an absolute path), the conversion is aborted. When used through the GitHub workflow (see below), subsequent Notebooks are generated, but the workflow execution status is set to failed, and the summary displays the faulty Notebook.

Note: In Jupyter-based environnements, editing the metadata of a Notebook is done in the _ADVANCED TOOLS_ area, under _Notebook metadata_. In Jupyter, it can be accessed by enabling _View_ > _Right Sidebar_ > _Show Notebook tools_. In JupyterLab, it's located in the _Property Inspector_ (gear icon) in the right sidebar.

### Configuration

The configuration file can include options for both conversion and GitHub automation. Each one only takes into account the relevant options:
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
    "post_processing": "echo 'Post-processing completed' || true"
}
```

* Conversion options (all mandatory for the conversion script, ignored by the workflow):
	* `solution_marker`: Dictionary of markers identifying solution content, containing only the core text, which is either wrapped as an HTML tag for Markdown or prefixed with a comment character for Python.
	* `placeholder`: Dictionary of replacement text for removed solutions
	* `generate_zip`: Boolean enabling ZIP archives to be generated
* Workflow options (ignored by the conversion script):
	* `notebooks_dir` (mandatory): List of directories to process
	* `post_processing` (optional): Post-processing shell command to be executed by the workflow, allowing for example to send the generated ZIP archives to a LMS.

## GitHub workflow

The conversion can be automated by a GitHub Actions workflow called `Generate Students Branch ` which calls the conversion script on every update of a Notebook in a monitored directory. Note that the GitHub workflow uses `.github/conversion.json` as configuration file.

This workflow can be supervised on the workflow page in the `Action` tab on the GitHub repository web page. Every time the workflow is run, a short overview of the conversion process is shown in the workflow summary:
![summary](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)

The workflow can also be run manually from the same tab. For more information on how to manage and monitor GitHub workflow, see the [official GitHub Actions documentation](https://docs.github.com/en/actions/writing-workflows/quickstart).

### Conversion triggering and branches

This workflow uses two branches to generate student Notebooks (but as many branches as needed can be created, they will just be ignored):
 * The `main` branch contains the solution versions and the necessary resources (it can also contain other materials, which are ignored). Pushing a Notebook on this branch triggers its conversion, provided the pushed Notebook is in a monitored directory (as defined in the `notebooks_dir` section of the configuration file).
 * The `Students` branch is generated automatically. Its content must not be modified, as it is fully rewritten each time a conversion occurs. It contains the same content (including subdirectories structure) as the directories monitored in `main` branch, except that solutions and instructor notes are removed from the Notebooks, whether for code or for questions in the text. If an original Notebook's filename ends with the configured `tutor_postfix`, this postfix is replaced by `student_postfix` in the converted Notebook's filename. If the original name does not end with `tutor_postfix`, the `student_postfix` is simply appended to the base name. No additional characters (such as underscores or spaces) are inserted automatically; the exact format is entirely determined by the postfix values set in the configuration.

Please note that conversion may take several dozens of seconds. This total delay includes both the time spent waiting for a GitHub Actions runner to become available (which can be long if no runners are free) and the time required to actually process the job. The execution time depends on how many Notebooks need to be converted and their length. Running other workflows in the repository at the same time may also increase the overall completion time. Moreover, in order to avoid useless conversions, `.ipynb_checkpoints` directories should be added to `.gitignore`.

### Post-processing command

The `post_processing` option in `conversion.json` allows executing a command after all Notebook conversions are completed. This command is executed on the Students branch. It means the post-command only has access to the processed/converted Notebooks, not the original versions from the main branch. This allows for example to send all the generated ZIP archives to a LMS using its API. The standard output of the command execution is added to the process summary. Markdown can be used to format this output. If the execution failed, the execution error output is also displayed.

The post-processing command can execute any shell command that is available in the GitHub Actions runner environment (see [Adding scripts to your workflow](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/adding-scripts-to-your-workflow) and [Workflow commands for GitHub Actions](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions)). Notably, It is possible to switch branches within the post-processing command using the standard Git checkout command:
```bash
git checkout main
```
This branch-switching capability can be included at the beginning of your post-command string
```yaml
"post_processing": "git checkout main && ./your-program"
```
It can also be done from the `post_processing` program itself through external Command execution.

## Solution formatting

Note that _nbworkshop_ can use any replacement text/tags and placeholder the user defines. In the following explanations, default versions are used.

### solution in `Code` cells
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

Solutions and comments are placed in a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> tag. They are replaced by a single placeholder <code>&lt;em&lt;TO COMPLETE&lt;/em&lt;</code>. Sometimes, Jupyter can't interpret Markdown code inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. In this case, reverting to HTML formatting is required.

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
