# nbworkshop

## Presentation

_nbworkshop_ is a lightweight tool for educators using Jupyter Notebooks, designed to streamline the preparation and sharing of exercises with hidden corrections or answers, without the overhead of a full assignment management system like nbgrader. While nbgrader provides a comprehensive system for assignment distribution, collection, and automated grading, which requires a structured workflow and full-cell tagging for solutions, _nbworkshop_ focuses on offering teachers simple and straightforward control over the visibility of answers and explanations, allowing them to mark specific parts of any cell, whether code or markdown.

When generating the Student version, _nbworkshop_ automatically removes only the indicated corrections or answers, leaving the rest of the content untouched. This approach works seamlessly for both code completion tasks and open-ended or conceptual questions, and does not require any imposed file structure or grading setup.
![example](https://github.com/user-attachments/assets/be557bda-6294-432e-8739-4d19538a341e)


For users working with GitHub, _nbworkshop_ also provides a workflow that monitors specific directories and, whenever a Notebook within these monitored directories is updated on the main branch, automatically generates Student versions of those Notebooks that is stored on a specific branch. An archive (ZIP) containing these student versions, along with any necessary attachments, can also be created and stored in the same branch. This makes it easy to distribute up-to-date materials to students while keeping instructor content private and organized. Note that this workflow can be easily adapted to Gitlab or BitBucket using their respective CD/CI tools.

**Key features:**
- **Precision and clarity** : Easily ark specific lines/blocks in code/markdown cells
- **Instant conversion** : Generate student versions (and optional self-contained ZIP archive) with one command
- **GitHub Integrated**: GitHub Actions integration for automatic push-triggered generation ([manual trigger](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow) also possible)
- **Automation-ready** : Can easily be integrated to other CD/CI chains
- **Configurable** : Custom markers/placeholders and naming pattern via simple JSON config

## Usage

### Configuration

All _nbworkshop_ code is in the `.github` directory. It contains:
 * `.github/scripts/student_version.py`: the Python script that converts Tutor Notebooks to Students Notebooks, and creates ZIP archives with all the attached files.
 * `.github/workflows/generate_student_version.yml`: The Github workflow that calls the aforementioned Python script every time a Notebook is pushed on the repository's `main` branch.
 * `.github/config.json`: The configuration file. This is where Notebook directories, text replacement, and placeholders must be defined.

The configuration file is straightforward:
```json
{
    "notebooks_dir": ["notebooks", "ASSIGNMENTS"],
    "solution_marker": {
        "code": "#SOLUTION",
        "markdown": "blockquote"
    },
    "placeholder": {
        "code": "#TO COMPLETE",
        "markdown": "<em>TO COMPLETE</em>"
    },
    "tutor_postfix": "_Tutor",
    "student_postfix": "_Student",
    "generate_zip": true,
	"post_command": "echo 'Post-processing completed' || true"
}
```
* Workflow options (ignored by the conversion script):
	* **`notebooks_dir`** (mandatory): List of directories to process
	* **`post_command`** (optional): Post-processing shell command to be executed by the workflow
* Conversion options (all mandatory for conversion script):
	* **`solution_marker`**: Dictionary of markers identifying solution content
	* **`placeholder`**: Dictionary of replacement text for removed solutions
	* **`generate_zip`**: Boolean enabling ZIP archives to be generated

Note: In order to avoid useless convertions, `.ipynb_checkpoints` directories should be added to `.gitignore`.

### Branches

You can create as many branches as you want, but only two branches are used by _nbworkshop_ for generating student notebooks:
 * The `main` branch is the one that triggers conversions. It contains the corrected versions and the necessary resources. It can also contain other materiels, which is ignored.
 * The `Students` branch is generated automatically. Its content must not be modified, as it is fully rewritten each time a conversion occurs. It contains the same content (including subdirectories structure) as the directories monitored in `main` branch, except that solutions are removed from the Notebooks, whether for code or for questions in the text. If an original Notebook's filename ends with the configured `tutor_postfix`, this postfix is replaced by `student_postfix` in the converted Notebook's filename. If the original name does not end with `tutor_postfix`, the `student_postfix` is simply appended to the base name. No additional characters (such as underscores or spaces) are inserted automatically; the exact format is entirely determined by the postfix values set in the configuration.

For each notebook, a zip archive can be generated automatically and added in the `ZIP` subdirectory of each directory containing converted Notebooks. Each archive contains one Notebook and all embedded files. These files must be referenced directly in the global metadata of the notebook, as a list associated with the key `"attached_files"`. 

Example:
```json
"attached_files": [
	"picture1.png",
	"img/picture2.jpg"
]
```

Relative paths can be used, they are replicated in the ZIP archive. Absolute paths are forbidden and generate an error preventing the conversion to complete.

If there is an error (embedded file missing or defined by an absolute path), the conversion is aborted. When used through the Github workflow, subsequent Notebooks are generated, but the workflow execution status is set to failed, and the summary displays the faulty Notebook.

Note: In Jupyter-based environnements, editing the metadata of a notebook is done in the _ADVANCED TOOLS_ area, under _Notebook metadata_. In Jupyter, it can be accessed by enabling _View_ > _Right Sidebar_ > _Show Notebook tools_. In JupyterLab, it's located in the _Property Inspector_ (gear icon) in the right sidebar.


### Github workflow

The conversion is managed by a Github workflow called `Students Notebook generation`. This workflow is run every time a Notebook from a monitored directory is pushed on the `main` branch, but it can also be run manually from the workflow page in the `Action` tab on the Github repository web page. This workflow can be overseen on the same page. Every time the workflow is run, a short rundown  of the conversion process is shown in the workflow summary:
![summary](https://github.com/user-attachments/assets/545d2bd4-8740-4ebc-8675-a7ac4e952cfb)


Please note that updating the  `Students` branch may take a several dozens of seconds. This total delay includes both the time spent waiting for a GitHub Actions runner to become available (which can be long if no runners are free) and the time required to actually process the job. The execution time depends on how many Notebooks need to be converted and their length. Running other workflows in your repository at the same time may also increase the overall completion time.

For more information on how to manage and monitor Github workflow, see [official GitHub Actions documentation](https://docs.github.com/en/actions/writing-workflows/quickstart).

### Conversion script stand-alone usage (or integration in other CD/CI environments)

If you prefer not to use GitHub workflows, you can manually run the Python script that generates student notebooks (in `.github/scripts/student_version.py` but i can be moved anywhere). Here's the command-line interface:
```bash
python student_version.py [NOTEBOOK_PATHS] \
    --config [PATH] \
    --hide-header
```

 * `NOTEBOOK_PATHS`: Process specific notebooks (supports glob patterns: `*.ipynb`, `**/exercises/*.ipynb`)
 * `--config`: Specify alternative config path (default: `./config.json`)
 * `--hide-header` : Suppress Markdown table headers for embedding in reports
 
The student version is created in the same directory as the original notebook. The summary is sent to the standard output. Notebooks are refered by absolute path if not in the hierarchy of the current working directry.

Depending on whether batch processing is performed internally by the script or not, the `--hide-header` option can be used to generate a summary table without a header, in order to concatenate the report sheet lines successively generated by the script. This can be useful when integrating the script in another CD/CI pipeline (or any batch processing).

## Corrections format

Note that _nbworkshop_ can use any replacement text/tags and placeholder the user defines. In the following explanations, English versions are used.

### Correction in `Code` cells
To create a line or block of correction, you need to add the comment `#SOLUTION` at the end of each line of the block. The block is replaced by a single placeholder `#TO COMPLETE`. Example:

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

You can add regular comments, placed before `#SOLUTION` on the same line. Example:
```python
y = x #comment #SOLUTION
```

You can also add comments specifically for tutors after `#SOLUTION` on the same line. Example:
```python
y = x #SOLUTION comment for the tutor
```

### Correction in Markdown cells

Corrections and comments are placed in a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> tag. They are replaced by a single placeholder <code>&lt;em&lt;TO COMPLETE&lt;/em&lt;</code>. Sometimes, Jupyter can't interpret Markdown code inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>. In this case, you need to revert to HTML formatting.

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
    
If there is a blank line between the question and the answer, the placeholder is placed on the line below the question. Example :
```HTML
Question ?
<blockquote>
    Expected answer.
</blockquote>
```
    
is replaced by:
```html
Question ?
<em>TO COMPLETE</em>
```
    
### Note addressed to the tutor

A note only addressed to the tutor can be added in the notebook. This note is completely removed from the student Notebook. It must be placed in markdown cells, inside a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code>  block with the class <code>"comment"</code>. Example:
```html
WS text.<br>
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
This is a markdown cell that does not appear at all in the Students version. You must create a cell containing only a <code>&lt;blockquote&gt;&lt;/blockquote&gt;</code> block. The cell is then entirely removed when generating the student version.
