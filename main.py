import sys, os, shutil, datetime, functools
from send2trash import send2trash

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QScrollArea, QMessageBox, QMenu
)
from PySide6.QtGui import (
    QPixmap, QImage, QAction, QActionGroup, QShortcut, QKeySequence, QTransform
)
from PySide6.QtCore import Qt, QEvent, QSettings, QTimer, QUrl


from PIL import Image, ImageOps

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QScrollArea, QMessageBox, QMenu,
    QDockWidget, QTextEdit, QInputDialog
)

# ---- EXIF optional ----
try:
    import exifread
    EXIFREAD_AVAILABLE = True
except Exception:
    EXIFREAD_AVAILABLE = False

# ---- RAW optional ----
RAW_AVAILABLE = False
try:
    import rawpy
    import numpy as np
    RAW_AVAILABLE = True
except Exception:
    RAW_AVAILABLE = False  # App läuft trotzdem ohne RAW

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

# ===== App-Name =====
APP_NAME = "FixPeek"
RAW_EXTS = {".cr2", ".cr3", ".nef", ".nrw", ".arw", ".srf", ".sr2", ".orf", ".rw2", ".raf", ".dng", ".pef", ".srw"}

# ===== Sprachen / Translations =====
SUPPORTED_LANGS = ("de", "en", "es", "fr")
TR = {
    # ---- Menüs ----
    "menu_file":    {"de": "Datei", "en": "File", "es": "Archivo", "fr": "Fichier"},
    "menu_view":    {"de": "Ansicht", "en": "View", "es": "Ver", "fr": "Affichage"},
    "menu_options": {"de": "Optionen", "en": "Options", "es": "Opciones", "fr": "Options"},
    "menu_help":    {"de": "Hilfe", "en": "Help", "es": "Ayuda", "fr": "Aide"},
    "menu_sort":    {"de": "Sortieren", "en": "Sort", "es": "Ordenar", "fr": "Trier"},
    "menu_peek":    {"de": "Peek-Zoom", "en": "Peek Zoom", "es": "Zoom instantáneo", "fr": "Zoom instantané"},
    "menu_slideshow":{"de":"Slideshow", "en":"Slideshow", "es":"Diapositivas", "fr":"Diaporama"},
    "menu_x_action":{"de":"Aktion für Taste X", "en":"Action for key X", "es":"Acción para tecla X", "fr":"Action pour la touche X"},
    "menu_language": {"de":"Sprache / Language", "en":"Language", "es":"Idioma", "fr":"Langue"},

    # ---- Datei ----
    "act_open_file":   {"de":"Bild öffnen…", "en":"Open image…", "es":"Abrir imagen…", "fr":"Ouvrir une image…"},
    "act_open_folder": {"de":"Ordner öffnen…", "en":"Open folder…", "es":"Abrir carpeta…", "fr":"Ouvrir un dossier…"},
    "act_open_last":   {"de":"Zuletzt geöffneten Ordner öffnen", "en":"Open last folder", "es":"Abrir la última carpeta", "fr":"Ouvrir le dernier dossier"},

    # ---- Ansicht ----
    "act_meta_toggle": {"de":"Metadaten anzeigen", "en":"Show metadata", "es":"Mostrar metadatos", "fr":"Afficher les métadonnées"},
    "act_start_full":  {"de":"Im Vollbild starten", "en":"Start in fullscreen", "es":"Iniciar en pantalla completa", "fr":"Démarrer en plein écran"},
    "act_full_toggle": {"de":"Vollbild umschalten", "en":"Toggle fullscreen", "es":"Alternar pantalla completa", "fr":"Basculer en plein écran"},

    # ---- Sortieren ----
    "sort_name":   {"de":"🔤\u00A0 Dateiname", "en":"🔤\u00A0 Filename", "es":"🔤\u00A0 Nombre de archivo", "fr":"🔤\u00A0 Nom de fichier"},
    "sort_taken":  {"de":"📷\u00A0 Aufnahmedatum", "en":"📷\u00A0 Taken date", "es":"📷\u00A0 Fecha de toma", "fr":"📷\u00A0 Date de prise de vue"},
    "sort_ext":    {"de":"📂\u00A0 Dateityp", "en":"📂\u00A0 File type", "es":"📂\u00A0 Tipo de archivo", "fr":"📂\u00A0 Type de fichier"},
    "sort_ctime":  {"de":"⏱️\u00A0 Erstellungsdatum", "en":"⏱️\u00A0 Creation date", "es":"⏱️\u00A0 Fecha de creación", "fr":"⏱️\u00A0 Date de création"},
    "sort_mtime":  {"de":"✏️\u00A0 Änderungsdatum", "en":"✏️\u00A0 Modification date", "es":"✏️\u00A0 Fecha de modificación", "fr":"✏️\u00A0 Date de modification"},
    "sort_camera": {"de":"📸\u00A0 Kamera (EXIF)", "en":"📸\u00A0 Camera (EXIF)", "es":"📸\u00A0 Cámara (EXIF)", "fr":"📸\u00A0 Appareil (EXIF)"},
    "sort_lens":   {"de":"🔭\u00A0 Objektiv (EXIF)", "en":"🔭\u00A0 Lens (EXIF)", "es":"🔭\u00A0 Objetivo (EXIF)", "fr":"🔭\u00A0 Objectif (EXIF)"},
    "sort_desc":   {"de":"⇅\u00A0 Absteigend sortieren", "en":"⇅\u00A0 Sort descending", "es":"⇅\u00A0 Orden descendente", "fr":"⇅\u00A0 Trier par ordre décroissant"},

    # ---- Peek ----
    "peek_100": {"de":"100 %", "en":"100 %", "es":"100 %", "fr":"100 %"},
    "peek_200": {"de":"200 %", "en":"200 %", "es":"200 %", "fr":"200 %"},
    "peek_300": {"de":"300 %", "en":"300 %", "es":"300 %", "fr":"300 %"},
    "peek_400": {"de":"400 %", "en":"400 %", "es":"400 %", "fr":"400 %"},

    # ---- Slideshow ----
    "slide_startstop": {"de":"Start/Stop (Leertaste)", "en":"Start/Stop (Space)", "es":"Iniciar/Detener (Espacio)", "fr":"Démarrer/Arrêter (Espace)"},
    "slide_custom":    {"de":"Benutzerdefiniertes Intervall…", "en":"Custom interval…", "es":"Intervalo personalizado…", "fr":"Intervalle personnalisé…"},
    "slide_repeat":    {"de":"Am Ende wiederholen", "en":"Repeat at end", "es":"Repetir al final", "fr":"Répéter à la fin"},

    # ---- Optionen ----
    "opt_esc_quit": {"de":"Mit ESC beenden", "en":"Quit on ESC", "es":"Salir con ESC", "fr":"Quitter avec Échap"},
    "opt_x_trash":  {"de":"X = In Papierkorb verschieben", "en":"X = Move to Trash", "es":"X = Mover a la papelera", "fr":"X = Mettre à la corbeille"},
    "opt_x_folder": {"de":"X = In 'abgewählt' verschieben", "en":"X = Move to 'rejected'", "es":"X = Mover a 'descartado'", "fr":"X = Déplacer vers 'rejeté'"},
    "opt_lang_de":  {"de":"Deutsch", "en":"German", "es":"Alemán", "fr":"Allemand"},
    "opt_lang_en":  {"de":"Englisch", "en":"English", "es":"Inglés", "fr":"Anglais"},
    "opt_lang_es":  {"de":"Spanisch", "en":"Spanish", "es":"Español", "fr":"Espagnol"},
    "opt_lang_fr":  {"de":"Französisch", "en":"French", "es":"Francés", "fr":"Français"},

    # ---- Kontextmenü ----
    "ctx_open_image":  {"de":"Bild öffnen…", "en":"Open image…", "es":"Abrir imagen…", "fr":"Ouvrir une image…"},
    "ctx_open_folder": {"de":"Ordner öffnen…", "en":"Open folder…", "es":"Abrir carpeta…", "fr":"Ouvrir un dossier…"},
    "ctx_meta":        {"de":"Metadaten anzeigen (I)", "en":"Show metadata (I)", "es":"Mostrar metadatos (I)", "fr":"Afficher les métadonnées (I)"},
    "ctx_slide":       {"de":"Slideshow Start/Stop (Leertaste)", "en":"Slideshow Start/Stop (Space)", "es":"Diapositivas Iniciar/Detener (Espacio)", "fr":"Diaporama Démarrer/Arrêter (Espace)"},
    "ctx_x_menu":      {"de":"Aktion für Taste X", "en":"Action for key X", "es":"Acción para tecla X", "fr":"Action pour la touche X"},
    "ctx_x_trash":     {"de":"In Papierkorb verschieben", "en":"Move to Trash", "es":"Mover a la papelera", "fr":"Mettre à la corbeille"},
    "ctx_x_folder":    {"de":"In 'abgewählt' verschieben", "en":"Move to 'rejected'", "es":"Mover a 'descartado'", "fr":"Déplacer vers 'rejeté'"},
    "ctx_fullscreen":  {"de":"Vollbild umschalten \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 F", "en":"Toggle fullscreen \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 F", "es":"Alternar pantalla completa \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 F", "fr":"Basculer en plein écran \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 F"},

    # ---- Hilfe ----
    "help_title": {"de":"Hilfe", "en":"Help", "es":"Ayuda", "fr":"Aide"},
    "help_action": {"de":"Kurzanleitung & Shortcuts (H)", "en":"Quick guide & shortcuts (H)", "es":"Guía rápida y atajos (H)", "fr":"Guide rapide & raccourcis (H)"},
    "about_action": {
        "de": "Über FixPeek…",
        "en": "About FixPeek…",
        "es": "Acerca de FixPeek…",
        "fr": "À propos de FixPeek…"
    },
    "about_title": {
        "de": "Über FixPeek",
        "en": "About FixPeek",
        "es": "Acerca de FixPeek",
        "fr": "À propos de FixPeek"
    },
    "about_text": {
        "de": "FixPeek ist ein schneller, schlanker Bildbetrachter auf Basis von Python und Qt (PySide6).\nFunktionen: Peek‑Zoom, Vollbild, Slideshow (0,1 s – 10 min), Metadaten‑Panel, RAW‑Unterstützung (optional) u. v. m.\n\nLizenz: GNU GPLv3\nAutor: Joerg Junghanns\nQuelle: GitHub (Open Source)",
        "en": "FixPeek is a fast, lightweight image viewer built with Python and Qt (PySide6).\nFeatures: peek‑zoom, fullscreen, slideshow (0.1 s – 10 min), metadata panel, optional RAW support, and more.\n\nLicense: GNU GPLv3\nAuthor: Joerg Junghanns\nSource: GitHub (Open Source)",
        "es": "FixPeek es un visor de imágenes rápido y ligero basado en Python y Qt (PySide6).\nFunciones: zoom instantáneo, pantalla completa, diapositivas (0,1 s – 10 min), panel de metadatos, compatibilidad RAW opcional, y más.\n\nLicencia: GNU GPLv3\nAutor: Joerg Junghanns\nFuente: GitHub (código abierto)",
        "fr": "FixPeek est une visionneuse d’images rapide et légère, réalisée avec Python et Qt (PySide6).\nFonctionnalités : zoom instantané, plein écran, diaporama (0,1 s – 10 min), panneau de métadonnées, prise en charge RAW (optionnelle), etc.\n\nLicence : GNU GPLv3\nAuteur : Joerg Junghanns\nSource : GitHub (open source)"
    },
    "help_text": {
        "de": "KURZANLEITUNG\n\nDatei/Ordner öffnen:\n  • Datei öffnen …  ⌘O (macOS) / Ctrl+O (Linux)\n  • Ordner öffnen … ⌘⇧O (macOS) / Ctrl+Shift+O (Linux)\n  • Drag & Drop: Dateien oder Ordner ins Fenster ziehen\n  • Zuletzt geöffneten Ordner öffnen: Datei-Menü\n\nNavigation:\n  • Mausrad/Trackpad: vorheriges/nächstes Bild (1 Bild pro Raster)\n  • ← / →  bzw. ↑ / ↓ : vorheriges / nächstes Bild\n  • Bild↑ / Bild↓ : vorheriges / nächstes Bild\n  • Pos1 / Ende : erstes / letztes Bild\n\nAnsicht & Vollbild:\n  • Vollbild umschalten: F  (oder mittlere Maustaste)\n  • Peek‑Zoom (Schnellzoom): Strg + Linksklick halten → zoomt auf gewählten Punkt,\n    Loslassen = zurück zur Fensteranpassung\n  • Peek‑Zoom‑Stufe: Ansicht → Peek‑Zoom → 100/200/300/400 %\n  • Metadaten-Leiste ein/aus: I  (Ansicht → Metadaten anzeigen)\n\nSlideshow:\n  • Start/Stop: Leertaste  (Ansicht → Slideshow)\n  • Intervall: vordefiniert (2/5/10/20 s) oder „Benutzerdefiniertes Intervall…“\n  • Bereich: 0,1 s bis 10 min\n  • Während Slideshow: ↑ schneller, ↓ langsamer\n  • + / − : Intervall anpassen (auch außerhalb der Slideshow)\n  • Maus über Bild pausiert die Slideshow, Maus raus → weiter\n  • Am Ende wiederholen: Ansicht → Slideshow → Option\n\nSortieren:\n  • Ansicht → Sortieren: Dateiname, Aufnahmedatum (EXIF), Dateityp, Erstellungs‑/\n    Änderungsdatum, Kamera (EXIF), Objektiv (EXIF); auf/absteigend\n\nAuswahl per Taste X:\n  • Optionen → „X = In Papierkorb“ oder „X = In ‚abgewählt‘ verschieben“\n  • Rechtsklick → „Aktion für Taste X“ – schnelle Umschaltung\n\nESC‑Beenden (optional):\n  • Optionen → „Mit ESC beenden“ (nur wenn bewusst gewünscht)\n\nHinweise:\n  • Bilder werden nicht über 100 % vergrößert (Qualität bleibt erhalten)\n  • RAW‑Unterstützung optional (rawpy/numpy); Orientierung (EXIF) wird beachtet\n",
        "en": "QUICK GUIDE\n\nOpen file/folder:\n  • Open image …  ⌘O (macOS) / Ctrl+O (Linux)\n  • Open folder … ⌘⇧O (macOS) / Ctrl+Shift+O (Linux)\n  • Drag & drop: files or folders into the window\n  • Open last folder: File menu\n\nNavigation:\n  • Mouse wheel/trackpad: previous/next image (1 per notch)\n  • ← / →  and ↑ / ↓ : previous / next image\n  • PageUp / PageDown : previous / next image\n  • Home / End : first / last image\n\nView & fullscreen:\n  • Toggle fullscreen: F  (or middle mouse button)\n  • Peek‑zoom: hold Ctrl + left click → zoom to point,\n    release = back to fit-to-window\n  • Peek‑zoom level: View → Peek‑Zoom → 100/200/300/400 %\n  • Show metadata: I  (View → Show metadata)\n\nSlideshow:\n  • Start/Stop: Space  (View → Slideshow)\n  • Interval: presets (2/5/10/20 s) or “Custom interval…”\n  • Range: 0.1 s to 10 min\n  • While running: ↑ faster, ↓ slower\n  • + / − : adjust interval (even when not running)\n  • Mouse over image pauses; leaving resumes\n  • Repeat at end: View → Slideshow → option\n\nSorting:\n  • View → Sort: filename, taken date (EXIF), file type, creation/\n    modification date, camera (EXIF), lens (EXIF); asc/desc\n\nKey X action:\n  • Options → “X = Move to Trash” or “X = Move to ‘rejected’”\n  • Right-click → “Action for key X” – quick toggle\n\nESC quit (optional):\n  • Options → “Quit on ESC” (only if you really want that)\n\nNotes:\n  • Images are never enlarged beyond 100% (keeps quality)\n  • RAW support optional (rawpy/numpy); orientation (EXIF) respected\n",
        "es": "GUÍA RÁPIDA\n\nAbrir archivo/carpeta:\n  • Abrir imagen …  ⌘O (macOS) / Ctrl+O (Linux)\n  • Abrir carpeta … ⌘⇧O (macOS) / Ctrl+Shift+O (Linux)\n  • Arrastrar y soltar: archivos o carpetas en la ventana\n  • Abrir última carpeta: menú Archivo\n\nNavegación:\n  • Rueda del ratón/trackpad: imagen anterior/siguiente (1 por paso)\n  • ← / →  y ↑ / ↓ : imagen anterior / siguiente\n  • Re Pág / Av Pág : imagen anterior / siguiente\n  • Inicio / Fin : primera / última imagen\n\nVista y pantalla completa:\n  • Alternar pantalla completa: F  (o botón central del ratón)\n  • Zoom instantáneo: mantener Ctrl + clic izquierdo → zoom al punto,\n    soltar = ajustar a ventana\n  • Nivel de zoom: Ver → Zoom instantáneo → 100/200/300/400 %\n  • Mostrar metadatos: I  (Ver → Mostrar metadatos)\n\nDiapositivas:\n  • Iniciar/Detener: Espacio  (Ver → Diapositivas)\n  • Intervalo: predefinidos (2/5/10/20 s) o “Intervalo personalizado…”\n  • Rango: 0,1 s a 10 min\n  • En marcha: ↑ más rápido, ↓ más lento\n  • + / − : ajustar intervalo (también fuera de la reproducción)\n  • Ratón sobre la imagen pausa; al salir continúa\n  • Repetir al final: Ver → Diapositivas → opción\n\nOrdenación:\n  • Ver → Ordenar: nombre, fecha de toma (EXIF), tipo, fecha de creación/\n    modificación, cámara (EXIF), objetivo (EXIF); asc/desc\n\nAcción con la tecla X:\n  • Opciones → “X = Mover a la papelera” o “X = Mover a ‘descartado’”\n  • Clic derecho → “Acción para tecla X” – cambio rápido\n\nSalir con ESC (opcional):\n  • Opciones → “Salir con ESC” (solo si realmente lo deseas)\n\nNotas:\n  • Las imágenes no se amplían por encima del 100% (mantiene calidad)\n  • RAW opcional (rawpy/numpy); se respeta la orientación (EXIF)\n",
        "fr": "GUIDE RAPIDE\n\nOuvrir fichier/dossier :\n  • Ouvrir une image …  ⌘O (macOS) / Ctrl+O (Linux)\n  • Ouvrir un dossier … ⌘⇧O (macOS) / Ctrl+Shift+O (Linux)\n  • Glisser-déposer : fichiers ou dossiers dans la fenêtre\n  • Ouvrir le dernier dossier : menu Fichier\n\nNavigation :\n  • Molette/pavé tactile : image précédente/suivante (1 par cran)\n  • ← / →  et ↑ / ↓ : image précédente / suivante\n  • Page préc. / Page suiv. : image précédente / suivante\n  • Début / Fin : première / dernière image\n\nAffichage & plein écran :\n  • Basculer en plein écran : F  (ou bouton central)\n  • Zoom instantané : maintenir Ctrl + clic gauche → zoom sur le point,\n    relâcher = ajuster à la fenêtre\n  • Niveau de zoom : Affichage → Zoom instantané → 100/200/300/400 %\n  • Afficher les métadonnées : I  (Affichage → Afficher les métadonnées)\n\nDiaporama :\n  • Démarrer/Arrêter : Espace  (Affichage → Diaporama)\n  • Intervalle : préréglages (2/5/10/20 s) ou « Intervalle personnalisé… »\n  • Plage : 0,1 s à 10 min\n  • En cours : ↑ plus rapide, ↓ plus lent\n  • + / − : ajuster l’intervalle (même à l’arrêt)\n  • Souris sur l’image = pause ; en sortir = reprise\n  • Répéter à la fin : Affichage → Diaporama → option\n\nTri :\n  • Affichage → Trier : nom, date de prise (EXIF), type de fichier, date de création/\n    modification, appareil (EXIF), objectif (EXIF) ; croissant/décroissant\n\nAction touche X :\n  • Options → « X = Mettre à la corbeille » ou « X = Déplacer vers ‘rejeté’ »\n  • Clic droit → « Action pour la touche X » – bascule rapide\n\nÉchap pour quitter (optionnel) :\n  • Options → « Quitter avec Échap » (si vraiment souhaité)\n\nNotes :\n  • Les images ne sont jamais agrandies au-delà de 100% (qualité préservée)\n  • RAW optionnel (rawpy/numpy) ; orientation (EXIF) respectée\n"
    },
}
def tr(key: str, lang: str) -> str:
    m = TR.get(key, {})
    return m.get(lang, m.get("en", key))

# ===== Sortiermodi =====
SORT_NAME   = 0
SORT_TAKEN  = 1  # Aufnahmedatum (EXIF DateTimeOriginal)
SORT_EXT    = 2  # Dateityp
SORT_CTIME  = 3  # Erstellungsdatum (FS, wenn vorhanden)
SORT_MTIME  = 4  # Änderungsdatum
SORT_CAMERA = 5  # EXIF Kamera/Model
SORT_LENS   = 6  # EXIF Objektiv/LensModel


def build_file_filter(include_raw: bool) -> str:
    """Case-insensitiver Filter, z. B. *.[Jj][Pp][Gg] statt nur *.jpg."""
    def ci_glob(ext: str) -> str:
        parts = []
        for ch in ext[1:]:
            parts.append(f"[{ch.lower()}{ch.upper()}]" if ch.isalpha() else ch)
        return "*." + "".join(parts)
    exts = set(SUPPORTED)
    if include_raw:
        exts |= RAW_EXTS
    patterns = [ci_glob(e) for e in sorted(exts)]
    return f"Bilder ({' '.join(patterns)});;Alle Dateien (*)"


def load_qpixmap_any(path: str) -> QPixmap:
    """Lädt Bild als QPixmap und wendet EXIF-Orientation an (für ALLE Formate inkl. RAW)."""
    ext = os.path.splitext(path)[1].lower()

    # A) Normale Formate über Pillow laden + EXIF automatisch anwenden
    if ext in SUPPORTED or not RAW_AVAILABLE or ext not in RAW_EXTS:
        try:
            with Image.open(path) as pil:
                # Pillow macht die EXIF-Drehung korrekt:
                pil = ImageOps.exif_transpose(pil)  # dreht/spiegelt gemäß Orientation
                pil = pil.convert("RGBA")
                data = pil.tobytes("raw", "RGBA")
                qimg = QImage(data, pil.width, pil.height, QImage.Format_RGBA8888)
                return QPixmap.fromImage(qimg)
        except Exception:
            # Fallback auf Qt-Loader (evtl. ohne EXIF-Drehung)
            pm = QPixmap(path)
            # Als Sicherheitsnetz trotzdem EXIF prüfen (falls Pillow scheiterte):
            ori = get_exif_orientation(path)
            return apply_orientation_qpixmap(pm, ori)

    # B) RAW: mit rawpy laden, DANN EXIF-Orientation (exifread) anwenden
    pm = QPixmap()
    if RAW_AVAILABLE and ext in RAW_EXTS:
        try:
            with rawpy.imread(path) as raw:
                # 1) eingebettetes Thumbnail bevorzugen
                try:
                    thumb = raw.extract_thumb()
                    if thumb.format == rawpy.ThumbFormat.JPEG:
                        pm.loadFromData(thumb.data)
                    elif thumb.format == rawpy.ThumbFormat.BITMAP:
                        rgb = thumb.data  # (h,w,3)
                        h, w = rgb.shape[:2]
                        qimg = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888).copy()
                        pm = QPixmap.fromImage(qimg)
                except Exception:
                    pass
                # 2) Fallback: schnelle Entwicklung
                if pm.isNull():
                    rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8, gamma=(2.2, 4.5))
                    h, w = rgb.shape[:2]
                    qimg = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888).copy()
                    pm = QPixmap.fromImage(qimg)
        except Exception:
            pm = QPixmap(path)  # letzter Fallback

    # C) EXIF-Orientation (aus Datei) auf Pixmap anwenden
    ori = get_exif_orientation(path)
    pm = apply_orientation_qpixmap(pm, ori)
    return pm
    
def get_exif_orientation(path: str) -> int:
    """Liest EXIF-Orientation (1..8). Versteht auch Textwerte wie 'Rotated 90 CW'."""
    if EXIFREAD_AVAILABLE:
        try:
            # Nur bis Orientation lesen = schneller
            with open(path, "rb") as f:
                tags = exifread.process_file(f, details=False, stop_tag="Orientation")
            val = tags.get("Image Orientation") or tags.get("EXIF Orientation")
            if not val:
                return 1

            # 1) Versuch: direkte Zahl 1..8
            s = str(val).strip()
            try:
                n = int(s)
                if 1 <= n <= 8:
                    return n
            except Exception:
                pass

            # 2) Text-Mapping (kameratypische Ausgaben)
            sl = s.lower()
            mapping = {
                "horizontal": 1,
                "normal": 1,

                "mirror horizontal": 2,
                "mirrored horizontal": 2,

                "rotate 180": 3,
                "upside-down": 3,

                "mirror vertical": 4,
                "mirrored vertical": 4,

                "transpose": 5,  # H-Flip + 90° CCW
                "mirror horizontal and rotate 270 cw": 5,

                "rotate 90 cw": 6,
                "right-top": 6,

                "transverse": 7,  # H-Flip + 90° CW
                "mirror horizontal and rotate 90 cw": 7,

                "rotate 90 ccw": 8,
                "left-top": 8,
                "rotate 270 cw": 8,  # synonym
            }
            for key, num in mapping.items():
                if key in sl:
                    return num

            # 3) Grobe Heuristik (zur Sicherheit)
            if "180" in sl:
                return 3
            if "90" in sl and "cw" in sl:
                return 6
            if "90" in sl and ("ccw" in sl or "counter" in sl):
                return 8
        except Exception:
            pass
    return 1


def apply_orientation_qpixmap(pm: QPixmap, orientation: int) -> QPixmap:
    """Dreht/Spiegelt den Pixmap gemäß EXIF-Orientation."""
    if pm.isNull() or orientation == 1:
        return pm
    img = pm.toImage()

    # Orientierungscodes:
    # 1 = normal, 2 = H-Flip, 3 = 180°, 4 = V-Flip
    # 5 = Transpose (H-Flip + 90° CCW), 6 = 90° CW, 7 = Transverse (H-Flip + 90° CW), 8 = 90° CCW
    if orientation == 2:
        img = img.mirrored(True, False)
    elif orientation == 3:
        img = img.transformed(QTransform().rotate(180), Qt.SmoothTransformation)
    elif orientation == 4:
        img = img.mirrored(False, True)
    elif orientation == 5:
        img = img.transformed(QTransform().rotate(90), Qt.SmoothTransformation).mirrored(True, False)
    elif orientation == 6:
        img = img.transformed(QTransform().rotate(-90), Qt.SmoothTransformation)  # 90° CW
    elif orientation == 7:
        img = img.transformed(QTransform().rotate(-90), Qt.SmoothTransformation).mirrored(True, False)
    elif orientation == 8:
        img = img.transformed(QTransform().rotate(90), Qt.SmoothTransformation)   # 90° CCW

    return QPixmap.fromImage(img)

class Viewer(QMainWindow):
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    p = url.toLocalFile()
                    if os.path.isdir(p):
                        event.acceptProposedAction()
                        return
                    ext = os.path.splitext(p)[1].lower()
                    if ext in SUPPORTED or (RAW_AVAILABLE and ext in RAW_EXTS):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore(); return
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if not paths:
            event.ignore(); return

        # Bevorzugt: Ordner; sonst erste Datei
        first = paths[0]
        if os.path.isdir(first):
            self.last_folder = first
            self.settings.setValue("last_folder", self.last_folder)
            self._update_open_last_enabled()
            self._scan_folder_and_sort(first, None)
            if self.files:
                self.load_current()
            else:
                QMessageBox.information(self, "Hinweis", "Keine unterstützten Bilder im Ordner.")
            event.acceptProposedAction(); return

        # Datei(en): in deren Ordner öffnen und die erste Datei selektieren
        folder = os.path.dirname(first)
        filename = os.path.basename(first)
        self.last_folder = folder
        self.settings.setValue("last_folder", self.last_folder)
        self._update_open_last_enabled()
        self._scan_folder_and_sort(folder, filename)
        self.load_current()
        event.acceptProposedAction()

    def _update_open_last_enabled(self):
        # Enable/disable the 'open last folder' menu action if present
        try:
            # Find the action by text label inside the Datei menu
            for menu in self.menuBar().findChildren(QMenu):
                if menu.title() == "Datei":
                    for act in menu.actions():
                        if act.text() == "Zuletzt geöffneten Ordner öffnen":
                            act.setEnabled(bool(self.last_folder and os.path.isdir(self.last_folder)))
                            return
        except Exception:
            pass
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 600)

        # --- Settings zuerst laden ---
        self.settings         = QSettings(APP_NAME, APP_NAME)
        self.esc_quit_enabled = self.settings.value("esc_quit_enabled", False, type=bool)
        self.delete_mode      = self.settings.value("delete_mode", 1, type=int)  # 1=Papierkorb, 2=abgewählt
        self.sort_mode        = self.settings.value("sort_mode", SORT_NAME, type=int)
        self.sort_desc        = self.settings.value("sort_desc", False, type=bool)
        self.menubar_visible  = self.settings.value("menubar_visible", True, type=bool)
        self.start_fullscreen = self.settings.value("start_fullscreen", False, type=bool)
        self.last_folder     = self.settings.value("last_folder", "", type=str)

        # Sprache / Language laden
        self.lang = self.settings.value("lang", "de", type=str)
        if self.lang not in SUPPORTED_LANGS:
            self.lang = "de"

        # ---- Slideshow & Metadaten-Panel (früh initialisieren) ----
        self.slideshow_running     = False
        self.slideshow_interval_ms = self.settings.value("slideshow_interval_ms", 3000, type=int)
        self.slideshow_repeat      = self.settings.value("slideshow_repeat", True, type=bool)
        self.meta_visible          = self.settings.value("meta_visible", False, type=bool)

        # --- UI: Bildanzeige zentriert ---
        self.label = QLabel(alignment=Qt.AlignCenter)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(self.scroll)

        # Ensure the main window receives key events (not the scroll/label widgets)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.scroll.setFocusPolicy(Qt.NoFocus)
        self.label.setFocusPolicy(Qt.NoFocus)
        
        # --- Metadaten-Panel (rechts als Dock) ---
        self.meta_view = QTextEdit(self)
        self.meta_view.setReadOnly(True)
        self.meta_view.setMinimumWidth(260)
        self.meta_dock = QDockWidget("Metadaten", self)
        self.meta_dock.setObjectName("dock_meta")
        self.meta_dock.setWidget(self.meta_view)
        self.addDockWidget(Qt.RightDockWidgetArea, self.meta_dock)
        self.meta_dock.setVisible(self.meta_visible)

        # Overlay für kurze Hinweise (Intervall, Pause, usw.)
        self.overlay = QLabel("", self.scroll.viewport())
        self.overlay.setStyleSheet("QLabel { background: rgba(0,0,0,160); color: white; padding: 6px 10px; border-radius: 6px; }")
        self.overlay.setVisible(False)
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.overlay.move(10, 10)

        # Drag & Drop aktivieren
        self.setAcceptDrops(True)
        self.scroll.setAcceptDrops(True)
        self.label.setAcceptDrops(True)

        # Debounce for wheel events: ensure only one image step per user notch
        self._wheel_locked = False
        self._wheel_debounce_ms = 140
        self._wheel_timer = QTimer(self)
        self._wheel_timer.setSingleShot(True)
        self._wheel_timer.timeout.connect(self._unlock_wheel)

        # Events + Kontextmenü
        self.scroll.viewport().installEventFilter(self)
        self.label.installEventFilter(self)
        # Globaler Event-Filter: auch am Fenster und für die ganze App lauschen
        self.installEventFilter(self)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self.scroll.viewport().setContextMenuPolicy(Qt.CustomContextMenu)
        self.scroll.viewport().customContextMenuRequested.connect(self._show_context_menu_at_viewport)
        self.label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label.customContextMenuRequested.connect(self._show_context_menu_at_label)

        # Daten/Status
        self.current_folder = None
        self.files = []
        self.index = -1
        self.scale = 1.0
        self.pix: QPixmap | None = None
        self.peek_zoom_active = False
        self.peek_zoom_factor = 1.0  # 100 %
        self._exif_cache = {}

        # Menüs/Aktionen
        self._make_actions()
        self._sc_open = QShortcut(QKeySequence.StandardKey.Open, self)
        self._sc_open.activated.connect(self.open_file)

        self._sc_open_folder = QShortcut(QKeySequence("Meta+Shift+O"), self)
        self._sc_open_folder.activated.connect(self.open_folder)

        # Shortcut: Metadaten-Panel umschalten (Taste I)
        self._sc_meta = QShortcut(QKeySequence("I"), self)
        self._sc_meta.setContext(Qt.ApplicationShortcut)
        self._sc_meta.activated.connect(lambda: self.act_toggle_meta.toggle())

        # Shortcut: Hilfe
        self._sc_help = QShortcut(QKeySequence("H"), self)
        self._sc_help.setContext(Qt.ApplicationShortcut)
        self._sc_help.activated.connect(self._show_help)

        # Slideshow Timer
        self.slideshow_timer = QTimer(self)
        self.slideshow_timer.setInterval(self.slideshow_interval_ms)
        self.slideshow_timer.timeout.connect(self._slideshow_step)
        # Slideshow: Maus-Pause
        self._slideshow_mouse_pause = False

        # Startzustand anwenden
        self.menuBar().setVisible(self.menubar_visible)
        if self.start_fullscreen:
            self.toggle_fullscreen()

        self.resize(1000, 700)

    # ===================== Menüs / Aktionen =====================
    def _make_actions(self):
        # Clear existing menubar (when re-translating)
        mb = self.menuBar()
        mb.clear()

        # --- Datei / File ---
        m_file = mb.addMenu(tr("menu_file", self.lang))
        self.act_open_file   = QAction(tr("act_open_file", self.lang), self, triggered=self.open_file)
        self.act_open_folder = QAction(tr("act_open_folder", self.lang), self, triggered=self.open_folder)
        self.act_open_last   = QAction(tr("act_open_last", self.lang), self, triggered=self.open_last_folder)
        self.act_open_last.setEnabled(bool(self.last_folder and os.path.isdir(self.last_folder)))
        m_file.addAction(self.act_open_file)
        m_file.addAction(self.act_open_folder)
        m_file.addAction(self.act_open_last)

        # --- Ansicht / View ---
        m_view = mb.addMenu(tr("menu_view", self.lang))

        # Metadaten-Panel anzeigen
        self.act_toggle_meta = QAction(tr("act_meta_toggle", self.lang), self, checkable=True)
        self.act_toggle_meta.setChecked(getattr(self, "meta_dock", None) and self.meta_dock.isVisible())
        self.act_toggle_meta.toggled.connect(self._set_meta_visible)
        m_view.addAction(self.act_toggle_meta)

        # Im Vollbild starten (persistiert)
        self.act_start_fullscreen = QAction(tr("act_start_full", self.lang), self, checkable=True)
        self.act_start_fullscreen.setChecked(self.start_fullscreen)
        self.act_start_fullscreen.toggled.connect(self._set_start_fullscreen)
        m_view.addAction(self.act_start_fullscreen)

        # Manuell Vollbild umschalten
        self.act_fullscreen = QAction(tr("act_full_toggle", self.lang), self, triggered=self.toggle_fullscreen)
        self.act_fullscreen.setShortcut(QKeySequence("F"))
        m_view.addAction(self.act_fullscreen)

        # ---- Sortieren ----
        sort_menu = m_view.addMenu(tr("menu_sort", self.lang))
        self._sort_group = QActionGroup(self); self._sort_group.setExclusive(True)

        def _add_sort_action(key, mode):
            act = QAction(tr(key, self.lang), self, checkable=True)
            act.setChecked(self.sort_mode == mode)
            act.triggered.connect(lambda _=False, m=mode: self._set_sort_mode(m))
            self._sort_group.addAction(act); sort_menu.addAction(act)

        _add_sort_action("sort_name", SORT_NAME)
        _add_sort_action("sort_taken", SORT_TAKEN)
        _add_sort_action("sort_ext",   SORT_EXT)
        _add_sort_action("sort_ctime", SORT_CTIME)
        _add_sort_action("sort_mtime", SORT_MTIME)
        _add_sort_action("sort_camera", SORT_CAMERA)
        _add_sort_action("sort_lens",   SORT_LENS)

        sort_menu.addSeparator()
        self._sort_desc_action = QAction(tr("sort_desc", self.lang), self, checkable=True)
        self._sort_desc_action.setChecked(self.sort_desc)
        self._sort_desc_action.toggled.connect(self._set_sort_desc)
        sort_menu.addAction(self._sort_desc_action)

        # ---- Peek-Zoom ----
        peek_menu = m_view.addMenu(tr("menu_peek", self.lang))
        self._peek_group = QActionGroup(self); self._peek_group.setExclusive(True)
        for key, factor in [("peek_100", 1.0), ("peek_200", 2.0), ("peek_300", 3.0), ("peek_400", 4.0)]:
            act = QAction(tr(key, self.lang), self, checkable=True)
            act.setData(factor)
            act.setChecked(abs(self.peek_zoom_factor - factor) < 1e-9)
            act.triggered.connect(lambda _, f=factor: self._set_peek_zoom_factor(f))
            self._peek_group.addAction(act); peek_menu.addAction(act)

        # ---- Slideshow submenu ----
        slide_menu = m_view.addMenu(tr("menu_slideshow", self.lang))
        self._slide_group = QActionGroup(self); self._slide_group.setExclusive(True)
        for label, ms in [( "2 s", 2000), ("5 s", 5000), ("10 s", 10000), ("20 s", 20000)]:
            act = QAction(label, self, checkable=True)
            act.setChecked(self.slideshow_interval_ms == ms)
            act.triggered.connect(lambda _, m=ms: self._set_slideshow_interval(m))
            self._slide_group.addAction(act); slide_menu.addAction(act)
        slide_menu.addSeparator()
        act_custom = QAction(tr("slide_custom", self.lang), self, triggered=self._ask_slideshow_interval)
        slide_menu.addAction(act_custom)
        self.act_slide_toggle = QAction(tr("slide_startstop", self.lang), self, triggered=self.toggle_slideshow)
        slide_menu.addAction(self.act_slide_toggle)
        self.act_slide_repeat = QAction(tr("slide_repeat", self.lang), self, checkable=True)
        self.act_slide_repeat.setChecked(self.slideshow_repeat)
        self.act_slide_repeat.toggled.connect(self._set_slideshow_repeat)
        slide_menu.addAction(self.act_slide_repeat)

        # --- Optionen / Options ---
        m_opts = mb.addMenu(tr("menu_options", self.lang))
        esc_quit = QAction(tr("opt_esc_quit", self.lang), self, checkable=True)
        esc_quit.setChecked(self.esc_quit_enabled)
        esc_quit.toggled.connect(self._set_esc_quit)
        m_opts.addAction(esc_quit)

        self.opt_trash  = QAction(tr("opt_x_trash", self.lang), self, checkable=True)
        self.opt_folder = QAction(tr("opt_x_folder", self.lang), self, checkable=True)
        self.opt_trash.setChecked(self.delete_mode == 1)
        self.opt_folder.setChecked(self.delete_mode == 2)
        self.opt_trash.triggered.connect(lambda: self.set_delete_mode(1))
        self.opt_folder.triggered.connect(lambda: self.set_delete_mode(2))
        m_opts.addSeparator(); m_opts.addActions([self.opt_trash, self.opt_folder])

        # Sprache / Language submenu
        lang_menu = m_opts.addMenu(tr("menu_language", self.lang))
        self._lang_group = QActionGroup(self); self._lang_group.setExclusive(True)
        for code, key in [("de","opt_lang_de"), ("en","opt_lang_en"), ("es","opt_lang_es"), ("fr","opt_lang_fr")]:
            act = QAction(tr(key, self.lang), self, checkable=True)
            act.setChecked(self.lang == code)
            act.triggered.connect(functools.partial(self._set_language, code))
            self._lang_group.addAction(act); lang_menu.addAction(act)

        # --- Hilfe / Help ---
        m_help = mb.addMenu(tr("menu_help", self.lang))
        help_act = QAction(tr("help_action", self.lang), self, triggered=self._show_help)
        m_help.addAction(help_act)
        about_act = QAction(tr("about_action", self.lang), self, triggered=self._show_about)
        m_help.addAction(about_act)

        # Shortcuts auch ohne Menüklick nutzbar
        self.addAction(self.act_fullscreen)

    def _set_language(self, code: str):
        if code not in SUPPORTED_LANGS:
            return
        if code == self.lang:
            return
        self.lang = code
        self.settings.setValue("lang", self.lang)
        # Rebuild all menus/texts
        self._make_actions()

    def _t_help(self) -> str:
        return tr("help_text", self.lang)
    def _show_help(self):
        QMessageBox.information(self, f"{APP_NAME} — {tr('help_title', self.lang)}", self._t_help())

    def _show_about(self):
        QMessageBox.information(
            self,
            tr("about_title", self.lang),
            tr("about_text", self.lang)
        )


    # ===================== Setter / Optionen =====================
    def _set_start_fullscreen(self, enabled: bool):
        self.start_fullscreen = bool(enabled)
        self.settings.setValue("start_fullscreen", self.start_fullscreen)

    def _set_esc_quit(self, enabled: bool):
        self.esc_quit_enabled = bool(enabled)
        self.settings.setValue("esc_quit_enabled", self.esc_quit_enabled)

    def _set_peek_zoom_factor(self, factor: float):
        self.peek_zoom_factor = float(factor)
        # optional Titel aktualisieren:
        self._update_window_title()

    # ===================== Datei/Ordner öffnen =====================
    def open_file(self):
        filter_str = build_file_filter(include_raw=RAW_AVAILABLE)
        path, _ = QFileDialog.getOpenFileName(self, "Bild öffnen", "", filter_str)
        if path:
            folder = os.path.dirname(path)
            filename = os.path.basename(path)
            self.last_folder = folder
            self.settings.setValue("last_folder", self.last_folder)
            self._update_open_last_enabled()
            self._scan_folder_and_sort(folder, filename)
            self.load_current()


    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Ordner öffnen", "")
        if folder:
            self.last_folder = folder
            self.settings.setValue("last_folder", self.last_folder)
            self._update_open_last_enabled()
            self._scan_folder_and_sort(folder, None)
            if not self.files:
                msg = "Keine unterstützten Bilder im Ordner."
                if not RAW_AVAILABLE:
                    msg += "\n(Hinweis: RAW-Unterstützung nicht installiert: pip install rawpy numpy)"
                QMessageBox.information(self, "Hinweis", msg)
                return
            self.load_current()

    def open_last_folder(self):
        folder = self.last_folder
        if not folder or not os.path.isdir(folder):
            QMessageBox.information(self, "Hinweis", "Es ist kein zuletzt geöffneter Ordner gespeichert.")
            return
        self._scan_folder_and_sort(folder, None)
        if not self.files:
            QMessageBox.information(self, "Hinweis", "Im zuletzt geöffneten Ordner wurden keine unterstützten Bilder gefunden.")
            return
        self.load_current()

    # ===================== Fenster-Titel =====================
    def _update_window_title(self):
        if self.index < 0 or self.index >= len(self.files):
            self.setWindowTitle(APP_NAME);  return
        filename = self.files[self.index]
        if self.isFullScreen():
            self.setWindowTitle(f"{filename} — {APP_NAME}")
        else:
            suffix = "🗑️ X=Papierkorb" if self.delete_mode == 1 else "📂 X=abgewählt"
            self.setWindowTitle(f"{filename}   {suffix} — {APP_NAME}")

    # ===================== Bildanzeige =====================
    def load_current(self):
        if self.index < 0 or self.index >= len(self.files):
            self.label.clear(); self._update_window_title(); return
        path = os.path.join(self.current_folder, self.files[self.index])
        pix = load_qpixmap_any(path)
        if pix.isNull():
            QMessageBox.warning(self, "Fehler", f"Konnte nicht laden:\n{path}")
            return
        self.pix = pix
        self.peek_zoom_active = False
        self.fit_to_window()
        self._update_window_title()

    def update_view(self):
        if not self.pix:
            return
        w = int(self.pix.width() * self.scale)
        h = int(self.pix.height() * self.scale)
        self.label.setPixmap(self.pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Label mind. so groß wie der Viewport -> echte Zentrierung
        min_w = max(w, self.scroll.viewport().width())
        min_h = max(h, self.scroll.viewport().height())
        self.label.resize(min_w, min_h)
        
    def fit_to_window(self):
        if not self.pix:
            return
        area = self.scroll.viewport().size()
        if self.pix.width() == 0 or self.pix.height() == 0 or area.width() == 0 or area.height() == 0:
            return
        fw = area.width() / self.pix.width()
        fh = area.height() / self.pix.height()
        candidate = min(fw, fh)
        # nur verkleinern, nie größer als 100 %
        self.scale = min(1.0, candidate)
        self.update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.peek_zoom_active:
            self.fit_to_window()

    # ===================== Navigation =====================
    def next_image(self):
        if not self.files:
            return
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load_current()

    def prev_image(self):
        if not self.files:
            return
        if self.index > 0:
            self.index -= 1
            self.load_current()
    
    # ===================== Sortieren =====================
    def _read_exif_cached(self, path: str):
        """Liest EXIF einmalig und cached: (taken_ts, camera_str, lens_str)."""
        if path in self._exif_cache:
            return self._exif_cache[path]
        taken_ts = None; camera = None; lens = None
        if EXIFREAD_AVAILABLE:
            try:
                with open(path, "rb") as f:
                    tags = exifread.process_file(f, details=False)
                # Aufnahmedatum
                for key in ("EXIF DateTimeOriginal", "EXIF DateTimeDigitized", "Image DateTime"):
                    if key in tags:
                        raw = str(tags[key]).split(".")[0]
                        try:
                            dt = datetime.datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
                            taken_ts = int(dt.timestamp()); break
                        except Exception:
                            pass
                # Kamera / Modell
                if "Image Model" in tags:
                    camera = str(tags.get("Image Model"))
                elif "Image Make" in tags:
                    camera = str(tags.get("Image Make"))
                # Objektiv
                for key in ("EXIF LensModel", "MakerNote LensType", "MakerNote Lens", "EXIF LensMake"):
                    if key in tags:
                        lens = str(tags[key]); break
            except Exception:
                pass
        info = (taken_ts, camera, lens)
        self._exif_cache[path] = info
        return info

    def _file_sort_key(self, folder: str, fname: str):
        """Sortierschlüssel für aktuelle self.sort_mode."""
        path = os.path.join(folder, fname)
        ext = os.path.splitext(fname)[1].lower()
        try:
            st = os.stat(path)
        except Exception:
            st = None

        if self.sort_mode == SORT_NAME:
            key = (fname.lower(),)
        elif self.sort_mode == SORT_TAKEN:
            taken_ts, _, _ = self._read_exif_cached(path)
            if taken_ts is None:
                taken_ts = st.st_mtime if st else 0
            key = (taken_ts, fname.lower())
        elif self.sort_mode == SORT_EXT:
            key = (ext, fname.lower())
        elif self.sort_mode == SORT_CTIME:
            if st:
                ctime = getattr(st, "st_birthtime", None)
                if ctime is None:
                    ctime = st.st_mtime
            else:
                ctime = 0
            key = (ctime, fname.lower())
        elif self.sort_mode == SORT_MTIME:
            mtime = st.st_mtime if st else 0
            key = (mtime, fname.lower())
        elif self.sort_mode == SORT_CAMERA:
            _, camera, _ = self._read_exif_cached(path)
            key = ((camera or "").lower(), fname.lower())
        elif self.sort_mode == SORT_LENS:
            _, _, lens = self._read_exif_cached(path)
            key = ((lens or "").lower(), fname.lower())
        else:
            key = (fname.lower(),)
        return key

    def _scan_folder_and_sort(self, folder: str, select_filename: str | None = None):
        allowed_exts = set(SUPPORTED) | (RAW_EXTS if RAW_AVAILABLE else set())
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in allowed_exts]
        files.sort(key=lambda f: self._file_sort_key(folder, f), reverse=self.sort_desc)

        self.current_folder = folder
        self.files = files
        if not self.files:
            self.index = -1
            return
        if select_filename and select_filename in self.files:
            self.index = self.files.index(select_filename)
        else:
            self.index = 0

    def _resort_keep_current(self):
        if not self.current_folder or not self.files or self.index < 0:
            return
        current = self.files[self.index]
        self._scan_folder_and_sort(self.current_folder, current)
        self.load_current()

    def _set_sort_mode(self, mode: int):
        self.sort_mode = int(mode)
        self.settings.setValue("sort_mode", self.sort_mode)
        self._resort_keep_current()

    def _set_sort_desc(self, enabled: bool):
        self.sort_desc = bool(enabled)
        self.settings.setValue("sort_desc", self.sort_desc)
        self._resort_keep_current()
        
    # ===================== Metadaten & Slideshow =====================
    def _set_meta_visible(self, enabled: bool):
        self.meta_visible = bool(enabled)
        self.meta_dock.setVisible(self.meta_visible)
        self.settings.setValue("meta_visible", self.meta_visible)
        if self.meta_visible:
            self._update_metadata()

    def _read_exif_full(self, path: str) -> dict:
        """Liest ausgewählte Metadaten mit exifread und liefert ein Dict."""
        data = {}
        if EXIFREAD_AVAILABLE:
            try:
                with open(path, "rb") as f:
                    tags = exifread.process_file(f, details=False)
                def g(k):
                    v = tags.get(k)
                    return str(v) if v is not None else None
                data["Aufnahmedatum"] = g("EXIF DateTimeOriginal") or g("EXIF DateTimeDigitized") or g("Image DateTime")
                data["Kamera"] = g("Image Model") or g("Image Make")
                data["Objektiv"] = g("EXIF LensModel") or g("MakerNote LensType") or g("MakerNote Lens") or g("EXIF LensMake")
                data["Belichtungszeit"] = g("EXIF ExposureTime")
                data["Blende"] = g("EXIF FNumber")
                data["ISO"] = g("EXIF ISOSpeedRatings") or g("EXIF PhotographicSensitivity")
                data["Brennweite"] = g("EXIF FocalLength")
            except Exception:
                pass
        return data

    def _update_metadata(self):
        """Aktualisiert die Metadatenanzeige im Dock."""
        if not getattr(self, "meta_dock", None) or not self.meta_dock.isVisible():
            return
        if self.index < 0 or self.index >= len(self.files):
            self.meta_view.clear(); return
        path = os.path.join(self.current_folder, self.files[self.index])
        lines = [os.path.basename(path)]
        # Größe aus dem geladenen Pixmap
        if self.pix:
            lines.append(f"{self.pix.width()} × {self.pix.height()} px")
        # EXIF
        info = self._read_exif_full(path)
        def add(key, label):
            v = info.get(key)
            if v:
                lines.append(f"{label}: {v}")
        add("Aufnahmedatum", "Aufgenommen")
        add("Kamera", "Kamera")
        add("Objektiv", "Objektiv")
        add("Belichtungszeit", "Zeit")
        add("Blende", "Blende")
        add("ISO", "ISO")
        add("Brennweite", "Brennweite")
        self.meta_view.setPlainText("\n".join(lines))

    def toggle_slideshow(self):
        if not self.files:
            return
        self.slideshow_running = not self.slideshow_running
        if self.slideshow_running:
            self.slideshow_timer.start(self.slideshow_interval_ms)
            rep = "⟳" if self.slideshow_repeat else "⤓"
            self._show_overlay(f"Slideshow • {self._format_interval_label()}  {rep}")
        else:
            self.slideshow_timer.stop()
            self._show_overlay("■ Stopp", 800)

    def _slideshow_step(self):
        if not self.files:
            self.slideshow_timer.stop(); self.slideshow_running = False; return
        if self.index < len(self.files) - 1:
            self.index += 1
            self.load_current()
        else:
            if self.slideshow_repeat:
                self.index = 0
                self.load_current()
            else:
                self.slideshow_timer.stop()
                self.slideshow_running = False

    def _set_slideshow_interval(self, ms: int):
        self.slideshow_interval_ms = int(ms)
        self.settings.setValue("slideshow_interval_ms", self.slideshow_interval_ms)
        self.slideshow_timer.setInterval(self.slideshow_interval_ms)

    def _ask_slideshow_interval(self):
        # Dialog: Sekunden (0,1 bis 600, in 0,1er Schritten)
        current_sec = max(0.1, min(600.0, self.slideshow_interval_ms / 1000.0))
        val, ok = QInputDialog.getDouble(
            self,
            "Slideshow-Intervall",
            "Sekunden (0,1 – 600):",
            current_sec,
            0.1, 600.0, 1  # min, max, 1 Dezimalstelle
        )
        if not ok:
            return
        self._set_slideshow_interval(int(round(val * 1000)))
        # Vordefinierte Radio-Buttons abwählen, da benutzerdefiniert
        try:
            for act in self._slide_group.actions():
                act.setChecked(False)
        except Exception:
            pass

    def _set_slideshow_repeat(self, enabled: bool):
        self.slideshow_repeat = bool(enabled)
        self.settings.setValue("slideshow_repeat", self.slideshow_repeat)

    def _format_interval_label(self) -> str:
        sec = self.slideshow_interval_ms / 1000.0
        if sec < 10:
            return f"{sec:0.1f} s"
        elif sec < 60:
            return f"{int(round(sec))} s"
        else:
            # ab 60 s in min anzeigen, ggf. Restsekunden
            m = int(sec // 60)
            s = int(round(sec % 60))
            if s == 0:
                return f"{m} min"
            return f"{m} min {s} s"

    def _show_overlay(self, text: str, msec: int = 1200):
        try:
            self.overlay.setText(text)
            self.overlay.adjustSize()
            # oben links lassen; optional könnte man es dynamisch positionieren
            self.overlay.setVisible(True)
            QTimer.singleShot(msec, lambda: self.overlay.setVisible(False))
        except Exception:
            pass

    def _adjust_slideshow_interval(self, delta_ms: int):
        new_ms = max(100, min(600000, self.slideshow_interval_ms + delta_ms))  # 0.1 s .. 10 min
        if new_ms == self.slideshow_interval_ms:
            return
        self._set_slideshow_interval(new_ms)
        if self.slideshow_running and not self._slideshow_mouse_pause:
            self.slideshow_timer.start(self.slideshow_interval_ms)
        rep = "⟳" if self.slideshow_repeat else "⤓"
        self._show_overlay(f"{self._format_interval_label()}  {rep}")

    def _slideshow_pause_by_mouse(self, paused: bool):
        if not self.slideshow_running:
            return
        if paused and not self._slideshow_mouse_pause:
            self._slideshow_mouse_pause = True
            self.slideshow_timer.stop()
            self._show_overlay("⏸︎ Pause")
        elif not paused and self._slideshow_mouse_pause:
            self._slideshow_mouse_pause = False
            self.slideshow_timer.start(self.slideshow_interval_ms)
            self._show_overlay("▶︎ Weiter")

    # ===================== Peek-Zoom Helpers =====================
    def _viewport_offsets(self):
        vp = self.scroll.viewport().size()
        disp_w = int(self.pix.width() * self.scale)
        disp_h = int(self.pix.height() * self.scale)
        off_x = max(0, (vp.width() - disp_w) // 2)
        off_y = max(0, (vp.height() - disp_h) // 2)
        return off_x, off_y, disp_w, disp_h, vp

    def _center_image_point_in_view(self, img_x, img_y):
        vp_w = self.scroll.viewport().width()
        vp_h = self.scroll.viewport().height()
        target_x = int(img_x * self.scale - vp_w / 2)
        target_y = int(img_y * self.scale - vp_h / 2)
        hbar = self.scroll.horizontalScrollBar()
        vbar = self.scroll.verticalScrollBar()
        hbar.setValue(max(0, min(target_x, hbar.maximum())))
        vbar.setValue(max(0, min(target_y, vbar.maximum())))

    def _enter_peek_zoom(self, vp_pos):
        if not self.pix:
            return
        off_x, off_y, disp_w, disp_h, _ = self._viewport_offsets()
        dx = max(0, min(vp_pos.x() - off_x, disp_w))
        dy = max(0, min(vp_pos.y() - off_y, disp_h))
        img_x = dx / self.scale
        img_y = dy / self.scale
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scale = self.peek_zoom_factor
        self.peek_zoom_active = True
        self.update_view()
        self._center_image_point_in_view(img_x, img_y)

    def _exit_peek_zoom(self):
        self.peek_zoom_active = False
        self.fit_to_window()
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _unlock_wheel(self):
        self._wheel_locked = False

    # ===================== Kontextmenü =====================
    def _show_context_menu(self, global_pos):
        menu = QMenu(self)
        # Datei öffnen
        menu.addAction(QAction(tr("ctx_open_image", self.lang), menu, triggered=self.open_file))
        menu.addAction(QAction(tr("ctx_open_folder", self.lang), menu, triggered=self.open_folder))

        # Metadaten-Panel Toggle
        act_meta = QAction(tr("ctx_meta", self.lang), menu, checkable=True)
        act_meta.setChecked(self.meta_dock.isVisible())
        act_meta.toggled.connect(self._set_meta_visible)
        menu.addAction(act_meta)

        # Slideshow schnell
        menu.addAction(QAction(tr("ctx_slide", self.lang), menu, triggered=self.toggle_slideshow))
        menu.addSeparator()

        # Peek-Zoom
        peek_menu = menu.addMenu(tr("menu_peek", self.lang))
        group = QActionGroup(peek_menu); group.setExclusive(True)
        for key, factor in [("peek_100", 1.0), ("peek_200", 2.0), ("peek_300", 3.0), ("peek_400", 4.0)]:
            act = QAction(tr(key, self.lang), peek_menu, checkable=True)
            act.setData(factor)
            act.setChecked(abs(self.peek_zoom_factor - factor) < 1e-9)
            act.triggered.connect(lambda _, f=factor: self._set_peek_zoom_factor(f))
            group.addAction(act); peek_menu.addAction(act)

        # ESC-Option
        esc_action = QAction(tr("opt_esc_quit", self.lang), menu, checkable=True)
        esc_action.setChecked(self.esc_quit_enabled)
        esc_action.toggled.connect(self._set_esc_quit)
        menu.addAction(esc_action)

        # X-Modus
        menu.addSeparator()
        x_menu = menu.addMenu(tr("menu_x_action", self.lang))
        opt1 = QAction(tr("ctx_x_trash", self.lang), self, checkable=True)
        opt2 = QAction(tr("ctx_x_folder", self.lang), self, checkable=True)
        opt1.setChecked(self.delete_mode == 1)
        opt2.setChecked(self.delete_mode == 2)
        opt1.triggered.connect(lambda: self.set_delete_mode(1))
        opt2.triggered.connect(lambda: self.set_delete_mode(2))
        x_menu.addAction(opt1); x_menu.addAction(opt2)

        menu.addSeparator()
        menu.addAction(QAction(tr("ctx_fullscreen", self.lang), menu, triggered=self.toggle_fullscreen))

        menu.exec(global_pos)

    def _show_context_menu_at_viewport(self, pos):
        self._show_context_menu(self.scroll.viewport().mapToGlobal(pos))

    def _show_context_menu_at_label(self, pos):
        self._show_context_menu(self.label.mapToGlobal(pos))

    # ===================== Tastatur & Events =====================
    def eventFilter(self, obj, event):
        # Globales Loslassen der linken Maustaste beendet Peek-Zoom – unabhängig vom Zielwidget
        if event.type() == QEvent.MouseButtonRelease and self.peek_zoom_active:
            # getattr: kompatibel mit verschiedenen Qt-Versionen
            if getattr(event, "button", None) == Qt.LeftButton:
                self._exit_peek_zoom()
                return True
        if obj in (self.scroll.viewport(), self.label):
            t = event.type()
            if t == QEvent.Enter:
                self._slideshow_pause_by_mouse(True)
                # Kein return, damit weitere Enter-Logik (falls vorhanden) laufen kann
            if t == QEvent.Leave:
                self._slideshow_pause_by_mouse(False)
                # Kein return, damit weitere Leave-Logik (falls vorhanden) laufen kann
            if t == QEvent.Wheel:
                # One image per wheel 'intent': debounce multiple high-resolution events
                if self._wheel_locked:
                    return True
                dy = event.angleDelta().y()
                if dy > 0:
                    self.prev_image()
                elif dy < 0:
                    self.next_image()
                self._wheel_locked = True
                self._wheel_timer.start(self._wheel_debounce_ms)
                return True
            if t == QEvent.MouseButtonPress:
                # Mittlere Maustaste -> Vollbild umschalten
                if event.button() == Qt.MiddleButton:
                    self.toggle_fullscreen()
                    return True
                # Strg + LMB -> Peek-Zoom
                if (event.button() == Qt.LeftButton) and (event.modifiers() & Qt.ControlModifier):
                    pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
                    self._enter_peek_zoom(pos)
                    return True
            if t == QEvent.MouseButtonRelease:
                if self.peek_zoom_active and event.button() == Qt.LeftButton:
                    self._exit_peek_zoom()
                    return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.esc_quit_enabled:
            QApplication.quit(); return
        if event.key() == Qt.Key_X:
            self._handle_x_action(); return
        # Slideshow: schneller/langsamer
        if self.slideshow_running:
            if event.key() == Qt.Key_Up:
                # schneller: kleinere Intervalle
                step = 100 if self.slideshow_interval_ms < 1000 else 1000
                self._adjust_slideshow_interval(-step); return
            if event.key() == Qt.Key_Down:
                step = 100 if self.slideshow_interval_ms < 1000 else 1000
                self._adjust_slideshow_interval(+step); return
        # +/- funktionieren immer, auch außerhalb der Slideshow
        if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
            step = 100 if self.slideshow_interval_ms < 1000 else 1000
            self._adjust_slideshow_interval(-step); return
        if event.key() in (Qt.Key_Minus, Qt.Key_Underscore):
            step = 100 if self.slideshow_interval_ms < 1000 else 1000
            self._adjust_slideshow_interval(+step); return
        if event.key() == Qt.Key_Right:
            self.next_image(); return
        if event.key() == Qt.Key_Left:
            self.prev_image(); return
        if event.key() == Qt.Key_Up:
            self.prev_image(); return
        if event.key() == Qt.Key_Down:
            self.next_image(); return
        if event.key() == Qt.Key_PageUp:
            self.prev_image(); return
        if event.key() == Qt.Key_PageDown:
            self.next_image(); return
        if event.key() == Qt.Key_Home:
            if self.files:
                self.index = 0
                self.load_current()
            return
        if event.key() == Qt.Key_End:
            if self.files:
                self.index = len(self.files) - 1
                self.load_current()
            return
        if event.key() == Qt.Key_F:
            self.toggle_fullscreen(); return
        if event.key() == Qt.Key_Space:
            self.toggle_slideshow(); return
        if event.key() == Qt.Key_I:
            if hasattr(self, "act_toggle_meta"):
                self.act_toggle_meta.toggle()
            return
        super().keyPressEvent(event)

    # ===================== X-Aktion (Papierkorb / abgewählt) =====================
    def set_delete_mode(self, mode: int):
        self.delete_mode = 1 if mode == 1 else 2
        self.settings.setValue("delete_mode", self.delete_mode)
        if hasattr(self, "opt_trash"):  self.opt_trash.setChecked(self.delete_mode == 1)
        if hasattr(self, "opt_folder"): self.opt_folder.setChecked(self.delete_mode == 2)
        self._update_window_title()
        if getattr(self, "meta_dock", None) and self.meta_dock.isVisible():
            self._update_metadata()
            
    def _handle_x_action(self):
        if self.current_folder is None or self.index < 0 or self.index >= len(self.files):
            return
        path = os.path.join(self.current_folder, self.files[self.index])
        try:
            if self.delete_mode == 1:
                send2trash(path)
            else:
                target_folder = os.path.join(self.current_folder, "abgewählt")
                os.makedirs(target_folder, exist_ok=True)
                shutil.move(path, os.path.join(target_folder, os.path.basename(path)))
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Aktion fehlgeschlagen:\n{e}")
            return

        self.files.pop(self.index)
        if not self.files:
            self.index = -1
            self.label.clear()
            self._update_window_title()
            return
        if self.index >= len(self.files):
            self.index = len(self.files) - 1
        self.load_current()

    # ===================== Vollbild =====================
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self._update_window_title()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Viewer()
    win.show()
    sys.exit(app.exec())
