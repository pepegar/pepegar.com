#!/usr/bin/env python3

import re
import subprocess
import sys
import tempfile
import os
import shlex
import logging
import argparse
from colorama import init, Fore, Style
from pathlib import Path
import difflib

# Initialize colorama for cross-platform colored output
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def log_info(message, emoji='ℹ️ '):
    logger.info(f"{Fore.CYAN}{emoji} {message}{Style.RESET_ALL}")

def log_success(message, emoji='✅ '):
    logger.info(f"{Fore.GREEN}{emoji} {message}{Style.RESET_ALL}")

def log_warning(message, emoji='⚠️ '):
    logger.warning(f"{Fore.YELLOW}{emoji} {message}{Style.RESET_ALL}")

def log_error(message, emoji='❌ '):
    logger.error(f"{Fore.RED}{emoji} {message}{Style.RESET_ALL}")

def execute_code(code, command, filename=None):
    log_info(f"Executing code block: {command}", emoji='🚀')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        if filename:
            temp_file.write(f"# Filename: {filename}\n")
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        cmd_parts = shlex.split(command)
        cmd_parts.append(temp_file_path)
        result = subprocess.run(cmd_parts, check=True, capture_output=True, text=True)
        output = result.stdout.strip()
        return_code = result.returncode
        log_success(f"Code execution successful (return code: {return_code})")
    except subprocess.CalledProcessError as e:
        output = e.stderr.strip()
        return_code = e.returncode
        log_error(f"Code execution failed (return code: {return_code})")
    finally:
        os.unlink(temp_file_path)
        log_info("Temporary file cleaned up", emoji='🧹')

    return output, return_code

def format_terminal_output(command, output, return_code, filename=None):
    formatted_output = f"$ {command}"
    if filename:
        formatted_output += f" {filename}"
    formatted_output += f"\n{output}\n"
    if return_code != 0:
        formatted_output += f"\n[Process completed with exit code {return_code}]"
    return formatted_output

def process_markdown(input_file, output_file, check_mode=False):
    log_info(f"Processing Markdown file: {input_file}", emoji='📄')
    with open(input_file, 'r') as f:
        content = f.read()

    pattern = r'```(\w+)?\s*(!.+?)(?:\s+(\S+))?\n(.*?)```'
    code_blocks_count = len(re.findall(pattern, content, flags=re.DOTALL))
    log_info(f"Found {code_blocks_count} code blocks to process", emoji='🔍')

    def replace_code_block(match):
        language = match.group(1) or ''
        annotation = match.group(2)
        filename = match.group(3)
        code = match.group(4).strip()

        if annotation and annotation.startswith('!'):
            command = annotation[1:].strip()
            log_info(f"Processing code block: {command} {filename or ''}", emoji='⚙️ ')
            output, return_code = execute_code(code, command, filename)
            formatted_result = format_terminal_output(command, output, return_code, filename)
            log_success("Code block processed successfully")
            
            result_html = f'''
<details>
  <summary><strong>Execution Result</strong></summary>

```
{formatted_result}
```

</details>
'''
            return f"```{language}\n{code}\n```\n\n{result_html}"
        else:
            log_warning("Skipping unannotated code block")
            return match.group(0)

    processed_content = re.sub(pattern, replace_code_block, content, flags=re.DOTALL)
    
    if check_mode:
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                existing_content = f.read()
            if processed_content != existing_content:
                log_warning(f"File {output_file} would be modified", emoji='🔄')
                
                # Generate diff
                diff = difflib.unified_diff(
                    existing_content.splitlines(keepends=True),
                    processed_content.splitlines(keepends=True),
                    fromfile=str(output_file),
                    tofile=str(output_file) + " (after processing)",
                    n=3  # Context lines
                )
                
                # Print colorized diff
                for line in diff:
                    if line.startswith('+'):
                        print(Fore.GREEN + line.rstrip() + Style.RESET_ALL)
                    elif line.startswith('-'):
                        print(Fore.RED + line.rstrip() + Style.RESET_ALL)
                    elif line.startswith('^'):
                        print(Fore.BLUE + line.rstrip() + Style.RESET_ALL)
                    else:
                        print(line.rstrip())
                
                return True
            else:
                log_success(f"File {output_file} is up to date", emoji='👍')
                return False
        else:
            log_warning(f"Output file {output_file} does not exist and would be created", emoji='🆕')
            return True
    else:
        with open(output_file, 'w') as f:
            f.write(processed_content)
        log_success(f"Processed content saved to: {output_file}", emoji='💾')
        return False

def process_all_markdown_files(directory='.', check_mode=False):
    log_info(f"Searching for .md.in files in {directory}", emoji='🔎')
    would_modify = False
    for md_in_file in Path(directory).rglob('*.md.in'):
        output_file = md_in_file.with_name(md_in_file.stem)  # Remove .in from the filename
        if process_markdown(md_in_file, output_file, check_mode=check_mode):
            would_modify = True
    return would_modify

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Markdown files with executable code blocks.")
    parser.add_argument('directory', nargs='?', default='.', help="Directory to process (default: current directory)")
    parser.add_argument('--check', action='store_true', help="Check if files would be modified without making changes")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Assuming scripts/ is directly under project root
    os.chdir(project_root)  # Change to project root directory

    log_info(f"Starting Markdown preprocessing in {args.directory}", emoji='🎬')
    would_modify = process_all_markdown_files(args.directory, check_mode=args.check)
    
    if args.check:
        if would_modify:
            log_warning("Some files would be modified. Please run the preprocessor without --check.", emoji='⚠️')
            sys.exit(1)
        else:
            log_success("All files are up to date.", emoji='🎉')
            sys.exit(0)
    else:
        log_success("Preprocessing completed successfully!", emoji='🎉')
