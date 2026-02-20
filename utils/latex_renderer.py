import matplotlib.pyplot as plt
import os
from pathlib import Path

def generate_latex_img(latex_code: str, output_path: str):
    """
    Generates a PNG image from LaTeX code using Matplotlib's mathtext.
    
    Args:
        latex_code: The LaTeX string (without $ if they are added here).
        output_path: Path to save the PNG file.
    """
    # Configure for high quality (300 DPI for Gmail-skärpa)
    # Ensure fonts are consistent
    plt.rc('text', usetex=False) # Use Matplotlib's internal mathtext
    
    # Create figure with a small size, will be tight-boxed later
    fig = plt.figure(figsize=(0.1, 0.1))
    
    # We add $ around the code if it's missing for mathtext
    full_latex = f"${latex_code}$"
    
    # Render text. Using a larger fontsize helps with DPI clarity
    plt.text(0, 0, full_latex, fontsize=20, color='black')
    plt.axis('off')
    
    # Save with tight bounding box to eliminate whitespace
    # Transparent background for better dark/light mode compatibility
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.05, dpi=300, transparent=True)
    plt.close(fig)

if __name__ == "__main__":
    # Test
    test_code = r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}"
    generate_latex_img(test_code, "test_equation.png")
    print("Test image generated: test_equation.png")
