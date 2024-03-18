from PyQt5.QtGui import QFontDatabase, QFont


def load_application_fonts(app):
    """Loads the custom application fonts."""
    fontId = QFontDatabase.addApplicationFont("assets/fonts/Roboto-Light.ttf")
    fontFamilies = QFontDatabase.applicationFontFamilies(fontId)
    if fontFamilies:
        app.setFont(QFont(fontFamilies[0], 10))