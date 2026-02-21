import matplotlib
matplotlib.use('Agg') # Force non-GUI backend
import matplotlib.pyplot as plt
import os
from pathlib import Path

def generate_latex_img(latex_code: str, output_path: str, inline: bool = False):
    """
    Generates a PNG image from LaTeX code using Matplotlib's mathtext.
    
    Args:
        latex_code: The LaTeX string (without $ if they are added here).
        output_path: Path to save the PNG file.
        inline: If True, renders as inline math instead of displaystyle.
    """
    # Configure for high quality (300 DPI for Gmail-skärpa)
    # Enable full LaTeX support for complex environments like pmatrix
    plt.rc('text', usetex=True) 
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}')
    plt.rc('font', family='serif')
    
    # Create figure with a small size, will be tight-boxed later
    # We use a white background for the figure to help with light theme, 
    # but keep the savefig transparent.
    fig = plt.figure(figsize=(0.1, 0.1))
    
    # Handle delimiters smartly:
    # If the AI uses a block environment, don't wrap it in $...$
    if any(env in latex_code for env in [r"\begin{align", r"\begin{equation", r"\begin{gather", r"\begin{pmatrix"]):
        full_latex = latex_code
    else:
        if inline:
            full_latex = f"${latex_code}$"
        else:
            # Use displaystyle for full size sums/integrals even in simple lines
            full_latex = f"$\\displaystyle {latex_code}$"
    
    # Render text. Using a larger fontsize helps with DPI clarity
    plt.text(0, 0, full_latex, fontsize=14, color='black')
    plt.axis('off')
    
    # Save the result with high DPI and transparent background
    # We use bbox_inches='tight' to crop the image to the formula only
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.05, dpi=150, transparent=True)
    plt.close(fig)

if __name__ == "__main__":
    # Test
    test_code = r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}"
    generate_latex_img(test_code, "test_equation.png")
    print("Test image generated: test_equation.png")
