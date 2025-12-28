# Images and Icons Directory

This folder contains static images and icons used in the application.

## How to Add Your Logo/Icon

1. **Save your logo/icon file here** with the name `logo.png` (or `logo.svg` if you prefer SVG)
   - Recommended size: 128x128px or 256x256px
   - Format: PNG with transparent background works best
   - For medical theme, consider using a stethoscope, medical cross, or skin lesion icon

2. **The header in `main.py` is already configured** to use the icon at:
   ```
   assets/images/logo.png
   ```

3. **If you want to use a different filename**, update line 133 in `main.py`:
   ```html
   <img src="app/static/images/YOUR_FILENAME.png" alt="Logo" style="...">
   ```

## Alternative: Use an Emoji Instead

If you prefer to keep using an emoji (current: 🩺), simply replace the `<img>` tag with the emoji:

```html
🩺 Skin Lesion AI Triage Tool
```

## Note on Streamlit File Serving

Streamlit serves static files from the `static` directory. The current path structure is:
- `app/static/images/logo.png`

If the image doesn't load, you may need to:
1. Create a `static/images/` folder at the root level
2. Move your logo there
3. Update the path to: `static/images/logo.png`
