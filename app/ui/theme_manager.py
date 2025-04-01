from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSettings
import os
import re

class ThemeManager:
    """Manager for application theming."""
    
    # Store the current theme and processed stylesheet for quick access
    current_theme = "Dark"  # Default
    _current_stylesheet = ""
    
    @staticmethod
    def apply_theme(theme=None):
        """Apply the specified theme or load from settings."""
        settings = QSettings("LiDoMa", "DockerManager")
        
        # If no theme specified, load from settings
        if theme is None:
            theme = settings.value("theme", "Dark")
        
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Load appropriate stylesheet
        if theme == "Dark":
            style_path = os.path.join(base_dir, "app", "ui", "style.qss")
        elif theme == "Light":
            style_path = os.path.join(base_dir, "app", "ui", "style_light.qss")
        else:  # System - future implementation
            style_path = os.path.join(base_dir, "app", "ui", "style.qss")  # Default to dark for now
        
        # Apply stylesheet if file exists
        if os.path.exists(style_path):
            with open(style_path, "r") as file:
                style = file.read()
                
                # Process imports and variables
                style = ThemeManager._process_imports(style, os.path.dirname(style_path))
                
                # Process CSS variables as Qt's QSS doesn't support var()
                style = ThemeManager._process_css_variables(style)
                
                # Store the processed stylesheet
                ThemeManager._current_stylesheet = style
                
                # Apply the processed stylesheet to the application
                app = QApplication.instance()
                if app:
                    # Clear existing stylesheet first to ensure changes are applied
                    app.setStyleSheet("")
                    app.setStyleSheet(style)
                
                # Store the current theme in memory for other components to access
                ThemeManager.current_theme = theme
                
                # Debug print for troubleshooting
                print(f"Applied theme: {theme}")
                
                return True
        return False
    
    @staticmethod
    def refresh_widget_style(widget):
        """Reapply the current theme to a specific widget and its children."""
        if ThemeManager._current_stylesheet:
            # This forces the widget to reapply the stylesheet
            widget.setStyleSheet("")
            widget.setStyleSheet(ThemeManager._current_stylesheet)
    
    @staticmethod
    def get_current_theme():
        """Return the currently active theme name."""
        return ThemeManager.current_theme
    
    @staticmethod
    def _process_imports(css_content, base_path):
        """Process @import statements in the CSS content."""
        # Find all import statements
        import_pattern = r'@import\s+url\(["\'](.+?)["\']\);'
        matches = re.findall(import_pattern, css_content)
        
        # Process each import
        for import_file in matches:
            import_path = os.path.join(base_path, import_file)
            if os.path.exists(import_path):
                with open(import_path, 'r') as f:
                    import_content = f.read()
                    # Replace the import statement with the file content
                    css_content = css_content.replace(f'@import url("{import_file}");', import_content)
                    css_content = css_content.replace(f"@import url('{import_file}');", import_content)
        
        return css_content
    
    @staticmethod
    def _process_css_variables(css_content):
        """Process CSS variables and replace var() calls with actual values."""
        # First, extract all variable definitions
        variables = {}
        var_pattern = r'--([a-zA-Z0-9_-]+):\s*([^;]+);'
        for match in re.finditer(var_pattern, css_content):
            var_name = match.group(1)
            var_value = match.group(2).strip()
            variables[var_name] = var_value
        
        # Then replace all var() references with their values
        var_usage_pattern = r'var\(--([a-zA-Z0-9_-]+)\)'
        matches = re.findall(var_usage_pattern, css_content)
        
        # Process each variable usage
        for var_name in matches:
            if var_name in variables:
                # Replace the var() call with the actual value
                css_content = css_content.replace(f'var(--{var_name})', variables[var_name])
        
        # Remove variable definitions as they're not needed after processing
        css_content = re.sub(r'\/\*.*?\*\/\s*', '', css_content, flags=re.DOTALL)  # Remove comments
        css_content = re.sub(r'--[a-zA-Z0-9_-]+:\s*[^;]+;', '', css_content)  # Remove variable definitions
        
        return css_content
