"""
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
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "beautifulsoup4>=4.9.0",  # For HTML processing in Markdown cells
# ]
# ///

import argparse
import json
import os
import zipfile
from pathlib import Path
from bs4 import BeautifulSoup
import shutil
from pathlib import Path
import subprocess

def load_config(config_path):
    """
    Load and validate configuration from JSON file
    """
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    required_keys = ["solution_marker", "placeholder",
        "tutor_postfix", "student_postfix", "generate_zip"
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    return config

def process_markdown_cell(cell, config):
    """
    Process markdown cell to remove solutions
    """
    
    stats = {"questions": 0, "remarks": 0}
    new_source = []
    in_solution = False

    for line in cell["source"]:
        soup = BeautifulSoup(line, "html.parser")
        solution = soup.find(config["solution_marker"]["markdown"])
        
        if solution:
            in_solution = True
            if "comment" in solution.get("class", []):
                stats["remarks"] += 1
            else:
                stats["questions"] += 1
                new_source.append(f"{config["placeholder"]["markdown"]}\n")
        elif in_solution:
            if f"</{config["solution_marker"]["markdown"]}>" in line:
                in_solution = False
        else:
            new_source.append(line)
    
    cell["source"] = new_source
    return cell, stats

def process_code_cell(cell, config):
    """Process code cell to remove solutions while preserving indentation"""
    stats = {"code_blocks": 0}
    new_source = []
    in_solution = False
    solution_marker = "#"+config["solution_marker"]["code"]
    placeholder = config["placeholder"]["code"]

    for line in cell["source"]:
        # beginning of a solution block
        if solution_marker in line:
            if not in_solution:  # Nouveau bloc
                stats["code_blocks"] += 1
                in_solution = True
                expanded_line = line.expandtabs(4)
                indent = len(expanded_line) - len(expanded_line.lstrip(" "))
                new_source.append(" " * indent + placeholder + "\n")
            continue  # ignore all solution lines
        
        # end of solution block
        if in_solution:
            in_solution = False
        
        new_source.append(line)

    cell["source"] = new_source
    
    # Clear cell outputs and execution count
    cell["outputs"] = []
    cell["execution_count"] = None
    return cell, stats


def process_notebook(input_path, config):
    """Convert a notebook to student version in-place"""

    input_path = Path(input_path).resolve()
    
    try:
        display_path = input_path.relative_to(Path.cwd())
    except ValueError:
        display_path = input_path

    with open(input_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)
    
    stats = {"questions": 0, "code_blocks": 0, "remarks": 0}
    attached_files = notebook.get("metadata", {}).get("attached_files", [])

    # Process cells
    processed_cells = []
    for cell in notebook["cells"]:
        if cell["cell_type"] == "markdown":
            processed_cell, cell_stats = process_markdown_cell(cell, config)
        elif cell["cell_type"] == "code":
            processed_cell, cell_stats = process_code_cell(cell, config)
        else:
            processed_cell, cell_stats = cell, {}
            
        if processed_cell:
            processed_cells.append(processed_cell)
            for k in stats: stats[k] += cell_stats.get(k, 0)

    # Save student version next to original
    notebook["cells"] = processed_cells
    input_path = Path(input_path)
    
    # Generate student filename based on tutor_postfix presence
    stem = input_path.stem
    tutor_postfix = config["tutor_postfix"]
    student_postfix = config["student_postfix"]

    if stem.endswith(tutor_postfix):
        # Replace tutor_postfix with student_postfix at the end
        student_stem = stem[: -len(tutor_postfix)] + student_postfix
    else:
        # Just append student_postfix
        student_stem = stem + student_postfix

    student_filename = f"{student_stem}{input_path.suffix}"
    output_path = input_path.with_name(student_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    # Create ZIP in subdirectory
    zip_path = None
    if config["generate_zip"]:
            zip_dir = input_path.parent / "ZIP"
            zip_dir.mkdir(parents=True, exist_ok=True)
            zip_path = zip_dir / f"{input_path.stem}.zip"
            
            with zipfile.ZipFile(zip_path, "w") as zipf:
                zipf.write(output_path, arcname=student_filename)
                for fname in attached_files:
                    if os.path.isabs(fname):
                        raise ValueError(f"Absolute path forbidden in embedded files: {fname}")
                    
                    file_path = input_path.parent / fname
                    if not file_path.exists():
                        raise FileNotFoundError(f"Missing embedded file: {file_path}")
                    
                    zipf.write(file_path, arcname=fname)

    return {
        "display_path": str(display_path),
        "stats": stats,
        "zip": str(zip_path) if zip_path else None
    }
    
if __name__ == '__main__':
    """Main entry point for notebook conversion"""
    parser = argparse.ArgumentParser(description="Convert Jupyter notebooks to student versions")
    parser.add_argument("inputs", nargs="+", help="Input notebook path(s)")
    parser.add_argument("--config", default="conversion.json", help="Configuration file path")
    parser.add_argument("--hide-header", action="store_true", 
                        help="Suppress summary header in output")
    args = parser.parse_args()

    config = load_config(args.config)
    results = []

    # Print header if needed
    if not args.hide_header:
        print("## Processing Report")
        print("| Notebook | Questions | Code Blocks |  ZIP |")
        print("|----------|-----------|-------------|------|")

    # Process all input notebooks
    for input_path in args.inputs:
        result = process_notebook(input_path, config)
        results.append(result)
        
        # Print results line to stdout
        print(f"| `{Path(result["display_path"])}` | {result["stats"]["questions"]} | "
              f"{result["stats"]["code_blocks"]} | "
              f"{"✅" if result["zip"] else "❌"} |")
