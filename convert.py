import nbformat
import os
import re
from copy import deepcopy

def has_no_output_comment(source):
    """Check if a code cell has the 'NO OUTPUT' comment."""
    lines = source.strip().split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') and 'NO OUTPUT' in stripped.upper():
            return True
    return False

def detect_and_adjust_matplotlib_code(code):
    """
    Detect matplotlib subplot configurations and adjust figure size and DPI for Voila display.
    """
    # Check if this cell contains matplotlib plotting
    if not ('plt.subplots' in code or 'fig, ax = plt.subplots' in code or 'pyplot.subplots' in code):
        return code
    
    # Extract subplot configuration
    subplot_match = re.search(r'plt\.subplots\s*\(\s*(\d+)\s*,\s*(\d+)', code)
    if not subplot_match:
        # Try alternative pattern
        subplot_match = re.search(r'subplots\s*\(\s*(\d+)\s*,\s*(\d+)', code)
    
    if subplot_match:
        rows = int(subplot_match.group(1))
        cols = int(subplot_match.group(2))
        total_subplots = rows * cols
        
        # Calculate optimal figure size based on number of subplots and viewport
        # Reduced sizes by 10-15% for better viewport fitting
        if total_subplots <= 2:
            # Single row or column - use moderate width
            figsize = '[8.5, 3.5]' if cols > rows else '[5, 7]'
            dpi = '120'
        elif total_subplots == 4:
            # 2x2 grid - optimize for 4 subplots (reduced from [12, 8] to [10, 7])
            if rows == 2 and cols == 2:
                figsize = '[10, 7]'  # 15% reduction in width, 12% in height
                dpi = '100'  # Lower DPI for better fitting
            else:
                figsize = '[12, 5]' if cols > rows else '[7, 8.5]'
                dpi = '120'
        elif total_subplots <= 6:
            # Medium complexity (reduced from [15, 8] and [10, 12])
            figsize = '[13, 7]' if cols > rows else '[8.5, 10]'
            dpi = '100'
        else:
            # Many subplots - use larger figure with lower DPI (reduced from [16, 10])
            figsize = '[14, 8.5]'
            dpi = '80'
        
        # Replace figsize parameter
        code = re.sub(r'figsize\s*=\s*\[[^\]]+\]', f'figsize={figsize}', code)
        
        # Replace or add DPI parameter
        if 'dpi=' in code:
            code = re.sub(r'dpi\s*=\s*\d+', f'dpi={dpi}', code)
        else:
            # Add DPI parameter after figsize
            code = re.sub(r'(figsize\s*=\s*\[[^\]]+\])', rf'\1, dpi={dpi}', code)
    
    # Also adjust any standalone figure size definitions
    else:
        # Look for figsize definitions without subplots
        if 'figsize' in code:
            # Apply conservative sizing for single plots (reduced from [10, 6])
            code = re.sub(r'figsize\s*=\s*\[[^\]]+\]', 'figsize=[8.5, 5]', code)
            if 'dpi=' in code:
                code = re.sub(r'dpi\s*=\s*\d+', 'dpi=120', code)
    
    return code

def convert_notebook_to_voila(input_notebook, output_notebook, css_path=None):
    """
    Transform a standard Jupyter notebook into a polished Voila presentation.
    
    This function converts a regular notebook into one with beautiful HTML styling,
    proper MathJax support, and optimized widget layouts for web presentation.
    
    Args:
        input_notebook (str): Path to the source Jupyter notebook
        output_notebook (str): Destination path for the styled notebook
        css_path (str, optional): Custom CSS file to override default styling
    """
    # Read the original notebook structure
    with open(input_notebook, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Initialize a fresh notebook with preserved metadata
    new_nb = nbformat.v4.new_notebook()
    new_nb.metadata = nb.metadata.copy()
    # Mark notebook as trusted to prevent security warnings in Voila
    new_nb.metadata['trusted'] = True
    
    # Create the foundation cell with MathJax configuration and styling
    # This hidden cell sets up the mathematical typesetting and visual appearance
    styling_cell = nbformat.v4.new_code_cell(source="""
# This cell configures the notebook's appearance and mathematical rendering
from IPython.display import display, HTML

# Configure MathJax for proper LaTeX rendering and apply custom styling
display(HTML(\"\"\"
<!-- MathJax configuration for proper equation rendering -->
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  tex2jax: {
    inlineMath: [['$','$'], ['\\(','\\)']],
    displayMath: [['$$','$$'], ['\\[','\\]']],
    processEscapes: true,
    processEnvironments: true,
    skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'span', '.references'],
    ignoreClass: "references notmath"
  },
  TeX: {
    equationNumbers: { autoNumber: "none" },  // Clean look without equation numbers
    extensions: ["AMSmath.js", "AMSsymbols.js"]
  },
  CommonHTML: {
    linebreaks: { automatic: true }  // Responsive equation breaking
  }
});
</script>

<!-- Load MathJax from CDN for mathematical typesetting -->
<script src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_HTML"></script>

<style>
""" + (load_css(css_path) if css_path else DEFAULT_CSS) + """
</style>
\"\"\"))
""")
    styling_cell.metadata.tags = ["hide-input"]
    new_nb.cells.append(styling_cell)
    
    # Extract the main title from the first markdown heading
    # This will become our prominent page header
    title = "Jupyter Notebook"
    title_cell_index = None
    
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "markdown" and cell.source.startswith("# "):
            lines = cell.source.splitlines()
            title = lines[0].strip("# ")
            title_cell_index = i
            break
    
    # Create a styled title section at the top of the presentation
    title_cell = nbformat.v4.new_code_cell(source=f"""
# Display the main title with professional styling
display(HTML(\"\"\"
<h1>{title}</h1>
\"\"\"))
""")
    title_cell.metadata.tags = ["hide-input"]
    new_nb.cells.append(title_cell)
    
    # Process each cell from the original notebook
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "markdown":
            # Handle the title cell specially to avoid duplication
            if i == title_cell_index:
                lines = cell.source.splitlines()
                if len(lines) > 1:  # Check if there's content beyond the title
                    # Extract everything after the main title
                    remaining_content = '\n'.join(lines[1:])
                    
                    # Look for secondary headings to organize content properly
                    secondary_headings = re.findall(r'^##\s+.+$', remaining_content, re.MULTILINE)
                    
                    if secondary_headings:
                        # Split content at the first secondary heading
                        parts = re.split(r'^(##\s+.+$)', remaining_content, 1, re.MULTILINE)
                        
                        # The introduction is everything before the first subheading
                        intro_content = parts[0].strip()
                        
                        # Add introduction content with special styling
                        if intro_content:
                            new_cell = nbformat.v4.new_code_cell(source=f"""
# Display introduction content with distinctive styling
display(HTML(\"\"\"
<div class="intro-content">
{convert_markdown_to_html(intro_content)}
</div>
\"\"\"))
""")
                            new_cell.metadata.tags = ["hide-input"]
                            new_nb.cells.append(new_cell)
                        
                        # Add the remaining content as a regular section
                        rest_content = parts[1] + (parts[2] if len(parts) > 2 else "")
                        if rest_content.strip():
                            new_cell = nbformat.v4.new_code_cell(source=f"""
# Display remaining content from title cell
display(HTML(\"\"\"
<div class="section">
{convert_markdown_to_html(rest_content)}
</div>
\"\"\"))
""")
                            new_cell.metadata.tags = ["hide-input"]
                            new_nb.cells.append(new_cell)
                    else:
                        # No subheadings found - treat all as introduction
                        if remaining_content.strip():
                            new_cell = nbformat.v4.new_code_cell(source=f"""
# Display introduction content
display(HTML(\"\"\"
<div class="intro-content">
{convert_markdown_to_html(remaining_content)}
</div>
\"\"\"))
""")
                            new_cell.metadata.tags = ["hide-input"]
                            new_nb.cells.append(new_cell)
            else:
                # Convert regular markdown cells to styled HTML sections
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Convert markdown content to styled HTML
display(HTML(\"\"\"
<div class="section">
{convert_markdown_to_html(cell.source)}
</div>
\"\"\"))
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
            
        elif cell.cell_type == "code":
            # Process different types of code cells appropriately
            
            # Check for NO OUTPUT comment first
            if has_no_output_comment(cell.source):
                # Execute code but completely suppress all output
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Execute code without displaying output (NO OUTPUT comment detected)
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Create null output streams to completely suppress output
null_stdout = io.StringIO()
null_stderr = io.StringIO()

# Execute code with all output redirected to null
with redirect_stdout(null_stdout), redirect_stderr(null_stderr):
{indent_code(cell.source)}
    
# Clear the null streams to free memory
null_stdout.close()
null_stderr.close()
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
                
            elif contains_status_display(cell.source):
                # Preserve cells that display colored status messages
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Execute cell with status display output
{cell.source}
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
                
            elif is_import_or_setup_cell(cell.source):
                # Hide import statements and setup code from the presentation
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Execute setup/import code (hidden from presentation)
{cell.source}
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
                
            elif contains_interactive_plot(cell.source):
                # Special handling for interactive widgets and plots
                # Add descriptive headers based on the widget type
                if 'ThermalWidget' in cell.source:
                    header_html = """
<div class="widget-area">
    <h3>Interactive Thermal Homogenization Explorer</h3>
    <p>Use the controls below to explore thermal properties of heterogeneous materials in real-time:</p>
    <ul>
        <li><strong>Microstructure ID:</strong> Select from 30,000 different microstructure samples</li>
        <li><strong>Inclusion Conductivity:</strong> Change the thermal conductivity of the inclusion material</li>
        <li><strong>Loading Angle:</strong> Adjust the direction of the applied temperature gradient</li>
    </ul>
    <p><em>Note</em>: If the widget is not displayed, try executing the cell again</p>
</div>
"""
                elif any(widget in cell.source for widget in ['FloatSlider', 'IntSlider', 'interact']):
                    header_html = """
<div class="widget-area">
    <h3>Interactive Plot</h3>
    <p>Use the controls below to adjust the visualization:</p>
</div>
"""
                else:
                    # Generic interactive content header
                    header_html = """
<div class="widget-area">
    <h3>Interactive Content</h3>
    <p>Interactive elements are displayed below:</p>
</div>
"""
                
                # Preserve the interactive functionality with added context
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Display interactive widget with descriptive header
from IPython.display import display, HTML

# Add informative header for the interactive content
display(HTML(\"\"\"{header_html}\"\"\"))

# Execute the original interactive code
{cell.source}
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
            else:
                # Handle regular code cells by capturing and styling their output
                # Check if this is a matplotlib plotting cell and adjust if needed
                adjusted_code = detect_and_adjust_matplotlib_code(cell.source)
                
                new_cell = nbformat.v4.new_code_cell(source=f"""
# Execute code and display output in styled container
from IPython.display import display, HTML

# Capture output from the original code execution
_original_output = None
try:
    import io
    import sys
    _stdout_capture = io.StringIO()
    _original_stdout = sys.stdout
    sys.stdout = _stdout_capture
    
    # Run the original code (with matplotlib adjustments if applicable)
{indent_code(adjusted_code)}
    
    # Restore stdout and capture what was printed
    sys.stdout = _original_stdout
    _original_output = _stdout_capture.getvalue()
except Exception as e:
    import traceback
    _original_output = f"Error: {{str(e)}}\\n{{traceback.format_exc()}}"
finally:
    # Display any output in a nicely styled container
    if _original_output and _original_output.strip():
        display(HTML(f\"\"\"
        <div style="background: #e6f7ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
            <pre style="margin: 0; background: transparent; white-space: pre-wrap; font-family: 'Consolas', 'Monaco', monospace;">{{_original_output}}</pre>
        </div>
        \"\"\"))
""")
                new_cell.metadata.tags = ["hide-input"]
                new_nb.cells.append(new_cell)
    
    # Add a professional footer to complete the presentation
    footer_cell = nbformat.v4.new_code_cell(source="""
# Add footer with attribution
display(HTML(\"\"\"
<div class="footer">
    <p>&copy; 2025 | Created with <a href="https://github.com/voila-dashboards/voila" target="_blank">Voila</a></p>
</div>
\"\"\"))
""")
    footer_cell.metadata.tags = ["hide-input"]
    new_nb.cells.append(footer_cell)
    
    # Save the transformed notebook
    with open(output_notebook, 'w', encoding='utf-8') as f:
        nbformat.write(new_nb, f)
    
    print(f"Conversion complete: {input_notebook} → {output_notebook}")
    print(f"Run with: voila {output_notebook} --template=material --theme=light")

def convert_markdown_to_html(markdown_text):
    """
    Convert markdown text to HTML while preserving LaTeX mathematical expressions.
    
    This function carefully handles mathematical notation, citations, and references
    to ensure proper rendering in the final presentation.
    """
    # Use unique placeholders to protect math expressions during conversion
    placeholder_format = "MATH_PLACEHOLDER_{}_TYPE_{}"
    math_blocks = []
    has_math = False  # Track whether this content contains mathematical expressions
    
    # Check for a References section and handle it separately
    references_section = None
    references_match = re.search(r'^(#+)\s+References:?.*$', markdown_text, re.MULTILINE | re.IGNORECASE)
    
    if references_match:
        # Split content at the References heading
        parts = re.split(r'^(#+\s+References:?.*$)', markdown_text, 1, re.MULTILINE | re.IGNORECASE)
        
        # Process main content normally, handle references specially
        markdown_text = parts[0]
        references_section = parts[1] + (parts[2] if len(parts) > 2 else "")
    
    # Extract align environments first - these need special handling for numbering
    def extract_align_env(match):
        nonlocal math_blocks, has_math
        has_math = True
        block_id = len(math_blocks)
        # Convert align to align* to prevent automatic equation numbering
        content = match.group(0)
        content = content.replace('\\begin{align}', '\\begin{align*}')
        content = content.replace('\\end{align}', '\\end{align*}')
        math_blocks.append(("align", content))
        return placeholder_format.format(block_id, "align")
    
    # Find and extract all align environments
    pattern = r'\\begin\{align\}(.*?)\\end\{align\}'
    markdown_text = re.sub(pattern, extract_align_env, markdown_text, flags=re.DOTALL)
    
    # Extract other LaTeX environments (cases, matrices, etc.)
    def extract_other_env(match):
        nonlocal math_blocks, has_math
        has_math = True
        block_id = len(math_blocks)
        math_blocks.append(("env", match.group(0)))
        return placeholder_format.format(block_id, "env")
    
    # Find and extract all other LaTeX environments
    pattern = r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}'
    markdown_text = re.sub(pattern, extract_other_env, markdown_text, flags=re.DOTALL)
    
    # Extract display math ($$...$$) blocks
    def extract_display_math(match):
        nonlocal math_blocks, has_math
        has_math = True
        block_id = len(math_blocks)
        math_blocks.append(("display", match.group(1)))
        return placeholder_format.format(block_id, "display")
    
    markdown_text = re.sub(r'\$\$(.*?)\$\$', extract_display_math, markdown_text, flags=re.DOTALL)
    
    # Extract inline math ($...$) expressions
    def extract_inline_math(match):
        nonlocal math_blocks, has_math
        has_math = True
        block_id = len(math_blocks)
        math_blocks.append(("inline", match.group(1)))
        return placeholder_format.format(block_id, "inline")
    
    markdown_text = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', extract_inline_math, markdown_text)
    
    # Protect parentheses content from MathJax interpretation (AFTER math extraction)
    markdown_text = re.sub(r'\(([^)]*)\)', r'<span class="notmath">(\1)</span>', markdown_text)
    
    # Convert regular markdown elements to HTML
    markdown_text = process_regular_markdown(markdown_text)
    
    # Protect citation references from being processed as math
    def escape_citation(match):
        # Wrap in span with class to prevent MathJax processing
        return f'<span class="notmath">[{match.group(1)}]</span>'

    # Find numerical citation patterns like [1], [2], etc.
    citation_pattern = r'\[(\d+)\]'
    markdown_text = re.sub(citation_pattern, escape_citation, markdown_text)
    
    # Process references section with special formatting
    if references_section:
        # Handle basic markdown formatting
        processed_references = references_section
        
        # Convert headings to HTML
        processed_references = re.sub(r'^# (.+)$', r'<h1>\1</h1>', processed_references, flags=re.MULTILINE)
        processed_references = re.sub(r'^## (.+)$', r'<h2>\1</h2>', processed_references, flags=re.MULTILINE)
        processed_references = re.sub(r'^### (.+)$', r'<h3>\1</h3>', processed_references, flags=re.MULTILINE)
        
        # Format numerical citations with special styling
        processed_references = re.sub(r'\[(\d+)\]', r'<span class="citation-number"><span class="bracket-content">[<em><strong>\1</strong></em>]</span></span>', processed_references)
        
        # Format bracketed descriptive text (like [Computer software])
        processed_references = re.sub(r'\[([^\]0-9][^\]]*)\]', r'<span class="bracket-content">[<em>\1</em>]</span>', processed_references)
        
        # Protect parentheses in references section too
        processed_references = re.sub(r'\(([^)]*)\)', r'&#40;\1&#41;', processed_references)
        
        # Clean up any escaped HTML characters
        processed_references = processed_references.replace('\\<', '<').replace('\\>', '>').replace('\\/', '/')
        
        # Convert URLs to clickable links
        processed_references = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', processed_references)
        
        # Wrap text in paragraphs while preserving headings
        paragraphs = []
        for p in processed_references.split('\n\n'):
            if p.strip() and not p.strip().startswith('<h'):
                paragraphs.append(f'<p>{p}</p>')
            else:
                paragraphs.append(p)
        
        processed_references = '\n'.join(paragraphs)
        
        # Wrap references in a special container with MathJax exclusion
        processed_references = f'''<div class="references" data-mathjax="ignore">
    <style>
        /* Prevent MathJax from interfering with reference formatting */
        .references .citation-number strong {{ font-weight: bold; font-style: normal; }}
        .references .bracket-content em {{ font-style: italic; font-weight: normal; }}
        .references p {{ font-weight: normal; }}
        .references span {{ font-weight: normal; }}
        .references {{ font-weight: normal; }}
    </style>
    {processed_references}
</div>'''
        
        # Combine main content with processed references
        markdown_text += processed_references
        
    # Restore all mathematical expressions to their proper LaTeX format
    for i, (block_type, content) in enumerate(math_blocks):
        # Escape backslashes for proper JavaScript string handling
        escaped_content = content.replace('\\', '\\\\')
        
        if block_type == "align":
            # Wrap align environments in display math delimiters
            replacement = f"$${escaped_content}$$"
        elif block_type == "env":
            # Wrap other environments in display math delimiters
            replacement = f"$${escaped_content}$$"
        elif block_type == "display":
            # Wrap display math content
            replacement = f"$${escaped_content}$$"
        else:  # inline
            # Wrap inline math content
            replacement = f"${escaped_content}$"
        
        placeholder = placeholder_format.format(i, block_type)
        markdown_text = markdown_text.replace(placeholder, replacement)
    
    # Add MathJax reprocessing script only if math content is present
    if has_math:
        markdown_text += """
<script>
if (window.MathJax) {
    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
}
</script>
"""
    
    return markdown_text

def process_regular_markdown(text):
    """Convert standard markdown elements to HTML without affecting LaTeX content."""
    # Convert markdown headings to HTML
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    
    # Process bullet lists with proper HTML structure
    lines = text.split('\n')
    in_list = False
    in_blockquote = False
    result = []
    
    for i, line in enumerate(lines):
        # Handle blockquotes
        if line.strip().startswith('>'):
            if not in_blockquote:
                result.append('<blockquote>')
                in_blockquote = True
            # Remove markdown blockquote characters and trim whitespace
            result.append(line.strip().lstrip('>').strip())
            continue
        else:
            if in_blockquote:
                result.append('</blockquote>')
                in_blockquote = False

        # Handle lists
        is_list_item = line.strip().startswith('- ')
        if is_list_item:
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    if in_blockquote:
        result.append('</blockquote>')
    
    text = '\n'.join(result)
    
    # Convert text formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)  
    # Italics: only match *…* when it's not immediately inside a literal ()
    text = re.sub(r'(?<!\()\*(.+?)\*(?!\))', r'<em>\1</em>', text)
    
    # Convert markdown links to HTML
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    
    # Wrap text blocks in paragraph tags
    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs):
        trimmed_p = p.strip()
        if trimmed_p and not trimmed_p.startswith('<') and not trimmed_p.endswith('>'):
            paragraphs[i] = f'<p>{trimmed_p}</p>'
    
    return '\n'.join(paragraphs)

def indent_code(code, spaces=4):
    """Add consistent indentation to code blocks for proper formatting."""
    prefix = ' ' * spaces
    return '\n'.join(prefix + line for line in code.split('\n'))

def contains_status_display(code):
    """
    Check if a code cell contains status displays with colored backgrounds.
    
    These are typically used for showing process status or important messages
    and should be preserved as-is in the presentation.
    """
    # Look for display(HTML patterns with background color styling
    if re.search(r'display\s*\(\s*HTML\s*\(\s*[frf]?""".*background:\s*#', code, re.DOTALL):
        return True
    return False

def is_import_or_setup_cell(code):
    """
    Identify cells that contain import statements or setup code.
    
    These cells are necessary for functionality but don't need to be
    prominently displayed in the presentation.
    """
    # Check for import statements
    if re.search(r'^\s*import\s+|^\s*from\s+.*\s+import', code, re.MULTILINE):
        return True
    
    # Check for package installation commands
    if re.search(r'^\s*!pip\s+|^\s*!conda\s+', code, re.MULTILINE):
        return True
    
    # Check for matplotlib configuration
    if '%matplotlib' in code:
        return True
    
    return False

def contains_interactive_plot(code):
    """
    Detect cells that contain interactive widgets or plots.
    
    These cells need special handling to provide context and ensure
    proper rendering in the Voila presentation.
    """
    # Check for various interactive widget patterns
    if re.search(r'interact\s*\(', code, re.MULTILINE):
        return True
    if re.search(r'ipywidgets\.', code, re.MULTILINE):
        return True
    if re.search(r'FloatSlider|IntSlider|Dropdown|Button|Checkbox|SelectionSlider|Play|DatePicker', code, re.MULTILINE):
        return True
    if re.search(r'ThermalWidget', code, re.MULTILINE):
        return True
    if re.search(r'@interact|interactive', code, re.MULTILINE):
        return True
    if re.search(r'widgets\.|HBox|VBox|Tab|Accordion', code, re.MULTILINE):
        return True
    if '%matplotlib widget' in code:
        return True
    # Check for widget observation patterns (common in interactive applications)
    if re.search(r'\.observe\s*\(', code, re.MULTILINE):
        return True
    # Check for widget display patterns
    if re.search(r'display\s*\(\s*\w*Box\s*\(', code, re.MULTILINE):
        return True
    return False

def load_css(css_path):
    """Load custom CSS styling from an external file if provided."""
    if css_path and os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    return DEFAULT_CSS

# Default CSS styling that creates a professional, responsive presentation layout
DEFAULT_CSS = """
    /* Main container with full-width responsive design */
    body {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.5;
        max-width: 100%;  /* Utilize full viewport width */
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Professional header styling with visual hierarchy */
    h1 {
        color: #2c3e50;
        text-align: center;
        padding-bottom: 15px;
        border-bottom: 2px solid #3498db;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #3498db;
        margin-top: 30px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    
    h3 {
        color: #2980b9;
        margin-top: 25px;
        padding-bottom: 5px;
    }
    
    h4 {
        color: #34495e;
        margin-top: 20px;
        font-style: italic;
    }
    
    /* Content section containers with subtle styling */
    .section {
        margin: 30px 0;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 5px;
        border-left: 5px solid #3498db;
    }
    
    /* Enhanced list presentation */
    ul {
        margin: 15px 0;
        padding-left: 25px;
        list-style-type: disc; /* Clear bullet points for readability */
    }
    
    ol {
        margin: 15px 0;
        padding-left: 25px;
    }
    
    li {
        margin: 5px 0;
        padding-left: 5px; /* Proper spacing after bullets */
    }
    
    /* Elegant footer styling */
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        text-align: center;
        font-size: 0.9em;
        color: #7f8c8d;
    }
    
    /* Responsive matplotlib widget containers */
    .jupyter-widgets-output-area {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }

    .jupyter-matplotlib-figure {
        width: 100% !important;
        max-width: 100% !important;
    }

    .jupyter-matplotlib-canvas-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    canvas.jupyter-matplotlib-canvas {
        max-width: 100% !important;
        width: 100% !important;
        height: auto !important;
    }
    
    /* Force matplotlib figures to be responsive */
    .output_subarea img {
        max-width: 100% !important;
        height: auto !important;
    }
    
    /* Ensure plot containers don't overflow */
    .widget-output {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    
    /* Figure containers should be responsive */
    .figure {
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Prevent horizontal scrolling in plot areas */
    .output {
        overflow-x: hidden !important;
    }
    
    /* Specific styling for multi-subplot figures */
    .output_png {
        max-width: 100% !important;
        width: 100% !important;
        height: auto !important;
        display: block !important;
        margin: 0 auto !important;
    }
    
    /* Interactive widget area with distinctive styling */
    .widget-area {
        background: #f1f8ff;
        padding: 20px;
        border-radius: 5px;
        margin: 30px 0;
        border: 1px solid #d1e5f9;
    }
    
    .widget-area h3 {
        color: #2980b9;
        margin-top: 0;
        margin-bottom: 15px;
    }
    
    .widget-area ul {
        margin-bottom: 15px;
    }
    
    .widget-area em {
        color: #7f8c8d;
        font-size: 0.9em;
    }
    
    /* Enhanced widget styling for better presentation */
    .jupyter-widgets {
        margin: 20px 0;
    }
    
    /* Responsive widget containers */
    .widget-container {
        width: 100% !important;
        max-width: none !important;
    }
    
    /* Improved widget layout containers */
    .widget-hbox, .widget-vbox {
        width: 100% !important;
    }
    
    /* Introduction content styling for content after main title */
    .intro-content {
        margin: 0 0 30px 0;
        padding: 15px 20px;
        background: #f9fbfd;
        border-radius: 5px;
        line-height: 1.6;
        color: #2c3e50;
        border-left: 5px solid #34495e;
    }

    /* Widget alignment and layout consistency */
    .widget-hbox {
        display: flex !important;
        align-items: center !important;
        margin: 10px 0 !important;
    }
    
    .widget-vbox {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
    }
    
    /* Consistent widget label styling */
    .jupyter-widgets.widget-label {
        min-width: 150px !important;
        text-align: left !important;
        padding-right: 10px !important;
    }
    
    /* Standardized widget dimensions */
    .widget-slider {
        width: 400px !important;
    }
    
    .widget-text {
        width: 200px !important;
    }
    
    /* Consistent widget container margins and alignment */
    .widget-container {
        margin: 5px 0 !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Consistent description label width for alignment */
    .widget-label {
        min-width: 140px !important;
        max-width: 140px !important;
        text-align: left !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    /* Proper spacing between widget groups */
    .widget-area .jupyter-widgets {
        margin: 15px 0 !important;
    }
"""

if __name__ == "__main__":
    import sys
    
    # Validate command line arguments
    if len(sys.argv) < 3:
        print("Usage: python convert.py input.ipynb output.ipynb [style.css]")
        sys.exit(1)
    
    input_notebook = sys.argv[1]
    output_notebook = sys.argv[2]
    css_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Execute the conversion process
    convert_notebook_to_voila(input_notebook, output_notebook, css_path)